# Deployment Guide

## Quick Deploy (One-Liner)

```bash
docker build -t muhammadfarzadali/ir-anthology-chat-api:latest . && docker push muhammadfarzadali/ir-anthology-chat-api:latest && kubectl apply -f k8s.yaml && kubectl rollout restart deployment/ir-anthology-chat-api -n webisstud && kubectl rollout status deployment/ir-anthology-chat-api -n webisstud --timeout=120s
```

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

## Useful Commands

| Command                                                          | Description       |
| ---------------------------------------------------------------- | ----------------- |
| `kubectl get pods -n webisstud -l app=ir-anthology-chat-api`     | Check pod status  |
| `kubectl logs -n webisstud -l app=ir-anthology-chat-api`         | View pod logs     |
| `kubectl describe pod -n webisstud -l app=ir-anthology-chat-api` | Detailed pod info |
| `kubectl exec -it <pod-name> -n webisstud -- /bin/sh`            | Shell into pod    |
