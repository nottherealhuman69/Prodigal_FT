#!/usr/bin/env python3
"""
Kubernetes Pod Scaling Setup Script
This script automates the entire setup process for Task 4
"""

import subprocess
import sys
import time
import json
import requests
from pathlib import Path

class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_step(step_num, message):
    print(f"\n{Colors.BLUE}=== Step {step_num}: {message} ==={Colors.END}")

def print_success(message):
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠️ {message}{Colors.END}")

def print_error(message):
    print(f"{Colors.RED}❌ {message}{Colors.END}")

def run_command(cmd, check=True, capture_output=False):
    """Run a shell command with error handling"""
    try:
        print(f"Running: {cmd}")
        if capture_output:
            result = subprocess.run(cmd, shell=True, check=check, 
                                  capture_output=True, text=True)
            return result.stdout.strip()
        else:
            result = subprocess.run(cmd, shell=True, check=check)
            return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print_error(f"Command failed: {cmd}")
        print_error(f"Error: {e}")
        return False

def check_prerequisites():
    """Check if required tools are installed"""
    print_step(0, "Checking Prerequisites")
    
    tools = {
        'docker': 'docker --version',
        'minikube': 'minikube version',
        'kubectl': 'kubectl version --client'
    }
    
    missing_tools = []
    
    for tool, cmd in tools.items():
        try:
            result = subprocess.run(cmd, shell=True, check=True, 
                                  capture_output=True, text=True)
            print_success(f"{tool} is installed")
        except subprocess.CalledProcessError:
            missing_tools.append(tool)
            print_error(f"{tool} is not installed")
    
    if missing_tools:
        print_error("Please install missing tools before continuing:")
        print("- Docker: https://docs.docker.com/get-docker/")
        print("- Minikube: https://minikube.sigs.k8s.io/docs/start/")
        print("- kubectl: Usually comes with minikube")
        return False
    
    return True

def start_minikube():
    """Start minikube if not running"""
    print_step(1, "Starting Minikube")
    
    # Check if minikube is running
    try:
        status = run_command("minikube status", capture_output=True)
        if "host: Running" in status:
            print_success("Minikube is already running")
            return True
    except:
        pass
    
    print("Starting minikube...")
    if run_command("minikube start"):
        print_success("Minikube started successfully")
        return True
    else:
        print_error("Failed to start minikube")
        return False

def enable_metrics_server():
    """Enable metrics server for HPA"""
    print_step(2, "Enabling Metrics Server")
    
    if run_command("minikube addons enable metrics-server"):
        print_success("Metrics server enabled")
        # Wait for metrics server to be ready
        print("Waiting for metrics server to be ready...")
        time.sleep(10)
        return True
    else:
        print_error("Failed to enable metrics server")
        return False

def build_docker_image():
    """Build the Docker image"""
    print_step(3, "Building Docker Image")
    
    if run_command("docker build -t fastapi-cpu-load:latest ."):
        print_success("Docker image built successfully")
        return True
    else:
        print_error("Failed to build Docker image")
        return False

def load_image_to_minikube():
    """Load Docker image into minikube"""
    print_step(4, "Loading Image into Minikube")
    
    if run_command("minikube image load fastapi-cpu-load:latest"):
        print_success("Image loaded into minikube")
        return True
    else:
        print_error("Failed to load image into minikube")
        return False

def deploy_kubernetes_resources():
    """Deploy all Kubernetes resources"""
    print_step(5, "Deploying Kubernetes Resources")
    
    resources = ['deployment.yaml', 'service.yaml', 'hpa.yaml']
    
    for resource in resources:
        if not Path(resource).exists():
            print_error(f"{resource} not found")
            return False
        
        if run_command(f"kubectl apply -f {resource}"):
            print_success(f"Applied {resource}")
        else:
            print_error(f"Failed to apply {resource}")
            return False
    
    return True

def wait_for_deployment():
    """Wait for deployment to be ready"""
    print_step(6, "Waiting for Deployment to be Ready")
    
    print("Waiting for pods to be ready (this may take a few minutes)...")
    cmd = "kubectl wait --for=condition=ready pod -l app=fastapi-app --timeout=300s"
    
    if run_command(cmd):
        print_success("Deployment is ready!")
        return True
    else:
        print_error("Deployment failed to become ready")
        return False

