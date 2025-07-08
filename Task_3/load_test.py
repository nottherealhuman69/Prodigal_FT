import requests
import time
import threading
import json
from datetime import datetime

# Configuration
API_URL = "http://localhost:5001"
TOTAL_REQUESTS = 1000
CONCURRENT_THREADS = 10
REQUESTS_PER_THREAD = TOTAL_REQUESTS // CONCURRENT_THREADS

def send_requests(thread_id, num_requests):
    """Send requests from a single thread"""
    success_count = 0
    error_count = 0
    
    for i in range(num_requests):
        try:
            # Create test event data
            event_data = {
                'thread_id': thread_id,
                'request_number': i,
                'timestamp': datetime.now().isoformat(),
                'test_data': f'Test data from thread {thread_id}, request {i}'
            }
            
            # Send POST request
            response = requests.post(
                f"{API_URL}/register_event",
                json=event_data,
                timeout=10
            )
            
            if response.status_code == 200:
                success_count += 1
                print(f"Thread {thread_id} - Request {i+1}: SUCCESS")
            else:
                error_count += 1
                print(f"Thread {thread_id} - Request {i+1}: ERROR {response.status_code}")
                
        except Exception as e:
            error_count += 1
            print(f"Thread {thread_id} - Request {i+1}: EXCEPTION {e}")
        
        # Small delay to prevent overwhelming
        time.sleep(0.01)
    
    print(f"Thread {thread_id} completed: {success_count} success, {error_count} errors")

def main():
    print(f"Starting load test with {TOTAL_REQUESTS} requests using {CONCURRENT_THREADS} threads")
    print(f"Target URL: {API_URL}")
    
    # Check if API is healthy
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code != 200:
            print("API health check failed!")
            return
        print("API health check passed")
    except Exception as e:
        print(f"Cannot connect to API: {e}")
        return
    
    # Record start time
    start_time = time.time()
    
    # Create and start threads
    threads = []
    for i in range(CONCURRENT_THREADS):
        thread = threading.Thread(
            target=send_requests,
            args=(i, REQUESTS_PER_THREAD)
        )
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    # Calculate total time
    end_time = time.time()
    total_time = end_time - start_time
    
    print(f"\nLoad test completed!")
    print(f"Total time: {total_time:.2f} seconds")
    print(f"Requests per second: {TOTAL_REQUESTS / total_time:.2f}")
    print(f"Check logs/consumer.log and logs/processed_events.txt to see processed events")

if __name__ == '__main__':
    main()