import requests
import time
import threading
import concurrent.futures
from datetime import datetime

def make_request(url, request_num):
    """Make a single request to the load endpoint"""
    try:
        response = requests.get(f"{url}/load", timeout=30)
        print(f"Request {request_num}: Status {response.status_code}, Time: {datetime.now()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Request {request_num} failed: {e}")
        return False

def generate_load(base_url, num_requests=50, max_workers=10):
    """Generate load by making multiple concurrent requests"""
    print(f"Starting load test with {num_requests} requests using {max_workers} workers")
    print(f"Target URL: {base_url}")
    
    successful_requests = 0
    failed_requests = 0
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all requests
        futures = []
        for i in range(num_requests):
            future = executor.submit(make_request, base_url, i+1)
            futures.append(future)
            time.sleep(0.1)  # Small delay between request submissions
        
        # Wait for all requests to complete
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                if result:
                    successful_requests += 1
                else:
                    failed_requests += 1
            except Exception as e:
                print(f"Request failed with exception: {e}")
                failed_requests += 1
    
    print(f"\nLoad test completed!")
    print(f"Successful requests: {successful_requests}")
    print(f"Failed requests: {failed_requests}")
    print(f"Total requests: {num_requests}")

if __name__ == "__main__":
    # Use localhost with port-forward
    BASE_URL = "http://localhost:8080"  # Assumes kubectl port-forward is running
    
    print("Starting load test...")
    print("IMPORTANT: Make sure you have port-forward running in another terminal:")
    print("kubectl port-forward svc/fastapi-service 8080:8000")
    print("")
    
    # Test connection first
    try:
        import requests
        test_response = requests.get(f"{BASE_URL}/health", timeout=5)
        if test_response.status_code == 200:
            print("✅ Connection test successful!")
        else:
            print("❌ Connection test failed!")
            print("Make sure port-forward is running: kubectl port-forward svc/fastapi-service 8080:8000")
            exit(1)
    except Exception as e:
        print(f"❌ Cannot connect to {BASE_URL}")
        print(f"Error: {e}")
        print("Make sure port-forward is running: kubectl port-forward svc/fastapi-service 8080:8000")
        exit(1)
    
    print("This will create CPU load to trigger autoscaling")
    print("Monitor with: kubectl get pods -w")
    
    generate_load(BASE_URL, num_requests=1000, max_workers=20)