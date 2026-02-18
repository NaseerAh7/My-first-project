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

def test_health_endpoint():
    """Test GET /api/health returns status and db check"""
    print("\n🔍 Testing GET /api/health (health check endpoint)")
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'ok' and data.get('db') == 'ok':
                print("✅ Health endpoint working correctly - MongoDB connection OK")
                return True
            else:
                print(f"❌ Health endpoint returned unexpected response: {data}")
                return False
        else:
            print(f"❌ Health endpoint failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health endpoint test failed: {str(e)}")
        return False

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

# JWT Authentication Tests

def test_admin_login_valid():
    """Test POST /api/auth/login with valid credentials"""
    print("\n🔍 Testing POST /api/auth/login (valid credentials)")
    
    admin_email = backend_env.get('ADMIN_EMAIL')
    admin_password = backend_env.get('ADMIN_PASSWORD')
    
    if not admin_email or not admin_password:
        print("❌ ADMIN_EMAIL/ADMIN_PASSWORD not found in backend/.env")
        return False, None
    
    login_data = {
        "email": admin_email,
        "password": admin_password
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Check required fields
            required_fields = ['access_token', 'token_type', 'expires_in']
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                print(f"❌ Missing required fields: {missing_fields}")
                return False, None
            
            if data.get('token_type') != 'bearer':
                print(f"❌ Expected token_type='bearer', got '{data.get('token_type')}'")
                return False, None
            
            access_token = data.get('access_token')
            if not access_token:
                print("❌ No access_token in response")
                return False, None
            
            print("✅ Valid login working correctly")
            return True, access_token
        else:
            print(f"❌ Expected 200, got {response.status_code}")
            return False, None
            
    except Exception as e:
        print(f"❌ Valid login test failed: {str(e)}")
        return False, None

def test_admin_login_invalid():
    """Test POST /api/auth/login with invalid password"""
    print("\n🔍 Testing POST /api/auth/login (invalid password)")
    
    admin_email = backend_env.get('ADMIN_EMAIL')
    
    if not admin_email:
        print("❌ ADMIN_EMAIL not found in backend/.env")
        return False
    
    login_data = {
        "email": admin_email,
        "password": "wrong_password_123"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 401:
            print("✅ Invalid password rejected - working correctly")
            return True
        else:
            print(f"❌ Expected 401, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Invalid login test failed: {str(e)}")
        return False

def test_recent_contacts_no_auth():
    """Test GET /api/contact/recent without Authorization header"""
    print("\n🔍 Testing GET /api/contact/recent (no Authorization header)")
    
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

def test_recent_contacts_invalid_token():
    """Test GET /api/contact/recent with invalid Bearer token"""
    print("\n🔍 Testing GET /api/contact/recent (invalid Bearer token)")
    
    try:
        headers = {"Authorization": "Bearer invalid_token_123"}
        response = requests.get(f"{API_BASE_URL}/contact/recent", headers=headers, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 401:
            print("✅ Invalid token rejected - working correctly")
            return True
        else:
            print(f"❌ Expected 401, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Invalid token test failed: {str(e)}")
        return False

def test_recent_contacts_legacy_auth():
    """Test GET /api/contact/recent with legacy x-admin-key (should be rejected)"""
    print("\n🔍 Testing GET /api/contact/recent (legacy x-admin-key - should be rejected)")
    
    try:
        headers = {"x-admin-key": ADMIN_API_KEY}
        response = requests.get(f"{API_BASE_URL}/contact/recent", headers=headers, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 401:
            print("✅ Legacy x-admin-key rejected - JWT migration working correctly")
            return True
        else:
            print(f"❌ Expected 401 (legacy auth should be rejected), got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Legacy auth test failed: {str(e)}")
        return False

def test_recent_contacts_valid_jwt():
    """Test GET /api/contact/recent with valid Bearer token"""
    print("\n🔍 Testing GET /api/contact/recent (valid Bearer token)")
    
    # First get a valid token
    login_success, access_token = test_admin_login_valid()
    if not login_success or not access_token:
        print("❌ Could not get valid access token for testing")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(f"{API_BASE_URL}/contact/recent", headers=headers, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Check for paginated format {items, next_cursor}
            if isinstance(data, dict) and 'items' in data and 'next_cursor' in data:
                items = data['items']
                next_cursor = data['next_cursor']
                
                print(f"✅ JWT auth + paginated format working - returned {len(items)} submissions")
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
        print(f"❌ Valid JWT test failed: {str(e)}")
        return False

def test_cursor_pagination():
    """Test cursor pagination behavior with JWT auth - call once to get next_cursor, then call again with cursor"""
    print("\n🔍 Testing GET /api/contact/recent (cursor pagination behavior with JWT)")
    
    # First get a valid token
    login_success, access_token = test_admin_login_valid()
    if not login_success or not access_token:
        print("❌ Could not get valid access token for pagination testing")
        return False
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        # First call - get initial page with limit=2 to ensure we get a cursor
        print("Step 1: Getting first page with limit=2")
        response1 = requests.get(f"{API_BASE_URL}/contact/recent?limit=2", headers=headers, timeout=10)
        
        if response1.status_code != 200:
            print(f"❌ First call failed with status {response1.status_code}")
            return False
        
        data1 = response1.json()
        print(f"First page response: {data1}")
        
        if not isinstance(data1, dict) or 'items' not in data1 or 'next_cursor' not in data1:
            print("❌ First call didn't return paginated format")
            return False
        
        first_items = data1['items']
        next_cursor = data1['next_cursor']
        
        print(f"First page: {len(first_items)} items, next_cursor: {next_cursor}")
        
        # If we have a next_cursor, test pagination
        if next_cursor:
            print(f"\nStep 2: Getting next page with cursor={next_cursor}")
            response2 = requests.get(
                f"{API_BASE_URL}/contact/recent?cursor={next_cursor}&limit=2", 
                headers=headers, 
                timeout=10
            )
            
            if response2.status_code != 200:
                print(f"❌ Second call failed with status {response2.status_code}")
                return False
            
            data2 = response2.json()
            print(f"Second page response: {data2}")
            
            if not isinstance(data2, dict) or 'items' not in data2 or 'next_cursor' not in data2:
                print("❌ Second call didn't return paginated format")
                return False
            
            second_items = data2['items']
            second_cursor = data2['next_cursor']
            
            print(f"Second page: {len(second_items)} items, next_cursor: {second_cursor}")
            
            # Check for no duplicates between pages
            first_ids = {item['id'] for item in first_items}
            second_ids = {item['id'] for item in second_items}
            
            if first_ids & second_ids:  # Intersection should be empty
                print(f"❌ Found duplicate items between pages: {first_ids & second_ids}")
                return False
            
            # Check that second page items are older (created_at should be less than first page)
            if first_items and second_items:
                first_latest = first_items[-1]['created_at']  # Last item of first page
                second_earliest = second_items[0]['created_at']  # First item of second page
                
                if first_latest <= second_earliest:
                    print("❌ Second page items are not older than first page items")
                    return False
            
            print("✅ Cursor pagination working correctly:")
            print("  - No duplicates between pages")
            print("  - Second page contains older items")
            print("  - Cursor advances properly")
            
        else:
            print("✅ No next_cursor (all items fit in first page) - pagination working correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ Cursor pagination test failed: {str(e)}")
        return False

def test_recent_contacts_limit_bounds():
    """Test GET /api/contact/recent limit parameter bounds with JWT auth"""
    print("\n🔍 Testing GET /api/contact/recent (limit bounds with JWT auth)")
    
    # First get a valid token
    login_success, access_token = test_admin_login_valid()
    if not login_success or not access_token:
        print("❌ Could not get valid access token for limit bounds testing")
        return False
    
    headers = {"Authorization": f"Bearer {access_token}"}
    all_passed = True
    
    # Test limit=1
    try:
        response = requests.get(f"{API_BASE_URL}/contact/recent?limit=1", headers=headers, timeout=10)
        print(f"\nLimit=1 - Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and 'items' in data:
                items = data['items']
                if len(items) <= 1:
                    print(f"✅ Limit=1 working correctly (returned {len(items)} items)")
                else:
                    print(f"❌ Limit=1 returned {len(items)} items")
                    all_passed = False
            else:
                print("❌ Expected paginated format {items, next_cursor}")
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
            if isinstance(data, dict) and 'items' in data:
                items = data['items']
                if len(items) <= 100:
                    print(f"✅ Limit=999 capped correctly (returned {len(items)} items)")
                else:
                    print(f"❌ Limit=999 returned {len(items)} items (should be max 100)")
                    all_passed = False
            else:
                print("❌ Expected paginated format {items, next_cursor}")
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
    print("🚀 Starting Backend API Tests - Health Check + Auth Sanity Check")
    print(f"Backend URL: {API_BASE_URL}")
    
    tests = [
        ("Health Endpoint", test_health_endpoint),
        ("Root Endpoint", test_root_endpoint),
        ("Contact Submission (Valid)", test_contact_submission_valid),
        ("Admin Login (Valid Credentials)", lambda: test_admin_login_valid()[0]),  # Only return success boolean
        ("Recent Contacts (Valid JWT Bearer Token)", test_recent_contacts_valid_jwt),
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