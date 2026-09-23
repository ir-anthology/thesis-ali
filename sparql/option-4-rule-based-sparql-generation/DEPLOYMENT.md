# Deployment Guide

## Quick Deploy (One-Liner)

Use this when the application code or Docker image has changed:

```bash
docker build -t muhammadfarzadali/ir-anthology-chat-api:latest . && docker push muhammadfarzadali/ir-anthology-chat-api:latest && kubectl apply -f k8s.yaml && kubectl rollout restart deployment/ir-anthology-chat-api -n webisstud && kubectl rollout status deployment/ir-anthology-chat-api -n webisstud --timeout=120s
```

If only `k8s.yaml` or another Kubernetes setting changed, skip the build and push steps. Apply the manifest and restart the deployment directly.

## Step-by-Step Deploy

### 1. Build Docker Image

```bash
docker build -t muhammadfarzadali/ir-anthology-chat-api:latest .
```

### 2. Push to Docker Hub

```bash
docker push muhammadfarzadali/ir-anthology-chat-api:latest
```

### 3. Apply Updated Kubernetes Config (if k8s.yaml changed)

```bash
kubectl apply -f k8s.yaml
```

### 4. Restart Deployment to Pull New Image

```bash
kubectl rollout restart deployment/ir-anthology-chat-api -n webisstud
```

### 5. Verify Rollout Status

```bash
kubectl rollout status deployment/ir-anthology-chat-api -n webisstud --timeout=120s
```

### 6. Confirm Pod is Running

```bash
kubectl get pods -n webisstud -l app=ir-anthology-chat-api
```

## Analytics Storage

Conversation analytics are stored in SQLite at `/data/analytics.sqlite3` inside the container. Kubernetes mounts this path from the `ir-anthology-chat-api-analytics` PersistentVolumeClaim, so analytics data survives pod restarts and image updates.

The deployment uses the `Recreate` strategy because the PVC is `ReadWriteOnce`. During a restart, Kubernetes stops the existing pod before starting its replacement so the volume can be mounted safely.

Verify the persistent volume and database after deployment:

```bash
kubectl get pvc -n webisstud ir-anthology-chat-api-analytics
kubectl get pods -n webisstud -l app=ir-anthology-chat-api
kubectl exec -n webisstud <pod-name> -- ls -lh /data
```

Retention is configured through `ANALYTICS_RETENTION_DAYS`. An empty value currently means indefinite retention. Set an approved number of days in `k8s.yaml` when a retention policy is established.

### One-Time Interaction Schema Update

If an existing analytics database was created before interaction logging was added, check the table before relying on interaction data:

```bash
kubectl exec -n webisstud <pod-name> -- python -c "import sqlite3; c=sqlite3.connect('/data/analytics.sqlite3'); print([row[1] for row in c.execute('PRAGMA table_info(conversation_events)')])"
```

If `interaction_json` is missing, first create and download a SQLite backup using the snapshot procedure below. Then stop the API deployment, mount the analytics PVC in a temporary maintenance pod, and run:

```sql
ALTER TABLE conversation_events ADD COLUMN interaction_json TEXT;
```

After the command succeeds, delete the maintenance pod, scale the API deployment back to one replica, and verify the column and event count. Keep the backup until new conversation events have been confirmed. This is a one-time operational update for existing databases; newly created databases include the column automatically.

### Copy the Kubernetes Database Locally

Use a SQLite backup snapshot instead of copying the live database file directly. This is important because SQLite may be using its WAL journal while the application is running.

The following PowerShell commands locate the running pod, create a temporary consistent snapshot, and copy it to the current local directory:

```powershell
# Use these three lines if kubectl tries to connect through an unavailable local proxy.
$env:HTTP_PROXY = ""
$env:HTTPS_PROXY = ""
$env:ALL_PROXY = ""

$pod = kubectl get pods -n webisstud `
  -l app=ir-anthology-chat-api `
  -o jsonpath="{.items[0].metadata.name}"

kubectl exec $pod -n webisstud -- python -c "import sqlite3; src=sqlite3.connect('/data/analytics.sqlite3'); dst=sqlite3.connect('/tmp/analytics-snapshot.sqlite3'); src.backup(dst); dst.close(); src.close()"

kubectl cp "${pod}:/tmp/analytics-snapshot.sqlite3" `
  .\kubernetes-analytics.sqlite3 -n webisstud

# Remove the temporary snapshot from the pod after copying it.
kubectl exec $pod -n webisstud -- rm -f /tmp/analytics-snapshot.sqlite3
```

Do not commit `kubernetes-analytics.sqlite3` to Git. It contains conversation data.

### Query the Local Copy

List the available tables and columns:

```powershell
@"
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
"@ | python -
```

Count sessions, conversation events, and feedback:

```powershell
@"
import sqlite3

with sqlite3.connect("kubernetes-analytics.sqlite3") as connection:
    for table in ("sessions", "conversation_events", "answer_feedback"):
        try:
            count = connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            print(f"{table}: {count}")
        except sqlite3.OperationalError:
            print(f"{table}: not available")
"@ | python -
```

Inspect recorded interaction types when the database contains the `interaction_json` column:

```powershell
@"
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
"@ | python -
```

Inspect recorded feedback:

```powershell
@"
import sqlite3

with sqlite3.connect("kubernetes-analytics.sqlite3") as connection:
    for row in connection.execute(
        "SELECT session_id, answer_turn_id, feedback, created_at "
        "FROM answer_feedback ORDER BY id"
    ):
        print(row)
"@ | python -
```

## Kubernetes Configuration Changes Without Rebuilding

When only the Kubernetes configuration changes, use:

```bash
kubectl apply -f k8s.yaml
kubectl rollout restart deployment/ir-anthology-chat-api -n webisstud
kubectl rollout status deployment/ir-anthology-chat-api -n webisstud --timeout=120s
kubectl get pods -n webisstud -l app=ir-anthology-chat-api
```

## API Key Safety

The `OPENAI_API_KEY` should be supplied through a Kubernetes Secret and referenced with `secretRef` in the Deployment. Do not commit a real API key to `k8s.yaml`, a ConfigMap, or the Git repository.

## Useful Commands

| Command                                                          | Description       |
| ---------------------------------------------------------------- | ----------------- |
| `kubectl get pods -n webisstud -l app=ir-anthology-chat-api`     | Check pod status  |
| `kubectl logs -n webisstud -l app=ir-anthology-chat-api`         | View pod logs     |
| `kubectl describe pod -n webisstud -l app=ir-anthology-chat-api` | Detailed pod info |
| `kubectl exec -it <pod-name> -n webisstud -- /bin/sh`            | Shell into pod    |
