"""
Test login and profile verification for the created account
"""

import requests
import json

BASE_URL = "http://localhost:5000"

# Account credentials
credentials = {
    "username": "testuser_complete",
    "password": "Test123456!"
}

def test_account():
    """Test login and profile retrieval"""
    try:
        print("=" * 60)
        print("Testing Account Login and Profile")
        print("=" * 60)
        
        # Login
        print("\n1. Testing Login...")
        login_response = requests.post(
            f"{BASE_URL}/api/login",
            json=credentials,
            headers={"Content-Type": "application/json"}
        )
        
        if login_response.status_code == 200:
            login_data = login_response.json()
            token = login_data.get('access_token')
            print(f"   [SUCCESS] Login successful!")
            print(f"   User: {login_data.get('user', {}).get('username', 'N/A')}")
            print(f"   Token: {token[:50]}...")
            
            # Test profile retrieval
            print("\n2. Testing Profile Retrieval...")
            profile_response = requests.get(
                f"{BASE_URL}/api/user/profile",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }
            )
            
            if profile_response.status_code == 200:
                profile_data = profile_response.json()
                print(f"   [SUCCESS] Profile retrieved successfully!")
                print(f"\n   Profile Details:")
                print(f"   - Age: {profile_data.get('age', 'N/A')}")
                print(f"   - Gender: {profile_data.get('gender', 'N/A')}")
                print(f"   - Height: {profile_data.get('height', 'N/A')} cm")
                print(f"   - Weight: {profile_data.get('weight', 'N/A')} kg")
                print(f"   - Training Level: {profile_data.get('training_level', 'N/A')}")
                print(f"   - Exercise History: {profile_data.get('exercise_history_years', 'N/A')} years")
                print(f"   - Fitness Goals: {profile_data.get('fitness_goals', [])}")
                print(f"   - Injuries: {profile_data.get('injuries', [])}")
                print(f"   - Medical Conditions: {profile_data.get('medical_conditions', [])}")
                print(f"   - Gym Access: {profile_data.get('gym_access', False)}")
                print(f"   - Equipment: {profile_data.get('equipment_access', [])}")
                print(f"   - Workout Days/Week: {profile_data.get('workout_days_per_week', 'N/A')}")
                print(f"   - Preferred Time: {profile_data.get('preferred_workout_time', 'N/A')}")
                
                print("\n" + "=" * 60)
                print("[SUCCESS] All tests passed!")
                print("=" * 60)
                print("\nAccount Credentials:")
                print(f"   Username: {credentials['username']}")
                print(f"   Password: {credentials['password']}")
                print("\nYou can now use these credentials to test the frontend.")
                return True
            else:
                print(f"   [ERROR] Profile retrieval failed: {profile_response.status_code}")
                print(f"   Response: {profile_response.text}")
                return False
        else:
            print(f"   [ERROR] Login failed: {login_response.status_code}")
            print(f"   Response: {login_response.text}")
            return False
            
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_account()

