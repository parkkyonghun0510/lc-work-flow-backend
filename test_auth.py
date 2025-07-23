#!/usr/bin/env python3

"""
Authentication Test Script for LC Work Flow Backend

This script tests the authentication endpoints by attempting to login with
the default test users created by setup_backend.py.
"""

import requests
import json
import sys
import os
from urllib.parse import urljoin

# Configuration
BASE_URL = "http://localhost:8000"
API_V1_STR = "/api/v1"
TOKEN_URL = urljoin(BASE_URL, f"{API_V1_STR}/auth/token")

# Test users from setup_backend.py
TEST_USERS = [
    {"username": "admin", "password": "admin123", "role": "Admin"},
    {"username": "testuser", "password": "testpassword", "role": "Manager"},
    {"username": "loanofficer", "password": "loan123", "role": "Loan Officer"}
]

def test_auth(username, password):
    """Test authentication for a user"""
    print(f"\nTesting authentication for user: {username}")
    
    # Prepare login data
    login_data = {
        "username": username,
        "password": password
    }
    
    try:
        # Make the request
        response = requests.post(
            TOKEN_URL,
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        # Check response
        if response.status_code == 200:
            token_data = response.json()
            print(f"✅ Authentication successful!")
            print(f"   Token type: {token_data.get('token_type')}")
            print(f"   Access token received: {token_data.get('access_token')[:20]}...")
            if 'refresh_token' in token_data:
                print(f"   Refresh token received: {token_data.get('refresh_token')[:20]}...")
            return True, token_data
        else:
            print(f"❌ Authentication failed with status code: {response.status_code}")
            print(f"   Response: {response.text}")
            return False, None
    except Exception as e:
        print(f"❌ Error during authentication: {str(e)}")
        return False, None

def test_protected_endpoint(token):
    """Test accessing a protected endpoint"""
    print("\nTesting access to protected endpoint...")
    
    # Choose a protected endpoint
    users_url = urljoin(BASE_URL, f"{API_V1_STR}/users/")
    
    try:
        # Make the request with the token
        response = requests.get(
            users_url,
            headers={
                "Authorization": f"Bearer {token['access_token']}"
            }
        )
        
        # Check response
        if response.status_code == 200:
            print(f"✅ Successfully accessed protected endpoint!")
            data = response.json()
            print(f"   Retrieved {len(data)} users")
            return True
        else:
            print(f"❌ Failed to access protected endpoint with status code: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error accessing protected endpoint: {str(e)}")
        return False

def main():
    print("===== LC Work Flow Backend - Authentication Test =====\n")
    
    # Check if server is running
    try:
        health_url = urljoin(BASE_URL, "/api/health")
        response = requests.get(health_url)
        if response.status_code != 200:
            print(f"❌ Server health check failed with status code: {response.status_code}")
            print("   Make sure the server is running at", BASE_URL)
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ Could not connect to server at {BASE_URL}")
        print("   Make sure the server is running")
        return False
    
    print(f"✅ Server is running at {BASE_URL}")
    
    # Test authentication for each user
    successful_auths = 0
    for user in TEST_USERS:
        success, token_data = test_auth(user["username"], user["password"])
        if success:
            successful_auths += 1
            # Test protected endpoint with the first successful token
            if successful_auths == 1:
                test_protected_endpoint(token_data)
    
    # Summary
    print(f"\n===== Authentication Test Summary =====")
    print(f"Total users tested: {len(TEST_USERS)}")
    print(f"Successful authentications: {successful_auths}")
    print(f"Failed authentications: {len(TEST_USERS) - successful_auths}")
    
    if successful_auths == len(TEST_USERS):
        print("\n✅ All authentication tests passed!")
        return True
    else:
        print(f"\n❌ Some authentication tests failed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)