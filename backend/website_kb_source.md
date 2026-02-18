# InsightGYM Knowledge Base

Use this file to store website knowledge that the AI can reference.
Add FAQs, policies, training program explanations, and any site-specific info here.

## Training Programs (Plans)
- We offer training programs (برنامه تمرینی) that members can purchase/assign.
- Flow: (1) User wants to buy → suggest_training_plans shows available plans. (2) After user buys/selects → create_workout_plan generates the actual workout.
- suggest_training_plans: for purchase intent (میخوام برنامه بخرم). Returns plans matched to user profile.
- create_workout_plan: ONLY after user bought a plan. Creates personalized workout from user profile + admin's Training Info (Training Levels Info tab: sets, reps, focus). Admin configures in Training Info > Training Levels Info.

## Examples
- Membership plans and pricing
- Trial period details
- How to book sessions
- Refund and cancellation policy
- Contact and support information
