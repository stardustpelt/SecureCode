#!/usr/bin/env python3
"""
Test script for SecureCode API (Backend Only)
For local tests, use 127.0.0.1. For another device, use the server's LAN IP after starting Django with 0.0.0.0:8000.
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

def test_health():
    """Test health check endpoint"""
    print("Testing health check...")
    response = requests.get(f"{BASE_URL}/health/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")

def test_analyze_success():
    """Test code analysis with valid code"""
    print("Testing code analysis (valid code)...")
    code = """def greet(name):
    return f"Hello, {name}!"

print(greet("World"))"""
    
    data = {
        "code": code,
        "filename": "test_success"
    }
    
    response = requests.post(f"{BASE_URL}/analyze/", json=data)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Has Errors: {result.get('has_errors')}")
    print(f"Output: {result.get('output')}")
    print(f"Status: {result.get('status')}\n")

def test_analyze_error():
    """Test code analysis with indentation error"""
    print("Testing code analysis (with error)...")
    code = """def greet(name):
print("Hello")  # Indentation error
    return name"""
    
    data = {
        "code": code,
        "filename": "test_error"
    }
    
    response = requests.post(f"{BASE_URL}/analyze/", json=data)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Has Errors: {result.get('has_errors')}")
    print(f"Error Count: {result.get('error_count')}")
    if result.get('errors'):
        for error in result['errors']:
            print(f"  - Line {error['line']}: {error['message']}")
    print()

def test_get_report():
    """Test getting a report"""
    print("Testing get report...")
    response = requests.get(f"{BASE_URL}/report/test_success/")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Filename: {result.get('filename')}")
        print(f"Report preview: {result.get('report')[:100]}...\n")

if __name__ == "__main__":
    print("=" * 60)
    print("SecureCode API Test Suite")
    print("=" * 60 + "\n")
    
    try:
        test_health()
        test_analyze_success()
        test_analyze_error()
        test_get_report()
        
        print("=" * 60)
        print("All tests completed!")
        print("=" * 60)
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to API. Make sure the server is running:")
        print("  python3 manage.py runserver 0.0.0.0:8000")
    except Exception as e:
        print(f"ERROR: {e}")
