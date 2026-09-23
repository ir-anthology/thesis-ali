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