def get_service_info():
    """Get service access information"""
    print_step(7, "Getting Service Information")
    
    try:
        minikube_ip = run_command("minikube ip", capture_output=True)
        if minikube_ip:
            service_url = f"http://{minikube_ip}:30080"
            print_success(f"Minikube IP: {minikube_ip}")
            print_success(f"Service URL: {service_url}")
            return minikube_ip, service_url
        else:
            print_error("Failed to get minikube IP")
            return None, None
    except Exception as e:
        print_error(f"Error getting service info: {e}")
        return None, None

def test_service(service_url):
    """Test if the service is accessible"""
    print_step(8, "Testing Service")
    
    if not service_url:
        print_error("No service URL available")
        return False
    
    try:
        print(f"Testing connection to {service_url}")
        response = requests.get(f"{service_url}/health", timeout=10)
        if response.status_code == 200:
            print_success("Service is responding correctly!")
            print(f"Response: {response.json()}")
            return True
        else:
            print_error(f"Service returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print_warning(f"Service test failed: {e}")
        print_warning("Service might still be starting up. Try testing manually in a few minutes.")
        return False

def show_status():
    """Show current cluster status"""
    print_step(9, "Showing Cluster Status")
    
    print("\n📊 Current Status:")
    print("-" * 50)
    
    # Show pods
    print("\n🔍 Pods:")
    run_command("kubectl get pods")
    
    # Show services
    print("\n🌐 Services:")
    run_command("kubectl get svc")
    
    # Show HPA
    print("\n📈 Horizontal Pod Autoscaler:")
    run_command("kubectl get hpa")

def update_load_test_script(minikube_ip):
    """Update the load test script with the correct IP"""
    if not minikube_ip:
        return
    
    try:
        # Read the current load_test.py
        with open('load_test.py', 'r') as f:
            content = f.read()
        
        # Replace the IP
        updated_content = content.replace(
            'BASE_URL = "http://192.168.49.2:30080"',
            f'BASE_URL = "http://{minikube_ip}:30080"'
        )
        
        # Write back
        with open('load_test.py', 'w') as f:
            f.write(updated_content)
        
        print_success(f"Updated load_test.py with IP: {minikube_ip}")
    except Exception as e:
        print_warning(f"Could not update load_test.py: {e}")

def show_next_steps(service_url):
    """Show what to do next"""
    print(f"\n{Colors.BOLD}🎉 Setup Complete! Here's what you can do next:{Colors.END}")
    print("-" * 60)
    
    if service_url:
        print(f"\n1. 🧪 Test the basic functionality:")
        print(f"   curl {service_url}/")
        print(f"   curl {service_url}/health")
        
        print(f"\n2. 💪 Create CPU load:")
        print(f"   curl {service_url}/load")
        
        print(f"\n3. 🚀 Run load test for autoscaling:")
        print(f"   python load_test.py")
    
    print(f"\n4. 👀 Monitor scaling in real-time:")
    print(f"   kubectl get pods -w")
    print(f"   kubectl get hpa -w")
    
    print(f"\n5. 📊 Check resource usage:")
    print(f"   kubectl top pods")
    
    print(f"\n6. 🧹 Clean up when done:")
    print(f"   kubectl delete -f hpa.yaml")
    print(f"   kubectl delete -f service.yaml")
    print(f"   kubectl delete -f deployment.yaml")

def main():
    """Main setup function"""
    print(f"{Colors.BOLD}🚀 Kubernetes Pod Scaling Setup{Colors.END}")
    print("This script will set up everything for Task 4")
    print("-" * 50)
    
    # Check prerequisites
    if not check_prerequisites():
        sys.exit(1)
    
    # Setup steps
    steps = [
        start_minikube,
        enable_metrics_server,
        build_docker_image,
        load_image_to_minikube,
        deploy_kubernetes_resources,
        wait_for_deployment,
    ]
    
    for step in steps:
        if not step():
            print_error("Setup failed. Please check the errors above.")
            sys.exit(1)
    
    # Get service info and test
    minikube_ip, service_url = get_service_info()
    update_load_test_script(minikube_ip)
    test_service(service_url)
    show_status()
    show_next_steps(service_url)
    
    print(f"\n{Colors.GREEN}✨ Setup completed successfully!{Colors.END}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Setup interrupted by user{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)