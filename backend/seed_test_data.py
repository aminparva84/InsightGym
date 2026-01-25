"""
Script to seed test data:
- Delete all existing members
- Create 10 new members with complete profiles
- Create 2 assistants with complete profiles
- Assign 2 members to admin
- Assign 4 members to each assistant
"""

from app import app, db
from app import User
from models import UserProfile
from werkzeug.security import generate_password_hash
import json

def seed_test_data():
    """Seed test data for development"""
    with app.app_context():
        try:
            print("=" * 70)
            print("Seeding Test Data")
            print("=" * 70)
            
            # Get admin user
            admin = User.query.filter_by(role='admin').first()
            if not admin:
                print("[ERROR] Admin user not found. Please create admin first.")
                return
            
            print(f"[OK] Found admin: {admin.username} (ID: {admin.id})")
            
            # Delete all existing members
            print("\n[1] Deleting existing members...")
            members = User.query.filter_by(role='member').all()
            for member in members:
                # Delete profile
                profile = UserProfile.query.filter_by(user_id=member.id).first()
                if profile:
                    db.session.delete(profile)
                # Delete user
                db.session.delete(member)
            deleted_count = len(members)
            print(f"[OK] Deleted {deleted_count} existing members")
            
            # Delete all existing assistants (except keep admin)
            print("\n[2] Deleting existing assistants...")
            assistants = User.query.filter_by(role='assistant').all()
            for assistant in assistants:
                # Delete profile
                profile = UserProfile.query.filter_by(user_id=assistant.id).first()
                if profile:
                    db.session.delete(profile)
                # Delete user
                db.session.delete(assistant)
            deleted_assistants = len(assistants)
            print(f"[OK] Deleted {deleted_assistants} existing assistants")
            
            db.session.commit()
            
            # Create 2 assistants with complete profiles
            print("\n[3] Creating 2 assistants with complete profiles...")
            assistants_data = [
                {
                    'username': 'assistant1',
                    'email': 'assistant1@insightgym.com',
                    'password': 'assistant123',
                    'age': 28,
                    'gender': 'male',
                    'weight': 80.5,
                    'height': 180,
                    'training_level': 'advanced',
                    'certifications': 'NASM-CPT, ACE-CPT, ISSA Certified Personal Trainer',
                    'qualifications': 'BS in Exercise Science, MS in Sports Physiology',
                    'years_of_experience': 5,
                    'specialization': 'Bodybuilding, Strength Training, Weight Loss',
                    'education': 'MS in Sports Physiology from University of Tehran',
                    'bio': 'Experienced personal trainer specializing in bodybuilding and strength training. 5 years of experience helping clients achieve their fitness goals.',
                    'chest_circumference': 110,
                    'waist_circumference': 85,
                    'abdomen_circumference': 90,
                    'arm_circumference': 38,
                    'hip_circumference': 100,
                    'thigh_circumference': 60
                },
                {
                    'username': 'assistant2',
                    'email': 'assistant2@insightgym.com',
                    'password': 'assistant123',
                    'age': 32,
                    'gender': 'female',
                    'weight': 65.0,
                    'height': 165,
                    'training_level': 'advanced',
                    'certifications': 'ACSM-CPT, NSCA-CSCS, Yoga Alliance RYT-200',
                    'qualifications': 'BS in Physical Education, Certified Nutrition Specialist',
                    'years_of_experience': 8,
                    'specialization': 'Weight Loss, Functional Training, Yoga, Nutrition',
                    'education': 'BS in Physical Education from Shahid Beheshti University',
                    'bio': 'Certified personal trainer and nutrition specialist with 8 years of experience. Specializes in weight loss, functional training, and holistic wellness approaches.',
                    'chest_circumference': 95,
                    'waist_circumference': 70,
                    'abdomen_circumference': 75,
                    'arm_circumference': 28,
                    'hip_circumference': 95,
                    'thigh_circumference': 55
                }
            ]
            
            created_assistants = []
            for idx, asst_data in enumerate(assistants_data, 1):
                assistant = User(
                    username=asst_data['username'],
                    email=asst_data['email'],
                    password_hash=generate_password_hash(asst_data['password']),
                    role='assistant',
                    language='fa'
                )
                db.session.add(assistant)
                db.session.flush()
                
                # Create complete profile
                profile = UserProfile(
                    user_id=assistant.id,
                    account_type='assistant',
                    age=asst_data['age'],
                    gender=asst_data['gender'],
                    weight=asst_data['weight'],
                    height=asst_data['height'],
                    training_level=asst_data['training_level'],
                    certifications=asst_data['certifications'],
                    qualifications=asst_data['qualifications'],
                    years_of_experience=asst_data['years_of_experience'],
                    specialization=asst_data['specialization'],
                    education=asst_data['education'],
                    bio=asst_data['bio'],
                    chest_circumference=asst_data['chest_circumference'],
                    waist_circumference=asst_data['waist_circumference'],
                    abdomen_circumference=asst_data['abdomen_circumference'],
                    arm_circumference=asst_data['arm_circumference'],
                    hip_circumference=asst_data['hip_circumference'],
                    thigh_circumference=asst_data['thigh_circumference'],
                    exercise_history_years=asst_data['years_of_experience'] + 5,
                    exercise_history_description='Professional trainer with extensive experience in fitness and training.',
                    gym_access=True,
                    workout_days_per_week=6,
                    preferred_workout_time='morning',
                    preferred_intensity='heavy'
                )
                
                # Set JSON fields
                profile.set_fitness_goals(['muscle_gain', 'strength', 'endurance'])
                profile.set_equipment_access(['machine', 'dumbbells', 'barbell', 'cable'])
                profile.set_home_equipment(['dumbbells', 'resistance_bands'])
                
                db.session.add(profile)
                created_assistants.append(assistant)
                print(f"[OK] Created assistant {idx}: {asst_data['username']} (ID: {assistant.id})")
            
            db.session.commit()
            
            # Create 10 members with complete profiles
            print("\n[4] Creating 10 members with complete profiles...")
            members_data = [
                {
                    'username': 'member1', 'email': 'member1@insightgym.com', 'password': 'member123',
                    'age': 25, 'gender': 'male', 'weight': 75.0, 'height': 175,
                    'training_level': 'beginner', 'assigned_to': admin.id
                },
                {
                    'username': 'member2', 'email': 'member2@insightgym.com', 'password': 'member123',
                    'age': 30, 'gender': 'female', 'weight': 60.0, 'height': 160,
                    'training_level': 'intermediate', 'assigned_to': admin.id
                },
                {
                    'username': 'member3', 'email': 'member3@insightgym.com', 'password': 'member123',
                    'age': 28, 'gender': 'male', 'weight': 85.0, 'height': 180,
                    'training_level': 'beginner', 'assigned_to': created_assistants[0].id
                },
                {
                    'username': 'member4', 'email': 'member4@insightgym.com', 'password': 'member123',
                    'age': 35, 'gender': 'female', 'weight': 70.0, 'height': 165,
                    'training_level': 'intermediate', 'assigned_to': created_assistants[0].id
                },
                {
                    'username': 'member5', 'email': 'member5@insightgym.com', 'password': 'member123',
                    'age': 22, 'gender': 'male', 'weight': 70.0, 'height': 170,
                    'training_level': 'beginner', 'assigned_to': created_assistants[0].id
                },
                {
                    'username': 'member6', 'email': 'member6@insightgym.com', 'password': 'member123',
                    'age': 27, 'gender': 'female', 'weight': 55.0, 'height': 158,
                    'training_level': 'advanced', 'assigned_to': created_assistants[0].id
                },
                {
                    'username': 'member7', 'email': 'member7@insightgym.com', 'password': 'member123',
                    'age': 33, 'gender': 'male', 'weight': 90.0, 'height': 185,
                    'training_level': 'intermediate', 'assigned_to': created_assistants[1].id
                },
                {
                    'username': 'member8', 'email': 'member8@insightgym.com', 'password': 'member123',
                    'age': 29, 'gender': 'female', 'weight': 65.0, 'height': 162,
                    'training_level': 'beginner', 'assigned_to': created_assistants[1].id
                },
                {
                    'username': 'member9', 'email': 'member9@insightgym.com', 'password': 'member123',
                    'age': 26, 'gender': 'male', 'weight': 78.0, 'height': 178,
                    'training_level': 'intermediate', 'assigned_to': created_assistants[1].id
                },
                {
                    'username': 'member10', 'email': 'member10@insightgym.com', 'password': 'member123',
                    'age': 31, 'gender': 'female', 'weight': 68.0, 'height': 168,
                    'training_level': 'advanced', 'assigned_to': created_assistants[1].id
                }
            ]
            
            created_members = []
            for idx, member_data in enumerate(members_data, 1):
                member = User(
                    username=member_data['username'],
                    email=member_data['email'],
                    password_hash=generate_password_hash(member_data['password']),
                    role='member',
                    language='fa',
                    assigned_to=member_data['assigned_to']
                )
                db.session.add(member)
                db.session.flush()
                
                # Create complete profile
                profile = UserProfile(
                    user_id=member.id,
                    account_type='member',
                    age=member_data['age'],
                    gender=member_data['gender'],
                    weight=member_data['weight'],
                    height=member_data['height'],
                    training_level=member_data['training_level'],
                    chest_circumference=100 + (member_data['age'] % 10),
                    waist_circumference=80 + (member_data['age'] % 10),
                    abdomen_circumference=85 + (member_data['age'] % 10),
                    arm_circumference=30 + (member_data['age'] % 5),
                    hip_circumference=95 + (member_data['age'] % 10),
                    thigh_circumference=55 + (member_data['age'] % 5),
                    exercise_history_years=2 if member_data['training_level'] == 'beginner' else (4 if member_data['training_level'] == 'intermediate' else 6),
                    exercise_history_description=f"Regular exercise routine with focus on {member_data['training_level']} level training.",
                    gym_access=True,
                    workout_days_per_week=3 if member_data['training_level'] == 'beginner' else (4 if member_data['training_level'] == 'intermediate' else 5),
                    preferred_workout_time='evening' if idx % 2 == 0 else 'morning',
                    preferred_intensity='light' if member_data['training_level'] == 'beginner' else ('medium' if member_data['training_level'] == 'intermediate' else 'heavy')
                )
                
                # Set JSON fields based on training level
                if member_data['training_level'] == 'beginner':
                    profile.set_fitness_goals(['weight_loss', 'endurance'])
                    profile.set_injuries([])
                    profile.set_medical_conditions([])
                elif member_data['training_level'] == 'intermediate':
                    profile.set_fitness_goals(['muscle_gain', 'strength'])
                    profile.set_injuries(['knee'] if idx % 3 == 0 else [])
                    profile.set_medical_conditions([])
                else:  # advanced
                    profile.set_fitness_goals(['muscle_gain', 'strength', 'endurance'])
                    profile.set_injuries(['shoulder'] if idx % 2 == 0 else [])
                    profile.set_medical_conditions([])
                
                profile.set_equipment_access(['machine', 'dumbbells', 'barbell'])
                profile.set_home_equipment(['dumbbells', 'resistance_bands'])
                
                if profile.get_injuries():
                    profile.injury_details = f"Previous {profile.get_injuries()[0]} injury, fully recovered."
                
                db.session.add(profile)
                created_members.append(member)
                assigned_to_name = 'admin' if member_data['assigned_to'] == admin.id else f"assistant{created_assistants.index([a for a in created_assistants if a.id == member_data['assigned_to']][0]) + 1}"
                print(f"[OK] Created member {idx}: {member_data['username']} (ID: {member.id}) - Assigned to: {assigned_to_name}")
            
            db.session.commit()
            
            # Summary
            print("\n" + "=" * 70)
            print("SUMMARY")
            print("=" * 70)
            print(f"[OK] Deleted {deleted_count} existing members")
            print(f"[OK] Deleted {deleted_assistants} existing assistants")
            print(f"[OK] Created 2 assistants:")
            for idx, assistant in enumerate(created_assistants, 1):
                print(f"  - {assistant.username} (ID: {assistant.id})")
            print(f"[OK] Created 10 members:")
            print(f"  - 2 assigned to admin")
            print(f"  - 4 assigned to assistant1")
            print(f"  - 4 assigned to assistant2")
            print("\n" + "=" * 70)
            print("CREDENTIALS")
            print("=" * 70)
            print("\nAssistants:")
            for idx, assistant in enumerate(created_assistants, 1):
                print(f"  Assistant {idx}:")
                print(f"    Username: {assistant.username}")
                print(f"    Password: assistant123")
            print("\nMembers:")
            print("  All members:")
            print("    Username: member1 to member10")
            print("    Password: member123")
            print("\n" + "=" * 70)
            print("[SUCCESS] Test data seeded successfully!")
            print("=" * 70)
            
        except Exception as e:
            db.session.rollback()
            print(f"\n[ERROR] Error seeding data: {e}")
            import traceback
            traceback.print_exc()
            raise

if __name__ == '__main__':
    seed_test_data()

