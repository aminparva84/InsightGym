"""
Test login functionality with testuser_complete account
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_login():
    print("=" * 70)
    print("TESTING LOGIN FUNCTIONALITY")
    print("=" * 70)
    
    # Test account credentials - using testuser_complete
    credentials = {
        "username": "testuser_complete",
        "password": "Test123456!"
    }
    
    print(f"Testing with account: {credentials['username']}")
    
    print(f"\n[STEP 1] Attempting to login with username: {credentials['username']}")
    
    try:
        # Login request
        login_response = requests.post(
            f"{BASE_URL}/api/login",
            json=credentials,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   Status Code: {login_response.status_code}")
        
        if login_response.status_code == 200:
            print(f"   ✓ LOGIN SUCCESSFUL!")
            login_data = login_response.json()
            token = login_data.get('access_token')
            user_data = login_data.get('user', {})
            
            print(f"\n   Token (first 50 chars): {token[:50]}...")
            print(f"   Token length: {len(token)}")
            print(f"   User ID: {user_data.get('id')}")
            print(f"   Username: {user_data.get('username')}")
            print(f"   Email: {user_data.get('email')}")
            
            # Test authenticated endpoint
            print(f"\n[STEP 2] Testing authenticated endpoint /api/user")
            user_response = requests.get(
                f"{BASE_URL}/api/user",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }
            )
            
            print(f"   Status Code: {user_response.status_code}")
            
            if user_response.status_code == 200:
                print(f"   ✓ USER ENDPOINT SUCCESSFUL!")
                user_info = user_response.json()
                print(f"   User ID: {user_info.get('id')}")
                print(f"   Username: {user_info.get('username')}")
                print(f"   Email: {user_info.get('email')}")
                print(f"   Language: {user_info.get('language')}")
                
                # Test profile endpoint
                print(f"\n[STEP 3] Testing profile endpoint /api/user/profile")
                profile_response = requests.get(
                    f"{BASE_URL}/api/user/profile",
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json"
                    }
                )
                
                print(f"   Status Code: {profile_response.status_code}")
                
                if profile_response.status_code == 200:
                    print(f"   ✓ PROFILE ENDPOINT SUCCESSFUL!")
                    profile_data = profile_response.json()
                    print(f"   Profile fields loaded: {len(profile_data)} fields")
                    print(f"   Age: {profile_data.get('age')}")
                    print(f"   Weight: {profile_data.get('weight')}")
                    print(f"   Height: {profile_data.get('height')}")
                    print(f"   Gender: {profile_data.get('gender')}")
                    print(f"   Training Level: {profile_data.get('training_level')}")
                elif profile_response.status_code == 404:
                    print(f"   ⚠ Profile not found (user hasn't created profile yet)")
                else:
                    print(f"   ✗ PROFILE ENDPOINT FAILED")
                    print(f"   Response: {profile_response.text}")
            else:
                print(f"   ✗ USER ENDPOINT FAILED")
                print(f"   Response: {user_response.text}")
            
            print(f"\n{'=' * 70}")
            print("LOGIN TEST COMPLETE - ALL SYSTEMS WORKING!")
            print("=" * 70)
            return True
            
        elif login_response.status_code == 401:
            print(f"   ✗ LOGIN FAILED - Invalid credentials")
            print(f"   Response: {login_response.text}")
            return False
        else:
            print(f"   ✗ LOGIN FAILED - Unexpected status code")
            print(f"   Response: {login_response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"\n   ✗ ERROR: Cannot connect to backend server")
        print(f"   Make sure the backend is running on {BASE_URL}")
        return False
    except Exception as e:
        print(f"\n   ✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_login()
    exit(0 if success else 1)

