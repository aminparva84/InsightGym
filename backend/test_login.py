"""
Test login endpoint to see what error we get
"""

import requests
import json

# Test login
response = requests.post('http://localhost:5000/api/login', json={
    'username': 'demo',
    'password': 'demo123'
})

print(f"Status Code: {response.status_code}")
print(f"Response: {response.json()}")

# If login fails, try registration
if response.status_code != 200:
    print("\nTrying to register...")
    reg_response = requests.post('http://localhost:5000/api/register', json={
        'username': 'demo',
        'email': 'demo@raha-fitness.com',
        'password': 'demo123',
        'language': 'fa'
    })
    print(f"Registration Status: {reg_response.status_code}")
    print(f"Registration Response: {reg_response.json()}")

