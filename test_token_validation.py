"""
Test script to validate JWT token and check if it matches the backend secret
"""

import requests
import json
import jwt
import os
from dotenv import load_dotenv

load_dotenv('backend/.env')

BASE_URL = "http://localhost:5000"

# Test credentials
credentials = {
    "username": "testuser_complete",
    "password": "Test123456!"
}

def test_token():
    """Test token creation and validation"""
    try:
        print("=" * 60)
        print("Testing JWT Token Validation")
        print("=" * 60)
        
        # Step 1: Login to get a fresh token
        print("\n1. Logging in to get fresh token...")
        login_response = requests.post(
            f"{BASE_URL}/api/login",
            json=credentials,
            headers={"Content-Type": "application/json"}
        )
        
        if login_response.status_code != 200:
            print(f"   [ERROR] Login failed: {login_response.status_code}")
            print(f"   Response: {login_response.text}")
            return False
        
        login_data = login_response.json()
        token = login_data.get('access_token')
        print(f"   [SUCCESS] Login successful!")
        print(f"   Token (first 50 chars): {token[:50]}...")
        print(f"   Token length: {len(token)}")
        
        # Step 2: Try to decode the token (without verification to see what's in it)
        try:
            decoded = jwt.decode(token, options={"verify_signature": False})
            print(f"\n2. Token contents (without verification):")
            print(f"   User ID: {decoded.get('sub')}")
            print(f"   Expires: {decoded.get('exp')}")
            print(f"   Issued at: {decoded.get('iat')}")
        except Exception as e:
            print(f"   [ERROR] Could not decode token: {e}")
        
        # Step 3: Get JWT_SECRET_KEY from backend
        jwt_secret = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
        print(f"\n3. Backend JWT_SECRET_KEY:")
        print(f"   Secret key (first 20 chars): {jwt_secret[:20]}...")
        print(f"   Secret key length: {len(jwt_secret)}")
        
        # Step 4: Try to verify token with the secret
        try:
            decoded_verified = jwt.decode(token, jwt_secret, algorithms=["HS256"])
            print(f"\n4. Token verification:")
            print(f"   [SUCCESS] Token is valid with current secret key!")
            print(f"   User ID: {decoded_verified.get('sub')}")
        except jwt.ExpiredSignatureError:
            print(f"\n4. Token verification:")
            print(f"   [ERROR] Token has expired")
        except jwt.InvalidTokenError as e:
            print(f"\n4. Token verification:")
            print(f"   [ERROR] Token is invalid: {e}")
            print(f"   This means the token was created with a different secret key!")
        
        # Step 5: Test with /api/user endpoint
        print(f"\n5. Testing /api/user endpoint...")
        user_response = requests.get(
            f"{BASE_URL}/api/user",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
        )
        
        if user_response.status_code == 200:
            print(f"   [SUCCESS] /api/user endpoint works!")
            user_data = user_response.json()
            print(f"   Username: {user_data.get('username')}")
        else:
            print(f"   [ERROR] /api/user endpoint failed: {user_response.status_code}")
            print(f"   Response: {user_response.text}")
        
        # Step 6: Test with /api/user/profile endpoint
        print(f"\n6. Testing /api/user/profile endpoint...")
        profile_response = requests.get(
            f"{BASE_URL}/api/user/profile",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
        )
        
        if profile_response.status_code == 200:
            print(f"   [SUCCESS] /api/user/profile endpoint works!")
            profile_data = profile_response.json()
            print(f"   Profile data keys: {list(profile_data.keys())}")
        else:
            print(f"   [ERROR] /api/user/profile endpoint failed: {profile_response.status_code}")
            print(f"   Response: {profile_response.text}")
            error_data = profile_response.json() if profile_response.text else {}
            print(f"   Error message: {error_data.get('error', 'N/A')}")
            print(f"   Error details: {error_data.get('message', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_token()





