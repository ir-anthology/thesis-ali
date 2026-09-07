# Kubernetes Deployment Guide

This document describes how to deploy and manage the `ir-anthology-chat-api` application on the Webis Kubernetes cluster.

## Table of Contents

- [Overview](#overview)
- [Cluster Access](#cluster-access)
- [Deployment Architecture](#deployment-architecture)
- [Building and Pushing the Docker Image](#building-and-pushing-the-docker-image)
- [Kubernetes Resources](#kubernetes-resources)
- [Common kubectl Commands](#common-kubectl-commands)
- [Troubleshooting](#troubleshooting)
- [Updating the Deployment](#updating-the-deployment)
- [Useful Links](#useful-links)

---

## Overview

| Setting | Value |
|---------|-------|
| Application | `ir-anthology-chat-api` |
| Namespace | `webisstud` |
| Image | `muhammadfarzadali/ir-anthology-chat-api:latest` |
| Service Type | NodePort |
| NodePort | `31080` |
| Container Port | `8000` |
| Resources | 1 CPU, 1Gi RAM |

---

## Cluster Access

### Prerequisites

- kubectl installed
- VPN connection (if outside Weimar University)
- Webis Kubernetes cluster credentials

### Configure kubectl

Run these commands one at a time on Windows:

```powershell
# Set credentials
kubectl config set-credentials "muhammad.farzad.ali@uni-weimar.de" \
    --auth-provider="oidc" \
    --auth-provider-arg=idp-issuer-url="https://dex.srv.webis.de" \
    --auth-provider-arg=client-id="webis-k8s-auth" \
    --auth-provider-arg=client-secret="O7irMStuJj43gG5soopaTiFExy9GAQ" \
    --auth-provider-arg=id-token="<your-id-token>" \
    --auth-provider-arg=refresh-token="<your-refresh-token>"

# Set cluster
kubectl config set-cluster webis --server="https://k8s.srv.webis.de"

# Set context
kubectl config set-context webis \
    --cluster="webis" \
    --namespace="webisstud" \
    --user="muhammad.farzad.ali@uni-weimar.de"

# Switch to context
kubectl config use-context webis
```

### Verify Connection

```powershell
kubectl auth whoami
```

Expected output:
```
ATTRIBUTE   VALUE
Username    oidc:muhammad.farzad.ali@uni-weimar.de
Groups      [oidc:auth/auth-webisstud system:authenticated]
```

---

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Kubernetes Cluster                        │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Namespace: webisstud                                │   │
│  │                                                     │   │
│  │  ┌──────────────────────────────────────────────┐  │   │
│  │  │  ConfigMap: ir-anthology-chat-api-config      │  │   │
│  │  │  - OPENAI_API_KEY                             │  │   │
│  │  │  - LLM_MODEL, DBLP_SPARQL_ENDPOINT, etc.     │  │   │
│  │  └──────────────────────────────────────────────┘  │   │
│  │                        │                           │   │
│  │                        ▼                           │   │
│  │  ┌──────────────────────────────────────────────┐  │   │
│  │  │  Deployment: ir-anthology-chat-api            │  │   │
│  │  │  ┌────────────────────────────────────────┐  │  │   │
│  │  │  │  Pod: ir-anthology-chat-api-xxxxx      │  │  │   │
│  │  │  │  ┌──────────────────────────────────┐  │  │  │   │
│  │  │  │  │  Container: ir-anthology-chat-api│  │  │  │   │
│  │  │  │  │  Image: muhammadfarzadali/...    │  │  │  │   │
│  │  │  │  │  Port: 8000                      │  │  │  │   │
│  │  │  │  └──────────────────────────────────┘  │  │  │   │
│  │  │  └────────────────────────────────────────┘  │  │   │
│  │  └──────────────────────────────────────────────┘  │   │
│  │                        │                           │   │
│  │                        ▼                           │   │
│  │  ┌──────────────────────────────────────────────┐  │   │
│  │  │  Service: ir-anthology-chat-api               │  │   │
│  │  │  Type: NodePort                               │  │   │
│  │  │  Port: 8000 → 31080                           │  │   │
│  │  └──────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────┘   │
│                          │                                  │
│                          ▼                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  External Access:                                    │   │
│  │  http://webis{6-10}.medien.uni-weimar.de:31080      │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## Building and Pushing the Docker Image

### Build the Image

```powershell
cd D:\work\hiwi\conversational-knowledge-graph\thesis-ali\sparql\option-4-rule-based-sparql-generation

docker build -t muhammadfarzadali/ir-anthology-chat-api:latest .
```

### Login to Docker Hub

```powershell
docker login
```

### Push the Image

```powershell
docker push muhammadfarzadali/ir-anthology-chat-api:latest
```

---

## Kubernetes Resources

### k8s.yaml

The deployment consists of three resources:

#### 1. ConfigMap

Stores non-sensitive configuration and the OpenAI API key.

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: ir-anthology-chat-api-config
  namespace: webisstud
data:
  OPENAI_API_KEY: "<your-api-key>"
  LLM_MODEL: "gpt-5.6-luna"
  LLM_TEMPERATURE: "0.0"
  LLM_MAX_TOKENS: "2000"
  DBLP_SPARQL_ENDPOINT: "https://sparql.dblp.org/sparql"
  MAX_RESULT_ROWS: "50"
  QUESTION_BATCH_SIZE: "10"
  API_HOST: "0.0.0.0"
  API_PORT: "8000"
  RELOAD: "false"
```

#### 2. Deployment

Manages the pod lifecycle.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ir-anthology-chat-api
  namespace: webisstud
spec:
  selector:
    matchLabels:
      app: ir-anthology-chat-api
  replicas: 1
  template:
    metadata:
      labels:
        app: ir-anthology-chat-api
    spec:
      containers:
        - name: ir-anthology-chat-api
          image: muhammadfarzadali/ir-anthology-chat-api:latest
          imagePullPolicy: Always
          resources:
            requests:
              cpu: "1"
              memory: 1Gi
            limits:
              cpu: "1"
              memory: 1Gi
          ports:
            - name: http
              containerPort: 8000
              protocol: TCP
          envFrom:
            - configMapRef:
                name: ir-anthology-chat-api-config
          livenessProbe:
            httpGet:
              path: /api/health
              port: http
            initialDelaySeconds: 10
            periodSeconds: 30
            timeoutSeconds: 5
            failureThreshold: 3
          readinessProbe:
            httpGet:
              path: /api/health
              port: http
            initialDelaySeconds: 5
            periodSeconds: 10
            timeoutSeconds: 3
            failureThreshold: 3
```

#### 3. Service

Exposes the application via NodePort.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: ir-anthology-chat-api
  namespace: webisstud
spec:
  type: NodePort
  selector:
    app: ir-anthology-chat-api
  ports:
    - port: 8000
      targetPort: http
      nodePort: 31080
      protocol: TCP
```

---

## Common kubectl Commands

### Viewing Resources

```powershell
# List all pods in the namespace
kubectl get pods -n webisstud

# List pods with labels
kubectl get pods -n webisstud -l app=ir-anthology-chat-api

# List all resources for the app
kubectl get all -n webisstud -l app=ir-anthology-chat-api

# Get detailed pod information
kubectl describe pod -n webisstud -l app=ir-anthology-chat-api

# Get service information
kubectl get svc -n webisstud ir-anthology-chat-api

# Get deployment information
kubectl get deployment -n webisstud ir-anthology-chat-api
```

### Viewing Logs

```powershell
# View pod logs
kubectl logs -n webisstud -l app=ir-anthology-chat-api

# Follow logs in real-time
kubectl logs -n webisstud -l app=ir-anthology-chat-api -f

# View last 100 lines
kubectl logs -n webisstud -l app=ir-anthology-chat-api --tail=100
```

### Accessing the Pod

```powershell
# Open a shell inside the pod
kubectl exec -it -n webisstud -l app=ir-anthology-chat-api -- bash

# Run a single command
kubectl exec -it -n webisstud -l app=ir-anthology-chat-api -- ls /app

# Copy files from pod to local
kubectl cp webisstud/<pod-name>:/app/data ./local-data

# Copy files from local to pod
kubectl cp ./local-file webisstud/<pod-name>:/app/
```

### Port Forwarding

```powershell
# Forward local port 8080 to pod port 8000
kubectl port-forward -n webisstud -l app=ir-anthology-chat-api 8080:8000

# Access locally at http://localhost:8080
```

### Scaling

```powershell
# Scale to 2 replicas
kubectl scale deployment -n webisstud ir-anthology-chat-api --replicas=2

# Scale back to 1 replica
kubectl scale deployment -n webisstud ir-anthology-chat-api --replicas=1
```

### Restarting

```powershell
# Restart the deployment (rolling restart)
kubectl rollout restart deployment -n webisstud ir-anthology-chat-api

# Check rollout status
kubectl rollout status deployment -n webisstud ir-anthology-chat-api

# View rollout history
kubectl rollout history deployment -n webisstud ir-anthology-chat-api
```

### Deleting Resources

```powershell
# Delete using the YAML file
kubectl delete -f k8s.yaml

# Delete the deployment only
kubectl delete deployment -n webisstud ir-anthology-chat-api

# Delete the service only
kubectl delete svc -n webisstud ir-anthology-chat-api

# Delete the configmap only
kubectl delete configmap -n webisstud ir-anthology-chat-api-config
```

---

## Troubleshooting

### Pod is in `ContainerCreating` Status

The pod is pulling the Docker image. Wait 30-60 seconds. If it stays in this state:

```powershell
# Check pod events
kubectl describe pod -n webisstud -l app=ir-anthology-chat-api

# Look for "Events" at the bottom of the output
```

### Pod is in `CrashLoopBackOff` Status

The container is crashing. Check the logs:

```powershell
# View crash logs
kubectl logs -n webisstud -l app=ir-anthology-chat-api

# View previous container logs (if restarted)
kubectl logs -n webisstud -l app=ir-anthology-chat-api --previous
```

### Pod is in `ImagePullBackOff` Status

The Docker image cannot be pulled. Verify:

1. Image exists on Docker Hub: `docker pull muhammadfarzadali/ir-anthology-chat-api:latest`
2. Image name is correct in `k8s.yaml`
3. Docker Hub is accessible from the cluster

### Health Check Failures

If the pod is running but health checks fail:

```powershell
# Test the health endpoint manually
kubectl exec -it -n webisstud -l app=ir-anthology-chat-api -- curl http://localhost:8000/api/health
```

### NodePort Already in Use

If port `31080` is taken, change the `nodePort` value in `k8s.yaml` to another port in the range 30000-32767, then reapply:

```powershell
kubectl apply -f k8s.yaml
```

---

## Updating the Deployment

### Update the Docker Image

1. Make code changes
2. Build and push a new image:

```powershell
docker build -t muhammadfarzadali/ir-anthology-chat-api:latest .
docker push muhammadfarzadali/ir-anthology-chat-api:latest
```

3. Restart the deployment to pull the new image:

```powershell
kubectl rollout restart deployment -n webisstud ir-anthology-chat-api
```

### Update Configuration

1. Edit `k8s.yaml` (ConfigMap section)
2. Apply changes:

```powershell
kubectl apply -f k8s.yaml
```

3. Restart the deployment to pick up new config:

```powershell
kubectl rollout restart deployment -n webisstud ir-anthology-chat-api
```

---

## Access Points

| Method | URL |
|--------|-----|
| API Base | `http://webis6.medien.uni-weimar.de:31080` |
| Health Check | `http://webis6.medien.uni-weimar.de:31080/api/health` |
| Swagger Docs | `http://webis6.medien.uni-weimar.de:31080/docs` |
| Alternative Nodes | `webis7`, `webis8`, `webis9`, `webis10` |

---

## Useful Links

- [Webis Kubernetes Tutorial](https://kb.webis.de/k8s-manual/kubernetes-tutorial/index.html)
- [kubectl Cheat Sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Docker Hub - muhammadfarzadali](https://hub.docker.com/u/muhammadfarzadali)
