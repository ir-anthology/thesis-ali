# Deployment Guide — Linux

Linux/bash counterpart of [`DEPLOYMENT.md`](./DEPLOYMENT.md). Same application,
image, namespace and manifest — only the shell pieces differ. `DEPLOYMENT.md`
uses PowerShell for the analytics-database workflow; everything below is the
bash equivalent.

Keep both files in sync when the deploy procedure changes.

- **Image:** `muhammadfarzadali/ir-anthology-chat-api:latest`
- **Namespace:** `webisstud`
- **Manifest:** `k8s.yaml` (ConfigMap, Deployment, PVC, Service, Ingress)
- **Workdir:** `sparql/option-4-rule-based-sparql-generation`

---

## 0. Prerequisites

| Tool | Check | If missing |
|---|---|---|
| kubectl | `kubectl version --client` | see [`docs/kubectl-webis-setup.md`](../../docs/kubectl-webis-setup.md) |
| cluster access | `kubectl get pods -n webisstud` | same doc; OIDC login + `webis` context |
| docker | `docker version` | `sudo apt install docker.io`, then `sudo usermod -aG docker $USER` (re-login) |
| Docker Hub auth | `docker login` | credentials for `muhammadfarzadali` |
| python3 | `python3 --version` | `sudo apt install python3` |
| sqlite3 (optional) | `sqlite3 --version` | `sudo apt install sqlite3` |

> **On this workstation docker is not installed yet** (`docker version` fails).
> Steps 1–2 need it; steps 3–6 do not.

If you are not in the `docker` group, prefix docker commands with `sudo`. Verify
with `docker ps` — a permission error means the group change has not taken
effect yet (log out and back in).

Working directory for every command below:

```bash
cd sparql/option-4-rule-based-sparql-generation
```

---

## 1. Quick Deploy (One-Liner)

Use when the application code or Docker image changed:

```bash
docker build -t muhammadfarzadali/ir-anthology-chat-api:latest . \
  && docker push muhammadfarzadali/ir-anthology-chat-api:latest \
  && kubectl apply -f k8s.yaml \
  && kubectl rollout restart deployment/ir-anthology-chat-api -n webisstud \
  && kubectl rollout status deployment/ir-anthology-chat-api -n webisstud --timeout=120s
```

If only `k8s.yaml` changed, skip build and push — apply and restart directly
(§7).

---

## 2. Step-by-Step Deploy

### 1. Build the image

```bash
docker build -t muhammadfarzadali/ir-anthology-chat-api:latest .
```

### 2. Push to Docker Hub

```bash
docker login                     # if the session expired
docker push muhammadfarzadali/ir-anthology-chat-api:latest
```

### 3. Apply the Kubernetes config (if `k8s.yaml` changed)

```bash
kubectl apply -f k8s.yaml
```

### 4. Restart the deployment to pull the new image

```bash
kubectl rollout restart deployment/ir-anthology-chat-api -n webisstud
```

### 5. Verify the rollout

```bash
kubectl rollout status deployment/ir-anthology-chat-api -n webisstud --timeout=120s
```

### 6. Confirm the pod is running

```bash
kubectl get pods -n webisstud -l app=ir-anthology-chat-api
```

Expect `1/1 Running` with a low `AGE`. The strategy is `Recreate`, so there is a
brief window with zero pods while the old one stops and the new one starts — a
gap in `kubectl get pods -w` is normal, not a failure.

---

## 3. Analytics Storage

Conversation analytics live in SQLite at `/data/analytics.sqlite3` inside the
container. Kubernetes mounts that path from the
`ir-anthology-chat-api-analytics` PersistentVolumeClaim, so data survives pod
restarts and image updates.

The deployment uses the `Recreate` strategy because the PVC is `ReadWriteOnce`:
the old pod must stop before the replacement can mount the volume.

Verify volume and database after deploying:

```bash
kubectl get pvc -n webisstud ir-anthology-chat-api-analytics
kubectl get pods -n webisstud -l app=ir-anthology-chat-api
kubectl exec -n webisstud <pod-name> -- ls -lh /data
```

Retention is configured through `ANALYTICS_RETENTION_DAYS`. Empty currently means
indefinite retention; set an approved number of days in `k8s.yaml` once a policy
exists.

### One-Time Interaction Schema Update

If an existing analytics database predates interaction logging, check the table
first:

```bash
kubectl exec -n webisstud <pod-name> -- python -c \
  "import sqlite3; c=sqlite3.connect('/data/analytics.sqlite3'); print([row[1] for row in c.execute('PRAGMA table_info(conversation_events)')])"
```

If `interaction_json` is missing: back up first (§4), then scale the API down,
mount the PVC in a maintenance pod, and apply the change.

