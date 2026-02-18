#!/usr/bin/env python3
"""
Backend API Testing Script
Tests the contact submission and admin endpoints
"""

import requests
import json
from datetime import datetime
import sys
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
                    # Remove quotes if present
                    value = value.strip('"\'')
                    env_vars[key] = value
    return env_vars

# Load frontend and backend env vars
frontend_env = load_env_file('/app/frontend/.env')
backend_env = load_env_file('/app/backend/.env')

# Get URLs and keys
BACKEND_URL = frontend_env.get('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE_URL = f"{BACKEND_URL}/api"
ADMIN_API_KEY = backend_env.get('ADMIN_API_KEY', '')

print(f"Testing backend at: {API_BASE_URL}")
print(f"Admin API Key: {'*' * len(ADMIN_API_KEY) if ADMIN_API_KEY else 'NOT SET'}")
print("=" * 60)

def test_root_endpoint():
    """Test GET /api/ returns Hello World"""
    print("\n🔍 Testing GET /api/ (root endpoint)")
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('message') == 'Hello World':
                print("✅ Root endpoint working correctly")
                return True
            else:
                print("❌ Root endpoint returned unexpected message")
                return False
        else:
            print(f"❌ Root endpoint failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Root endpoint test failed: {str(e)}")
        return False

def test_contact_submission_valid():
    """Test POST /api/contact with valid data"""
    print("\n🔍 Testing POST /api/contact (valid submission)")
    
    test_data = {
        "name": "John Smith",
        "email": "john.smith@example.com", 
        "message": "Hello, I'm interested in your portfolio work. Would love to discuss potential collaboration opportunities."
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/contact",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 201:
            data = response.json()
            # Check required fields
            required_fields = ['id', 'name', 'email', 'message', 'created_at']
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                print(f"❌ Missing required fields: {missing_fields}")
                return False
            
            # Check if input data is echoed back
            if (data['name'] == test_data['name'] and 
                data['email'] == test_data['email'] and 
                data['message'] == test_data['message']):
                print("✅ Valid contact submission working correctly")
                return True
            else:
                print("❌ Input data not properly echoed back")
                return False
        else:
            print(f"❌ Expected 201, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Contact submission test failed: {str(e)}")
        return False

def test_contact_submission_missing_fields():
    """Test POST /api/contact with missing fields"""
    print("\n🔍 Testing POST /api/contact (missing fields validation)")
    
    test_cases = [
        {"email": "test@example.com", "message": "Missing name"},
        {"name": "John", "message": "Missing email"},
        {"name": "John", "email": "test@example.com"},  # Missing message
        {}  # All fields missing
    ]
    
    all_passed = True
    for i, test_data in enumerate(test_cases):
        print(f"\nTest case {i+1}: {test_data}")
        try:
            response = requests.post(
                f"{API_BASE_URL}/contact",
                json=test_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            print(f"Status Code: {response.status_code}")
            if response.status_code == 422:
                print("✅ Validation working correctly")
            else:
                print(f"❌ Expected 422, got {response.status_code}")
                print(f"Response: {response.text}")
                all_passed = False
                
        except Exception as e:
            print(f"❌ Test case {i+1} failed: {str(e)}")
            all_passed = False
    
    return all_passed

def test_contact_submission_invalid_email():
    """Test POST /api/contact with invalid email"""
    print("\n🔍 Testing POST /api/contact (invalid email validation)")
    
    test_data = {
        "name": "John Smith",
        "email": "invalid-email-format",
        "message": "Test message with invalid email"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/contact",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 422:
            print("✅ Email validation working correctly")
            return True
        else:
            print(f"❌ Expected 422 for invalid email, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Invalid email test failed: {str(e)}")
        return False

def test_recent_contacts_no_auth():
    """Test GET /api/contact/recent without authentication"""
    print("\n🔍 Testing GET /api/contact/recent (no auth header)")
    
    try:
        response = requests.get(f"{API_BASE_URL}/contact/recent", timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 401:
            print("✅ Authentication required - working correctly")
            return True
        else:
            print(f"❌ Expected 401, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ No auth test failed: {str(e)}")
        return False

def test_recent_contacts_wrong_auth():
    """Test GET /api/contact/recent with wrong authentication"""
    print("\n🔍 Testing GET /api/contact/recent (wrong auth key)")
    
    try:
        headers = {"x-admin-key": "wrong_key_123"}
        response = requests.get(f"{API_BASE_URL}/contact/recent", headers=headers, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 401:
            print("✅ Wrong auth key rejected - working correctly")
            return True
        else:
            print(f"❌ Expected 401, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Wrong auth test failed: {str(e)}")
        return False

def test_recent_contacts_valid_auth():
    """Test GET /api/contact/recent with valid authentication - NEW PAGINATED FORMAT"""
    print("\n🔍 Testing GET /api/contact/recent (valid auth - paginated format)")
    
    if not ADMIN_API_KEY:
        print("❌ ADMIN_API_KEY not found in backend/.env")
        return False
    
    try:
        headers = {"x-admin-key": ADMIN_API_KEY}
        response = requests.get(f"{API_BASE_URL}/contact/recent", headers=headers, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Check for new paginated format {items, next_cursor}
            if isinstance(data, dict) and 'items' in data and 'next_cursor' in data:
                items = data['items']
                next_cursor = data['next_cursor']
                
                print(f"✅ Paginated format working - returned {len(items)} submissions")
                print(f"Next cursor: {next_cursor}")
                
                # Check if items is an array
                if not isinstance(items, list):
                    print("❌ Items should be an array")
                    return False
                
                # Check if sorted by created_at desc (if we have multiple items)
                if len(items) > 1:
                    dates = [item.get('created_at') for item in items if 'created_at' in item]
                    if dates == sorted(dates, reverse=True):
                        print("✅ Results properly sorted by created_at desc")
                    else:
                        print("❌ Results not properly sorted by created_at desc")
                        return False
                
                return True
            else:
                print("❌ Expected paginated format {items, next_cursor}")
                print(f"Got keys: {list(data.keys()) if isinstance(data, dict) else 'not a dict'}")
                return False
        else:
            print(f"❌ Expected 200, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Valid auth test failed: {str(e)}")
        return False

def test_recent_contacts_limit_bounds():
    """Test GET /api/contact/recent limit parameter bounds"""
    print("\n🔍 Testing GET /api/contact/recent (limit bounds)")
    
    if not ADMIN_API_KEY:
        print("❌ ADMIN_API_KEY not found in backend/.env")
        return False
    
    headers = {"x-admin-key": ADMIN_API_KEY}
    all_passed = True
    
    # Test limit=1
    try:
        response = requests.get(f"{API_BASE_URL}/contact/recent?limit=1", headers=headers, timeout=10)
        print(f"\nLimit=1 - Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if len(data) <= 1:
                print("✅ Limit=1 working correctly")
            else:
                print(f"❌ Limit=1 returned {len(data)} items")
                all_passed = False
        else:
            print(f"❌ Limit=1 failed with status {response.status_code}")
            all_passed = False
    except Exception as e:
        print(f"❌ Limit=1 test failed: {str(e)}")
        all_passed = False
    
    # Test limit=999 (should cap at 100)
    try:
        response = requests.get(f"{API_BASE_URL}/contact/recent?limit=999", headers=headers, timeout=10)
        print(f"\nLimit=999 - Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if len(data) <= 100:
                print(f"✅ Limit=999 capped correctly (returned {len(data)} items)")
            else:
                print(f"❌ Limit=999 returned {len(data)} items (should be max 100)")
                all_passed = False
        else:
            print(f"❌ Limit=999 failed with status {response.status_code}")
            all_passed = False
    except Exception as e:
        print(f"❌ Limit=999 test failed: {str(e)}")
        all_passed = False
    
    return all_passed

def main():
    """Run all backend tests"""
    print("🚀 Starting Backend API Tests")
    print(f"Backend URL: {API_BASE_URL}")
    
    tests = [
        ("Root Endpoint", test_root_endpoint),
        ("Contact Submission (Valid)", test_contact_submission_valid),
        ("Contact Submission (Missing Fields)", test_contact_submission_missing_fields),
        ("Contact Submission (Invalid Email)", test_contact_submission_invalid_email),
        ("Recent Contacts (No Auth)", test_recent_contacts_no_auth),
        ("Recent Contacts (Wrong Auth)", test_recent_contacts_wrong_auth),
        ("Recent Contacts (Valid Auth)", test_recent_contacts_valid_auth),
        ("Recent Contacts (Limit Bounds)", test_recent_contacts_limit_bounds),
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
    print("📊 TEST SUMMARY")
    print(f"{'='*60}")
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())