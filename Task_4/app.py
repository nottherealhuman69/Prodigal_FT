from fastapi import FastAPI
import time
import hashlib
import os

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "FastAPI CPU Load Test App", "status": "running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/load")
def cpu_load():
    """Endpoint that creates CPU load for testing autoscaling"""
    # Create CPU load by doing intensive computation
    start_time = time.time()
    
    # Run CPU-intensive task for 5 seconds
    end_time = start_time + 5
    result = 0
    
    while time.time() < end_time:
        # CPU intensive operation
        for i in range(1000):
            result += hashlib.md5(f"test_{i}_{time.time()}".encode()).hexdigest().__hash__()
    
    duration = time.time() - start_time
    return {
        "message": "CPU load test completed",
        "duration_seconds": round(duration, 2),
        "result": result % 1000000  # Keep number manageable
    }

@app.get("/info")
def get_info():
    """Get pod information"""
    return {
        "hostname": os.environ.get("HOSTNAME", "unknown"),
        "pod_name": os.environ.get("HOSTNAME", "unknown"),
        "app_version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)