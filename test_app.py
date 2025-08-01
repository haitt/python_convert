#!/usr/bin/env python3
"""
Simple test script for the PDF/Word converter application
"""

import requests
import time
import os
from pathlib import Path

def test_application():
    """Test the basic functionality of the application"""
    
    base_url = "http://localhost"
    
    print("🧪 Testing PDF/Word Converter Application")
    print("=" * 50)
    
    # Test 1: Check if the application is running
    print("\n1. Testing application availability...")
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        if response.status_code == 200:
            print("✅ Application is running and accessible")
        else:
            print(f"❌ Application returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to application: {e}")
        print("   Make sure the application is running with: docker-compose up -d")
        return False
    
    # Test 2: Check API endpoints
    print("\n2. Testing API endpoints...")
    
    # Test conversions endpoint
    try:
        response = requests.get(f"{base_url}/conversions", timeout=10)
        if response.status_code == 200:
            print("✅ /conversions endpoint is working")
        else:
            print(f"❌ /conversions endpoint returned: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ /conversions endpoint error: {e}")
    
    # Test 3: Check if directories exist
    print("\n3. Checking file directories...")
    
    uploads_dir = Path("uploads")
    converted_dir = Path("converted")
    
    if uploads_dir.exists():
        print("✅ uploads directory exists")
    else:
        print("❌ uploads directory missing")
    
    if converted_dir.exists():
        print("✅ converted directory exists")
    else:
        print("❌ converted directory missing")
    
    # Test 4: Check Docker services
    print("\n4. Checking Docker services...")
    
    try:
        import subprocess
        result = subprocess.run(["docker-compose", "ps"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Docker Compose is available")
            print("   Services status:")
            for line in result.stdout.split('\n'):
                if 'web' in line or 'nginx' in line or 'db' in line:
                    print(f"   {line.strip()}")
        else:
            print("❌ Docker Compose check failed")
    except Exception as e:
        print(f"❌ Docker Compose check error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Basic tests completed!")
    print("\nTo start the application:")
    print("   docker-compose up -d")
    print("\nTo stop the application:")
    print("   docker-compose down")
    print("\nTo view logs:")
    print("   docker-compose logs -f")
    
    return True

if __name__ == "__main__":
    test_application() 