```bash
kubectl scale deployment/ir-anthology-chat-api -n webisstud --replicas=0
```

```yaml
# maintenance-pod.yaml — one-off PVC mount, delete afterwards
apiVersion: v1
kind: Pod
metadata:
  name: analytics-maint
  namespace: webisstud
spec:
  restartPolicy: Never
  containers:
    - name: maint
      image: muhammadfarzadali/ir-anthology-chat-api:latest
      command: ["sleep", "3600"]
      volumeMounts:
        - name: analytics-data
          mountPath: /data
  volumes:
    - name: analytics-data
      persistentVolumeClaim:
        claimName: ir-anthology-chat-api-analytics
```

```bash
kubectl apply -f maintenance-pod.yaml
kubectl wait --for=condition=Ready pod/analytics-maint -n webisstud --timeout=120s

kubectl exec -n webisstud analytics-maint -- python -c \
  "import sqlite3; c=sqlite3.connect('/data/analytics.sqlite3'); c.execute('ALTER TABLE conversation_events ADD COLUMN interaction_json TEXT'); c.commit(); print('ok')"

kubectl delete pod analytics-maint -n webisstud --wait=false
rm -f maintenance-pod.yaml
kubectl scale deployment/ir-anthology-chat-api -n webisstud --replicas=1
kubectl rollout status deployment/ir-anthology-chat-api -n webisstud --timeout=120s
```

Then re-check the column and the event count. Keep the backup until new
conversation events are confirmed. Newly created databases include the column
automatically — this is a one-time migration for existing data only.

---

## 4. Copy the Kubernetes Database Locally

Use a SQLite **backup snapshot**, never a direct copy of a live database file:
the application may be mid-WAL, and copying the file can yield a torn database.

This is the bash equivalent of the PowerShell block in `DEPLOYMENT.md`. It finds
the running pod, creates a consistent snapshot inside it, copies it into the
current directory, then removes the temporary file from the pod.

```bash
# Some environments export a proxy that kubectl cannot use for cluster traffic.
# Unset it for the current shell (lowercase variants included — curl and python
# honour those).
unset HTTP_PROXY HTTPS_PROXY ALL_PROXY http_proxy https_proxy all_proxy

set -euo pipefail

pod=$(kubectl get pods -n webisstud \
  -l app=ir-anthology-chat-api \
  -o jsonpath='{.items[0].metadata.name}')

if [ -z "${pod}" ]; then
  echo "No running pod found for app=ir-anthology-chat-api" >&2
  exit 1
fi

echo "Using pod: ${pod}"

# Consistent snapshot via the SQLite backup API (WAL-safe).
kubectl exec -n webisstud "${pod}" -- python -c \
  "import sqlite3; src=sqlite3.connect('/data/analytics.sqlite3'); dst=sqlite3.connect('/tmp/analytics-snapshot.sqlite3'); src.backup(dst); dst.close(); src.close()"

# Pull it down.
kubectl cp -n webisstud "${pod}:/tmp/analytics-snapshot.sqlite3" ./kubernetes-analytics.sqlite3

# Clean up inside the pod.
kubectl exec -n webisstud "${pod}" -- rm -f /tmp/analytics-snapshot.sqlite3

ls -lh ./kubernetes-analytics.sqlite3
```

Sanity-check the copy before trusting it:

```bash
sqlite3 ./kubernetes-analytics.sqlite3 'PRAGMA integrity_check;'   # -> ok
```

Without the `sqlite3` CLI:

```bash
python3 -c "import sqlite3; print(sqlite3.connect('kubernetes-analytics.sqlite3').execute('PRAGMA integrity_check').fetchone()[0])"
```

If `kubectl cp` fails with `exec: "tar": executable file not found`, stream the
file instead:

```bash
kubectl exec -n webisstud "${pod}" -- cat /tmp/analytics-snapshot.sqlite3 > ./kubernetes-analytics.sqlite3
```

> **Do not commit `kubernetes-analytics.sqlite3`.** It contains real conversation
> data. This directory's `.gitignore` already excludes the snapshot and its
> SQLite sidecars, so a download here stays untracked:

```bash
git check-ignore -v kubernetes-analytics.sqlite3
# .gitignore:49:kubernetes-analytics.sqlite3   kubernetes-analytics.sqlite3
```

---

## 5. Query the Local Copy

List tables and their columns:

```bash
python3 - <<'PY'
import sqlite3

with sqlite3.connect("kubernetes-analytics.sqlite3") as connection:
    tables = connection.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ).fetchall()
    for (table_name,) in tables:
        columns = connection.execute(
            f"PRAGMA table_info({table_name})"
        ).fetchall()
        print(table_name, [column[1] for column in columns])
PY
```

Count sessions, conversation events, and feedback:

