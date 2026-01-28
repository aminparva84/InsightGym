# Test Account Credentials

## Account Information

**Username:** `testuser_complete`  
**Email:** `testuser_complete@example.com`  
**Password:** `Test123456!`

## Complete Profile Details

### Basic Information
- **Age:** 28
- **Gender:** Male
- **Height:** 180 cm
- **Weight:** 75.5 kg
- **Training Level:** Intermediate
- **Exercise History:** 3 years
- **Exercise History Description:** "I have been working out for 3 years, focusing on strength training and cardio. I go to the gym regularly and have experience with free weights and machines."

### Training Goals
- Weight Loss
- Muscle Gain
- Strength
- Endurance

### Injuries
- Knee
- Lower Back
- **Injury Details:** "I have a minor knee injury from running and occasional lower back pain from heavy lifting. I need to be careful with squats and deadlifts."

### Medical Conditions
- High Blood Pressure
- **Medical Condition Details:** "I have mild high blood pressure that is controlled with medication. I need to monitor my heart rate during intense workouts."

### Training Conditions
- **Gym Access:** Yes
- **Gym Equipment:**
  - Machines
  - Dumbbells
  - Barbell
  - Cable Machine
- **Workout Days Per Week:** 5
- **Preferred Workout Time:** Evening
- **Preferred Intensity:** Medium

## Testing Steps

1. **Login Test:**
   - Open the frontend application
   - Click "Login" or "Sign Up"
   - Use the credentials above to log in
   - Verify you are redirected to the dashboard

2. **Profile Data Verification:**
   - Navigate to Dashboard → Profile tab
   - Verify all the profile details listed above are displayed correctly
   - Check that all fields are populated with the correct values

3. **Navigation Test (User Should Stay Logged In):**
   - From Dashboard, click on the site title to go to Landing Page
   - Verify you remain logged in (should see "My Profile" and "Logout" buttons)
   - Navigate back to Dashboard
   - Verify you remain logged in
   - Reload the page (F5)
   - Verify you remain logged in
   - Navigate between different tabs (Profile, History, Nutrition, Tips, Injuries)
   - Verify you remain logged in throughout

4. **Logout Test:**
   - Click the "Logout" button
   - Verify you are logged out and redirected to landing page
   - Verify you cannot access dashboard without logging in again

## Notes

- The account has been created with all profile details
- If you encounter any issues with profile data not displaying, check the browser console for errors
- If you encounter token validation errors, the fixes we implemented should handle them, but you may need to clear browser cache/localStorage and log in again





