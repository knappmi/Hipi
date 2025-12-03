#!/usr/bin/env python3
"""Test script to verify the application is running correctly"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000"
WEB_URL = "http://localhost:5000"

def test_endpoint(url, description):
    """Test an endpoint and return success status"""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"[PASS] {description}: OK")
            try:
                data = response.json()
                print(f"  Response: {json.dumps(data, indent=2)}")
            except:
                print(f"  Response: {response.text[:100]}")
            return True
        else:
            print(f"[FAIL] {description}: FAILED (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"[ERROR] {description}: ERROR - {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("Testing Home Assistant Platform Application")
    print("=" * 60)
    print()
    
    tests_passed = 0
    tests_total = 0
    
    # Test API endpoints
    print("API Endpoints:")
    print("-" * 60)
    
    tests_total += 1
    if test_endpoint(f"{BASE_URL}/", "Root endpoint"):
        tests_passed += 1
    
    tests_total += 1
    if test_endpoint(f"{BASE_URL}/health", "Health check"):
        tests_passed += 1
    
    tests_total += 1
    if test_endpoint(f"{BASE_URL}/api/v1/status", "API status"):
        tests_passed += 1
    
    tests_total += 1
    if test_endpoint(f"{BASE_URL}/api/v1/plugins", "Plugins list"):
        tests_passed += 1
    
    # Test Web UI
    print()
    print("Web UI:")
    print("-" * 60)
    
    tests_total += 1
    try:
        response = requests.get(WEB_URL, timeout=5)
        if response.status_code == 200:
            print(f"[PASS] Web UI: OK (Status: {response.status_code})")
            tests_passed += 1
        else:
            print(f"[FAIL] Web UI: FAILED (Status: {response.status_code})")
    except Exception as e:
        print(f"[ERROR] Web UI: ERROR - {e}")
    
    # Summary
    print()
    print("=" * 60)
    print(f"Tests: {tests_passed}/{tests_total} passed")
    print("=" * 60)
    
    if tests_passed == tests_total:
        print("[SUCCESS] All tests passed!")
        return 0
    else:
        print("[FAILURE] Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())

