# Task 4: Kubernetes Pod Scaling with FastAPI

This project demonstrates Kubernetes Horizontal Pod Autoscaling (HPA) using a FastAPI application that creates CPU load on demand.

## Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Load Test     │    │   Port Forward  │    │   FastAPI Pod   │
│   Script        │───▶│   localhost:8080│───▶│   (1-10 pods)   │
│  (1000 requests)│    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │       HPA       │
                       │   (Monitors     │
                       │   CPU > 50%)    │
                       └─────────────────┘
```

## Flow Diagram

```
1. Deploy FastAPI app → Kubernetes creates 1 pod
2. Start port-forward → Access via localhost:8080
3. Load test sends 1000 requests → CPU usage spikes above 50%
4. HPA monitors CPU → Creates additional pods (2-10)
5. Load distributed → Multiple pods handle requests
6. Load stops → CPU decreases → HPA scales down after 5 minutes
```

## Prerequisites

- Docker installed and running
- Minikube installed and running
- kubectl configured to use minikube context
- Python 3.9+ with requests library

## Project Structure

```
Task_4/
├── app.py                    # FastAPI application
├── requirements.txt          # Python dependencies
├── setup_requirements.txt    # Setup script dependencies
├── Dockerfile               # Container configuration
├── deployment.yaml          # Kubernetes deployment
├── service.yaml             # Kubernetes service
├── hpa.yaml                # Horizontal Pod Autoscaler
├── setup.py                # Python setup script
├── load_test.py            # Load testing script (1000 requests)
└── README.md               # This file
```

## Setup Instructions

### 1. Start Minikube
```bash
minikube start
```

### 2. Enable Metrics Server (Required for HPA)
```bash
minikube addons enable metrics-server
```

### 3. Install Setup Dependencies
```bash
pip install -r setup_requirements.txt
```

### 4. Run Python Setup Script
```bash
python setup.py
```

The setup script will automatically:
- Check if Docker, Minikube, and kubectl are installed
- Start Minikube if not running
- Enable metrics server for autoscaling
- Build and load the Docker image
- Deploy all Kubernetes resources
- Wait for everything to be ready
- Show you next steps

### 5. Alternative Manual Setup
If the Python script doesn't work, run these commands manually:

```bash
# Start minikube and enable metrics
minikube start
minikube addons enable metrics-server

# Build Docker image
docker build -t fastapi-cpu-load:latest .

# Load image into minikube
minikube image load fastapi-cpu-load:latest

# Apply Kubernetes configs
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f hpa.yaml

# Wait for pods to be ready
kubectl wait --for=condition=ready pod -l app=fastapi-app --timeout=300s
```

## Testing the Application

### 1. Check if Everything is Running
```bash
kubectl get pods
kubectl get svc
kubectl get hpa
```

### 2. Access the Service via Port Forward
```bash
# Run this in one terminal and keep it running
kubectl port-forward svc/fastapi-service 8080:8000
```

### 3. Test Basic Functionality (in another terminal)
```bash
curl http://localhost:8080/
curl http://localhost:8080/health
```

### 4. Create CPU Load (Manual)
```bash
# This will create CPU load for 5 seconds
curl http://localhost:8080/load
```

### 5. Run Load Test for Autoscaling
```bash
# Make sure port-forward is running first!
python load_test.py
```

## Monitoring Autoscaling

### Watch Pods Scale Up/Down
```bash
kubectl get pods -w
```

### Monitor HPA Status
```bash
kubectl get hpa -w
```

### Check Resource Usage
```bash
kubectl top pods
```

## How to Know It's Working

1. **Initial State**: You should see 1 pod running
2. **Port Forward Active**: `curl http://localhost:8080/health` returns `{"status":"healthy"}`
3. **During Load Test**: 
   - Load test runs 1000 requests with 20 concurrent workers
   - CPU usage increases to >50% (visible in `kubectl top pods`)
   - HPA creates more pods (visible in `kubectl get pods -w`)
   - You'll see 2-10 pods in "Running" state
4. **After Load Test**: 
   - CPU usage decreases below 50%
   - HPA scales down to 1 pod after 5 minutes (stabilization period)

## Expected Behavior

- **Scale Up**: When CPU > 50%, HPA adds pods (max 10)
- **Scale Down**: When CPU < 50%, HPA removes pods (min 1) after 5-minute stabilization
- **Resource Limits**: Each pod limited to 500m CPU, 512Mi memory
- **Health Checks**: Liveness and readiness probes ensure pod health

## Autoscaling Configuration

The HPA is configured with:
- **Target CPU**: 50% utilization
- **Min Replicas**: 1
- **Max Replicas**: 10
- **Scale Up**: Can double pods every 60 seconds
- **Scale Down**: Can reduce by 50% every 60 seconds after 5-minute stabilization

## Load Test Details

The `load_test.py` script:
- Sends **1000 HTTP requests** to `/load` endpoint
- Uses **20 concurrent workers** for maximum CPU impact
- Each request triggers 5 seconds of intensive CPU computation
- Tests connection first before starting load test
- Provides real-time feedback on request success/failure

## Troubleshooting

### Pods Not Scaling?
- Check if metrics-server is running: `kubectl get pods -n kube-system | grep metrics`
- Verify HPA can get metrics: `kubectl describe hpa fastapi-hpa`
- Check resource requests are set in deployment.yaml

### Can't Access the Service?
- Use port forwarding: `kubectl port-forward svc/fastapi-service 8080:8000`
- Test with: `curl http://localhost:8080/health`
- Alternative: `minikube service fastapi-service --url`

### Load Test Failing?
- Ensure port-forward is running: `kubectl port-forward svc/fastapi-service 8080:8000`
- Test connection manually: `curl http://localhost:8080/health`
- Install requests if needed: `pip install requests`

### Image Pull Issues?
- Build image: `docker build -t fastapi-cpu-load:latest .`
- Load into minikube: `minikube image load fastapi-cpu-load:latest`
- Check deployment has `imagePullPolicy: Never`

## Cleanup

```bash
kubectl delete -f hpa.yaml
kubectl delete -f service.yaml
kubectl delete -f deployment.yaml
```

## Key Learning Points

1. **HPA Requirements**: Resource requests must be set for HPA to work
2. **Metrics Server**: Essential for HPA to get CPU/memory metrics
3. **Stabilization**: Prevents rapid scaling up/down (thrashing)
4. **Port Forwarding**: Reliable way to access services in local development
5. **Resource Limits**: Protect cluster from resource exhaustion
6. **Health Checks**: Ensure only healthy pods receive traffic

## Production Considerations

This setup works identically in production Kubernetes clusters (EKS, GKE, AKS):
- Replace Minikube with production cluster
- Use LoadBalancer or Ingress instead of port-forward
- Consider custom metrics (queue length, response time) for scaling
- Add resource quotas and limits for multi-tenant environments
- Implement proper monitoring and alerting for scaling events