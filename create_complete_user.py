"""
Create a new user account with complete profile details
"""

import requests
import json
import random
import string

BASE_URL = "http://localhost:5000"

def generate_username():
    """Generate a unique username"""
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"complete_user_{random_str}"

def create_complete_user():
    print("=" * 70)
    print("CREATING NEW USER WITH COMPLETE PROFILE")
    print("=" * 70)
    
    # Generate unique credentials
    username = generate_username()
    email = f"{username}@example.com"
    password = "Complete123456!"
    
    print(f"\n[STEP 1] Registering new user...")
    print(f"  Username: {username}")
    print(f"  Email: {email}")
    print(f"  Password: {password}")
    
    # Register user
    register_data = {
        "username": username,
        "email": email,
        "password": password
    }
    
    try:
        register_response = requests.post(
            f"{BASE_URL}/api/register",
            json=register_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"  Registration Status: {register_response.status_code}")
        
        if register_response.status_code not in [200, 201]:
            print(f"  Registration failed: {register_response.text}")
            return None
        
        print("  [OK] User registered successfully")
        
        # Login to get token
        print(f"\n[STEP 2] Logging in...")
        login_response = requests.post(
            f"{BASE_URL}/api/login",
            json={"username": username, "password": password},
            headers={"Content-Type": "application/json"}
        )
        
        if login_response.status_code != 200:
            print(f"  Login failed: {login_response.text}")
            return None
        
        login_data = login_response.json()
        token = login_data['access_token']
        user_id = login_data['user']['id']
        
        print("  [OK] Login successful")
        print(f"  User ID: {user_id}")
        
        # Create complete profile
        print(f"\n[STEP 3] Creating complete profile...")
        
        profile_data = {
            # Basic Information
            "age": 32,
            "gender": "male",
            "height": 175.5,  # cm
            "weight": 78.2,   # kg
            "training_level": "advanced",
            
            # Fitness Goals
            "fitness_goals": [
                "weight_loss",
                "muscle_gain",
                "strength",
                "endurance",
                "flexibility"
            ],
            
            # Exercise History
            "exercise_history_years": 5,
            "exercise_history_description": "I have been training consistently for 5 years. Started with bodyweight exercises at home, then moved to gym training. I focus on compound movements, progressive overload, and periodization. I train 5-6 days per week with a split routine.",
            
            # Injuries
            "injuries": [
                "knee",
                "shoulder"
            ],
            "injury_details": "I have a minor knee injury from running (patellar tendinitis) that I manage with proper warm-up and stretching. Also have occasional shoulder impingement from overhead movements, so I avoid heavy overhead pressing.",
            
            # Medical Conditions
            "medical_conditions": [
                "high_blood_pressure"
            ],
            "medical_condition_details": "I have mild hypertension that is well-controlled with medication. I monitor my heart rate during intense workouts and avoid excessive caffeine before training.",
            
            # Equipment Access
            "gym_access": True,
            "equipment_access": [
                "machine",
                "dumbbells",
                "barbell",
                "cable_machine",
                "smith_machine",
                "leg_press",
                "pull_up_bar"
            ],
            "home_equipment": [
                "dumbbells",
                "resistance_bands",
                "yoga_mat",
                "pull_up_bar"
            ],
            
            # Preferences
            "preferred_workout_time": "evening",
            "workout_days_per_week": 6,
            "preferred_intensity": "heavy"
        }
        
        update_response = requests.put(
            f"{BASE_URL}/api/user/profile",
            json=profile_data,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
        )
        
        print(f"  Profile Update Status: {update_response.status_code}")
        
        if update_response.status_code == 200:
            print("  [OK] Profile created successfully")
            profile_info = update_response.json()['profile']
            print(f"  Age: {profile_info.get('age')}")
            print(f"  Weight: {profile_info.get('weight')} kg")
            print(f"  Height: {profile_info.get('height')} cm")
            print(f"  Gender: {profile_info.get('gender')}")
            print(f"  Training Level: {profile_info.get('training_level')}")
        else:
            print(f"  Profile update failed: {update_response.text}")
            return None
        
        # Verify profile
        print(f"\n[STEP 4] Verifying profile...")
        verify_response = requests.get(
            f"{BASE_URL}/api/user/profile",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if verify_response.status_code == 200:
            verified_profile = verify_response.json()
            print("  [OK] Profile verification successful")
            print(f"  All fields populated: YES")
            
            # Count filled fields
            filled_fields = sum(1 for v in verified_profile.values() if v is not None and v != [])
            print(f"  Total fields with data: {filled_fields}")
        else:
            print(f"  Verification failed: {verify_response.text}")
        
        print(f"\n{'=' * 70}")
        print("ACCOUNT CREATION COMPLETE!")
        print("=" * 70)
        print(f"\nCREDENTIALS:")
        print(f"  Username: {username}")
        print(f"  Email: {email}")
        print(f"  Password: {password}")
        print(f"  User ID: {user_id}")
        print(f"\nPROFILE DETAILS:")
        print(f"  Age: {profile_data['age']}")
        print(f"  Gender: {profile_data['gender']}")
        print(f"  Height: {profile_data['height']} cm")
        print(f"  Weight: {profile_data['weight']} kg")
        print(f"  Training Level: {profile_data['training_level']}")
        print(f"  Exercise History: {profile_data['exercise_history_years']} years")
        print(f"  Gym Access: {profile_data['gym_access']}")
        print(f"  Workout Days/Week: {profile_data['workout_days_per_week']}")
        print(f"  Preferred Time: {profile_data['preferred_workout_time']}")
        print(f"  Preferred Intensity: {profile_data['preferred_intensity']}")
        print(f"  Fitness Goals: {', '.join(profile_data['fitness_goals'])}")
        print(f"  Injuries: {', '.join(profile_data['injuries'])}")
        print(f"  Medical Conditions: {', '.join(profile_data['medical_conditions'])}")
        print(f"  Equipment Access: {len(profile_data['equipment_access'])} items")
        print(f"  Home Equipment: {len(profile_data['home_equipment'])} items")
        print(f"\n{'=' * 70}\n")
        
        return {
            "username": username,
            "email": email,
            "password": password,
            "user_id": user_id
        }
        
    except requests.exceptions.ConnectionError:
        print(f"\n  [ERROR] Cannot connect to backend server")
        print(f"  Make sure the backend is running on {BASE_URL}")
        return None
    except Exception as e:
        print(f"\n  [ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = create_complete_user()
    if result:
        print("\n[SUCCESS] Account created successfully!")
        print(f"You can now log in with:")
        print(f"  Username: {result['username']}")
        print(f"  Password: {result['password']}")
    else:
        print("\n[ERROR] Account creation failed")
        exit(1)

