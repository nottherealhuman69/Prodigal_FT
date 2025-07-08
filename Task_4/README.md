# Task 4: Kubernetes Pod Scaling (K8s + HPA)

## Overview
This task demonstrates Kubernetes Horizontal Pod Autoscaling (HPA) using a FastAPI application that can generate CPU load on demand. The system automatically scales from 1 to 10 pods based on CPU utilization.

## Architecture

### Components
- **FastAPI Application**: Simple web service with CPU load generation endpoint
- **Docker Container**: Containerized FastAPI app
- **Kubernetes Deployment**: Manages pod replicas with resource limits
- **Service**: Exposes the application via NodePort
- **HPA**: Automatically scales pods based on CPU usage (target: 50%)
- **Metrics Server**: Provides resource metrics for HPA decisions

### Flow Diagram
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Load Test     │───▶│   FastAPI App   │───▶│   CPU Load      │
│   (Python)      │    │   (Pod 1-10)    │    │   Generation    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Metrics       │◀───│   Kubernetes    │───▶│      HPA        │
│   Server        │    │   Cluster       │    │   (1-10 pods)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Prerequisites
- Docker installed
- Minikube installed
- kubectl installed
- Python 3.9+ with requests library

## Quick Start

### Option 1: Automated Setup (Recommended)
```bash
# Run the complete setup script
python setup.py
```

### Option 2: Manual Setup
```bash
# 1. Start Minikube
minikube start

# 2. Enable metrics server
minikube addons enable metrics-server

# 3. Build Docker image
docker build -t fastapi-cpu-load:latest .

# 4. Load image to Minikube
minikube image load fastapi-cpu-load:latest

# 5. Deploy Kubernetes resources
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f hpa.yaml

# 6. Wait for pods to be ready
kubectl wait --for=condition=ready pod -l app=fastapi-app --timeout=300s
```

## Testing the Application

### 1. Check Status
```bash
# View pods
kubectl get pods

# View service
kubectl get svc

# View HPA status
kubectl get hpa
```

### 2. Access the Application
```bash
# Start port forwarding (keep this running)
kubectl port-forward svc/fastapi-service 8080:8000
```

### 3. Test Endpoints
```bash
# Health check
curl http://localhost:8080/health

# Basic endpoint
curl http://localhost:8080/

# Generate CPU load
curl http://localhost:8080/load

# Pod information
curl http://localhost:8080/info
```

## Autoscaling Demo

### 1. Monitor in Real-time
Open multiple terminals:

**Terminal 1**: Port forwarding
```bash
kubectl port-forward svc/fastapi-service 8080:8000
```

**Terminal 2**: Watch pods
```bash
kubectl get pods -w
```

**Terminal 3**: Watch HPA
```bash
kubectl get hpa -w
```

### 2. Generate Load
**Terminal 4**: Run load test
```bash
python load_test.py
```

### 3. Observe Scaling
- Watch CPU usage increase in HPA output
- See new pods being created
- Monitor scaling behavior
- Observe scale-down after load stops

## File Structure
```
task4/
├── app.py              # FastAPI application
├── Dockerfile          # Container definition
├── requirements.txt    # Python dependencies
├── deployment.yaml     # Kubernetes deployment
├── service.yaml        # Kubernetes service
├── hpa.yaml           # Horizontal Pod Autoscaler
├── setup.py           # Automated setup script
├── load_test.py       # Load testing script
├── README.md          # This file
└── SUMMARY.md         # Implementation summary
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Basic status message |
| `/health` | GET | Health check |
| `/load` | GET | Generate CPU load (5 seconds) |
| `/info` | GET | Pod information |

## Configuration

### HPA Settings
- **Min Replicas**: 1
- **Max Replicas**: 10
- **Target CPU**: 50%
- **Scale Up**: 100% increase every 60s
- **Scale Down**: 50% decrease every 60s (after 5min stability)

### Resource Limits
- **CPU Request**: 100m
- **CPU Limit**: 500m
- **Memory Request**: 128Mi
- **Memory Limit**: 512Mi

## Monitoring Commands

```bash
# Real-time pod status
kubectl get pods -w

# HPA metrics
kubectl get hpa -w

# Resource usage
kubectl top pods

# Detailed HPA info
kubectl describe hpa fastapi-hpa

# Pod logs
kubectl logs -f deployment/fastapi-app
```

## Cleanup
```bash
# Remove all resources
kubectl delete -f hpa.yaml
kubectl delete -f service.yaml
kubectl delete -f deployment.yaml

# Stop Minikube (optional)
minikube stop
```

## Troubleshooting

### Common Issues
1. **Metrics not available**: Wait 1-2 minutes for metrics-server
2. **Image not found**: Ensure `minikube image load` completed
3. **Port already in use**: Change port in port-forward command
4. **HPA not scaling**: Check if load is generating sufficient CPU usage

### Debug Commands
```bash
# Check metrics server
kubectl get pods -n kube-system | grep metrics

# Verify image loaded
minikube image ls | grep fastapi

# Check pod logs
kubectl logs -l app=fastapi-app

# HPA events
kubectl describe hpa fastapi-hpa
```

## Demo Video Points
1. Show initial single pod
2. Start load test
3. Watch CPU usage increase
4. Observe new pods scaling up
5. Stop load test
6. Watch pods scale down
7. Demonstrate monitoring commands