```bash
python3 - <<'PY'
import sqlite3

with sqlite3.connect("kubernetes-analytics.sqlite3") as connection:
    for table in ("sessions", "conversation_events", "answer_feedback"):
        try:
            count = connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            print(f"{table}: {count}")
        except sqlite3.OperationalError:
            print(f"{table}: not available")
PY
```

Inspect interaction types (only when `interaction_json` exists):

```bash
python3 - <<'PY'
import json
import sqlite3

with sqlite3.connect("kubernetes-analytics.sqlite3") as connection:
    columns = {
        row[1] for row in connection.execute(
            "PRAGMA table_info(conversation_events)"
        )
    }
    if "interaction_json" not in columns:
        print("This database does not contain interaction_json.")
    else:
        rows = connection.execute(
            "SELECT id, started_at, interaction_json "
            "FROM conversation_events ORDER BY id"
        )
        for event_id, started_at, interaction_json in rows:
            print(event_id, started_at, json.loads(interaction_json) if interaction_json else None)
PY
```

Inspect recorded feedback:

```bash
python3 - <<'PY'
import sqlite3

with sqlite3.connect("kubernetes-analytics.sqlite3") as connection:
    for row in connection.execute(
        "SELECT session_id, answer_turn_id, feedback, created_at "
        "FROM answer_feedback ORDER BY id"
    ):
        print(row)
PY
```

Why heredocs and not `python3 -c`: the quoting above would need escaping for
`"` and `$` inside `-c`, and the here-doc keeps the SQL readable. `<<'PY'`
(single-quoted delimiter) disables shell expansion — important, because the SQL
contains `$`-free but `{table}`-f-strings that must reach Python untouched.

---

## 6. Shell Translation Table

For anyone diffing this file against the PowerShell original:

| PowerShell | bash |
|---|---|
| `$env:HTTP_PROXY = ""` | `unset HTTP_PROXY http_proxy` |
| `$pod = kubectl ...` | `pod=$(kubectl ...)` |
| `` ` `` line continuation | `\` line continuation |
| `"${pod}:/tmp/f"` | `"${pod}:/tmp/f"` (same) |
| `.\file.sqlite3` | `./file.sqlite3` |
| `@" ... "@ \| python -` | `python3 - <<'PY' ... PY` |
| `$LASTEXITCODE` | `$?` |
| `Select-String` | `grep` |
| `Get-Content -Tail 100` | `kubectl logs --tail=100`, `tail -n 100` |

---

## 7. Kubernetes Configuration Changes Without Rebuilding

When only Kubernetes configuration changed:

```bash
kubectl apply -f k8s.yaml
kubectl rollout restart deployment/ir-anthology-chat-api -n webisstud
kubectl rollout status deployment/ir-anthology-chat-api -n webisstud --timeout=120s
kubectl get pods -n webisstud -l app=ir-anthology-chat-api
```

Preview what would change before applying:

```bash
kubectl diff -f k8s.yaml
```

---

## 8. API Key Safety

`OPENAI_API_KEY` must come from a Kubernetes Secret referenced via `secretRef` in
the Deployment. Never put a real key in `k8s.yaml`, a ConfigMap, or Git.

Create or update the secret:

```bash
kubectl create secret generic ir-anthology-chat-api-secrets \
  --namespace webisstud \
  --from-literal=OPENAI_API_KEY='<key>' \
  --dry-run=client -o yaml | kubectl apply -f -
```

Keep it out of shell history with a leading space (if `HISTCONTROL=ignorespace`)
or by reading it from a file/env var instead of inlining it.

---

## 9. Useful Commands

| Command | Description |
|---|---|
| `kubectl get pods -n webisstud -l app=ir-anthology-chat-api` | Check pod status |
| `kubectl logs -n webisstud -l app=ir-anthology-chat-api --tail=100 -f` | Follow pod logs |
| `kubectl describe pod -n webisstud -l app=ir-anthology-chat-api` | Detailed pod info |
| `kubectl exec -it <pod-name> -n webisstud -- /bin/sh` | Shell into pod |
| `kubectl exec -n webisstud <pod-name> -- ls -lh /data` | Inspect the analytics volume |
| `kubectl rollout history deployment/ir-anthology-chat-api -n webisstud` | Revision history |
| `kubectl rollout undo deployment/ir-anthology-chat-api -n webisstud` | Roll back one revision |
| `kubectl port-forward -n webisstud svc/ir-anthology-chat-api 8000:8000` | Reach the API locally |
| `kubectl get events -n webisstud --sort-by=.lastTimestamp` | Recent cluster events |
| `kubectl auth can-i --list -n webisstud` | Your permissions in the namespace |

Interactive UI over the same data: [`docs/k9s-cheatsheet.md`](../../docs/k9s-cheatsheet.md).
