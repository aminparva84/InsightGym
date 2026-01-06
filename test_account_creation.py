"""
Script to create a test account with complete profile details
Run this script to create a test account for testing purposes
"""

import requests
import json

# Backend API URL
BASE_URL = "http://localhost:5000"

# Complete test account data
test_account = {
    "username": "testuser_complete",
    "email": "testuser_complete@example.com",
    "password": "Test123456!",
    "language": "en",
    "profile": {
        # Basic Information
        "age": 28,
        "gender": "male",
        "height": 180.0,  # cm
        "weight": 75.5,   # kg
        "training_level": "intermediate",
        "exercise_history_years": 3,
        "exercise_history_description": "I have been working out for 3 years, focusing on strength training and cardio. I go to the gym regularly and have experience with free weights and machines.",
        
        # Training Goals (multiple selections)
        "fitness_goals": [
            "weight_loss",
            "muscle_gain",
            "strength",
            "endurance"
        ],
        
        # Injuries
        "injuries": ["knee", "lower_back"],
        "injury_details": "I have a minor knee injury from running and occasional lower back pain from heavy lifting. I need to be careful with squats and deadlifts.",
        
        # Medical Conditions
        "medical_conditions": ["high_blood_pressure"],
        "medical_condition_details": "I have mild high blood pressure that is controlled with medication. I need to monitor my heart rate during intense workouts.",
        
        # Training Conditions
        "gym_access": True,
        "equipment_access": ["machine", "dumbbells", "barbell", "cable"],
        "home_equipment": [],
        "workout_days_per_week": 5,
        "preferred_workout_time": "evening",
        "preferred_intensity": "medium"
    }
}

def create_test_account():
    """Create a test account with complete profile"""
    try:
        print("=" * 60)
        print("Creating Test Account with Complete Profile")
        print("=" * 60)
        
        # Register the account
        response = requests.post(
            f"{BASE_URL}/api/register",
            json=test_account,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code in [200, 201]:
            data = response.json()
            print("\n[SUCCESS] Account created successfully!")
            print(f"\nAccount Credentials:")
            print(f"   Username: {test_account['username']}")
            print(f"   Email: {test_account['email']}")
            print(f"   Password: {test_account['password']}")
            print(f"\nAccess Token: {data.get('access_token', 'N/A')[:50]}...")
            print(f"\nUser ID: {data.get('user', {}).get('id', 'N/A')}")
            
            # Test login
            print("\n" + "=" * 60)
            print("Testing Login...")
            print("=" * 60)
            
            login_response = requests.post(
                f"{BASE_URL}/api/login",
                json={
                    "username": test_account['username'],
                    "password": test_account['password']
                },
                headers={"Content-Type": "application/json"}
            )
            
            if login_response.status_code == 200:
                login_data = login_response.json()
                print("[SUCCESS] Login successful!")
                print(f"Login Token: {login_data.get('access_token', 'N/A')[:50]}...")
                
                # Test profile retrieval
                print("\n" + "=" * 60)
                print("Testing Profile Retrieval...")
                print("=" * 60)
                
                token = login_data.get('access_token')
                profile_response = requests.get(
                    f"{BASE_URL}/api/user/profile",
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json"
                    }
                )
                
                if profile_response.status_code == 200:
                    profile_data = profile_response.json()
                    print("[SUCCESS] Profile retrieved successfully!")
                    print(f"\nProfile Summary:")
                    print(f"   Age: {profile_data.get('age', 'N/A')}")
                    print(f"   Gender: {profile_data.get('gender', 'N/A')}")
                    print(f"   Height: {profile_data.get('height', 'N/A')} cm")
                    print(f"   Weight: {profile_data.get('weight', 'N/A')} kg")
                    print(f"   Training Level: {profile_data.get('training_level', 'N/A')}")
                    print(f"   Exercise History: {profile_data.get('exercise_history_years', 'N/A')} years")
                    print(f"   Fitness Goals: {profile_data.get('fitness_goals', [])}")
                    print(f"   Injuries: {profile_data.get('injuries', [])}")
                    print(f"   Medical Conditions: {profile_data.get('medical_conditions', [])}")
                    print(f"   Gym Access: {profile_data.get('gym_access', False)}")
                    print(f"   Equipment: {profile_data.get('equipment_access', [])}")
                    print(f"   Workout Days/Week: {profile_data.get('workout_days_per_week', 'N/A')}")
                    print(f"   Preferred Time: {profile_data.get('preferred_workout_time', 'N/A')}")
                else:
                    print(f"[ERROR] Profile retrieval failed: {profile_response.status_code}")
                    print(f"   Response: {profile_response.text}")
            else:
                print(f"[ERROR] Login failed: {login_response.status_code}")
                print(f"   Response: {login_response.text}")
            
            return True
        else:
            print(f"[ERROR] Account creation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("[ERROR] Could not connect to backend server.")
        print("   Make sure the backend is running on http://localhost:5000")
        return False
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\nStarting Test Account Creation...\n")
    success = create_test_account()
    
    if success:
        print("\n" + "=" * 60)
        print("[SUCCESS] Test Account Created Successfully!")
        print("=" * 60)
        print("\nUse these credentials to test the application:")
        print(f"   Username: {test_account['username']}")
        print(f"   Password: {test_account['password']}")
        print("\nNext steps:")
        print("   1. Open the frontend application")
        print("   2. Log in with the credentials above")
        print("   3. Navigate to Dashboard -> Profile")
        print("   4. Verify all profile data is displayed correctly")
        print("   5. Test navigation between pages to ensure user stays logged in")
    else:
        print("\n" + "=" * 60)
        print("[ERROR] Test Account Creation Failed")
        print("=" * 60)
        print("\nTroubleshooting:")
        print("   1. Make sure the backend server is running")
        print("   2. Check if the account already exists (username or email)")
        print("   3. Check backend logs for errors")

