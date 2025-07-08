#!/usr/bin/env python3
"""
Setup script for Task 6 - Article + Scheme Scraper
Run this to install all dependencies
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up Task 6 - Article + Scheme Scraper")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Install pip packages
    if not run_command("pip install -r requirements.txt", "Installing Python packages"):
        sys.exit(1)
    
    # Install Playwright browsers
    if not run_command("playwright install chromium", "Installing Playwright browsers"):
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\nTo run the scraper:")
    print("  python scraper.py")
    print("\nOutput files will be generated:")
    print("  - scraped_data.json")
    print("  - scraped_data.csv") 
    print("  - summary_report.json")

if __name__ == "__main__":
    main()