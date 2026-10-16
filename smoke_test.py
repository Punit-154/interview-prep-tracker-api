import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'interview_tracker.settings')
django.setup()

from rest_framework.test import APIClient
from tracker.models import Problem, Attempt

client = APIClient()

print("--- Testing API Flow ---")

# 1. Health check
res = client.get('/')
print(f"1. Health Check: {res.status_code} - {res.json().get('status')}")
assert res.status_code == 200

# 2. Problems list
res = client.get('/api/problems/?topic=arrays&difficulty=easy')
print(f"2. Problems Filter: {res.status_code} - Found {res.json().get('count')} problems")
assert res.status_code == 200

# 3. Register user
reg_payload = {
    'username': 'demo_intern',
    'email': 'intern@interviewkickstart.com',
    'password': 'Password123!',
    'password_confirm': 'Password123!'
}
res = client.post('/api/auth/register/', reg_payload)
print(f"3. Register User: {res.status_code} - User ID: {res.json().get('id')}")
assert res.status_code == 201
access_token = res.json()['tokens']['access']

# 4. Authenticate client with JWT
client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

# 5. Get current user profile
res = client.get('/api/auth/me/')
print(f"5. Current User: {res.status_code} - {res.json().get('username')}")
assert res.status_code == 200

# 6. Create attempt
p = Problem.objects.first()
attempt_payload = {
    'problem': p.id,
    'status': 'solved',
    'time_taken': 18,
    'notes': 'Solved with two pointers. Optimal O(n) time and O(1) space.'
}
res = client.post('/api/attempts/', attempt_payload)
print(f"6. Create Attempt: {res.status_code} - Attempt ID: {res.json().get('id')} for problem '{res.json().get('problem_detail', {}).get('title')}'")
assert res.status_code == 201

# 7. Check stats
res = client.get('/api/attempts/stats/')
print(f"7. Stats: {res.status_code} - Solved: {res.json().get('total_solved')}, Time: {res.json().get('total_time_spent_minutes')} mins")
print(f"   Topic breakdown: {res.json().get('solved_by_topic')}")
assert res.status_code == 200
assert res.json()['total_solved'] == 1

print("\n>>> ALL API VERIFICATIONS SUCCEEDED! <<<")
