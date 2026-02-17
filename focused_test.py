#!/usr/bin/env python3
"""
Focused test for the specific requirements from the review request
"""

import requests
import json
import os
from pathlib import Path

# Load environment variables
def load_env_file(file_path):
    env_vars = {}
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    value = value.strip('"\'')
                    env_vars[key] = value
    return env_vars

frontend_env = load_env_file('/app/frontend/.env')
backend_env = load_env_file('/app/backend/.env')

BACKEND_URL = frontend_env.get('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE_URL = f"{BACKEND_URL}/api"
ADMIN_API_KEY = backend_env.get('ADMIN_API_KEY', '')

print("🎯 FOCUSED TESTING - Review Request Requirements")
print("=" * 60)

def test_invalid_email_422():
    """Test POST /api/contact should return 422 for invalid email"""
    print("\n🔍 Testing: POST /api/contact should return 422 for invalid email")
    
    test_data = {
        "name": "Test User",
        "email": "invalid-email-format",
        "message": "This should fail validation"
    }
    
    response = requests.post(
        f"{API_BASE_URL}/contact",
        json=test_data,
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 422:
        print("✅ REQUIREMENT MET: Invalid email returns 422")
        return True
    else:
        print(f"❌ REQUIREMENT FAILED: Expected 422, got {response.status_code}")
        return False

def test_valid_email_201_and_persists():
    """Test valid email still returns 201 and persists"""
    print("\n🔍 Testing: Valid email returns 201 and persists")
    
    test_data = {
        "name": "Sarah Johnson",
        "email": "sarah.johnson@company.com",
        "message": "I would like to discuss a potential project collaboration."
    }
    
    # Submit the contact
    response = requests.post(
        f"{API_BASE_URL}/contact",
        json=test_data,
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    
    print(f"POST Status Code: {response.status_code}")
    
    if response.status_code != 201:
        print(f"❌ REQUIREMENT FAILED: Expected 201, got {response.status_code}")
        return False
    
    submission_data = response.json()
    submission_id = submission_data.get('id')
    print(f"Created submission with ID: {submission_id}")
    
    # Verify persistence by fetching recent submissions
    headers = {"x-admin-key": ADMIN_API_KEY}
    response = requests.get(f"{API_BASE_URL}/contact/recent", headers=headers, timeout=10)
    
    if response.status_code != 200:
        print(f"❌ PERSISTENCE CHECK FAILED: Could not fetch recent submissions")
        return False
    
    recent_submissions = response.json()
    
    # Check if our submission is in the recent list
    found = False
    for submission in recent_submissions:
        if submission.get('id') == submission_id:
            found = True
            print(f"✅ PERSISTENCE VERIFIED: Submission found in database")
            break
    
    if found:
        print("✅ REQUIREMENT MET: Valid email returns 201 and persists")
        return True
    else:
        print("❌ REQUIREMENT FAILED: Submission not found in database")
        return False

def test_recent_auth_and_limit():
    """Test GET /api/contact/recent auth and limit behavior still works"""
    print("\n🔍 Testing: GET /api/contact/recent auth and limit behavior")
    
    # Test 1: No auth should return 401
    response = requests.get(f"{API_BASE_URL}/contact/recent", timeout=10)
    if response.status_code != 401:
        print(f"❌ AUTH TEST FAILED: Expected 401 without auth, got {response.status_code}")
        return False
    print("✅ Auth required - working correctly")
    
    # Test 2: Wrong auth should return 401
    headers = {"x-admin-key": "wrong_key"}
    response = requests.get(f"{API_BASE_URL}/contact/recent", headers=headers, timeout=10)
    if response.status_code != 401:
        print(f"❌ AUTH TEST FAILED: Expected 401 with wrong auth, got {response.status_code}")
        return False
    print("✅ Wrong auth rejected - working correctly")
    
    # Test 3: Valid auth should work
    headers = {"x-admin-key": ADMIN_API_KEY}
    response = requests.get(f"{API_BASE_URL}/contact/recent", headers=headers, timeout=10)
    if response.status_code != 200:
        print(f"❌ AUTH TEST FAILED: Expected 200 with valid auth, got {response.status_code}")
        return False
    print("✅ Valid auth working correctly")
    
    # Test 4: Limit parameter should work
    response = requests.get(f"{API_BASE_URL}/contact/recent?limit=1", headers=headers, timeout=10)
    if response.status_code != 200:
        print(f"❌ LIMIT TEST FAILED: Expected 200 with limit, got {response.status_code}")
        return False
    
    data = response.json()
    if len(data) > 1:
        print(f"❌ LIMIT TEST FAILED: Expected max 1 item, got {len(data)}")
        return False
    print("✅ Limit parameter working correctly")
    
    print("✅ REQUIREMENT MET: GET /api/contact/recent auth and limit behavior works")
    return True

def main():
    """Run focused tests for review request requirements"""
    
    tests = [
        ("Invalid Email Returns 422", test_invalid_email_422),
        ("Valid Email Returns 201 and Persists", test_valid_email_201_and_persists),
        ("Recent Contacts Auth and Limit", test_recent_auth_and_limit),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {str(e)}")
            results[test_name] = False
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 FOCUSED TEST SUMMARY")
    print(f"{'='*60}")
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nOverall: {passed}/{total} requirements met")
    
    if passed == total:
        print("🎉 All review request requirements satisfied!")
        return 0
    else:
        print("⚠️  Some requirements not met!")
        return 1

if __name__ == "__main__":
    exit(main())