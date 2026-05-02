import sys, os, requests
sys.path.insert(0, os.path.abspath(os.getcwd()))

from app import create_app
from backend.models import User, db
import time

app = create_app('development')
with app.app_context():
    user = User.query.filter_by(username='apitest3').first()
    if user:
        db.session.delete(user)
        db.session.commit()
    
    user = User(username='apitest3', email='apitest3@test.com')
    user.set_password('testpass')
    db.session.add(user)
    db.session.commit()
    print('Created user')

time.sleep(2)

BASE = 'http://127.0.0.1:5000'
s = requests.Session()

# Login
print('\n=== LOGIN ===')
resp = s.post(BASE + '/api/auth/login', json={'username': 'apitest3', 'password': 'testpass'})
print('Status:', resp.status_code)

# Get CSRF token from session (in a real app, you'd get this from a page load or from the login response)
# For this test, we'll extract it from the session cookie if it's there, or get it from the app
with app.app_context():
    from flask import session as flask_session
    # The session is created server-side, we need to extract it from our authenticated requests
    # For now, let's make a request to a page that returns the token
    
# Actually, let's just test with and without CSRF first
print('\n=== TEST 1: Add WITHOUT CSRF token (should fail) ===')
add_data = {
    'food_name': 'Test1',
    'quantity': 100,
    'calories': 150,
    'protein': 5,
    'fat': 3,
    'carbohydrates': 25
}
resp = s.post(BASE + '/api/nutrition/add', json=add_data)
print('Status:', resp.status_code)

# Now get a CSRF token by accessing a page
print('\n=== GET CSRF TOKEN from dashboard ===')
resp = s.get(BASE + '/dashboard')
print('Dashboard status:', resp.status_code)

# The CSRF token should be in the session cookie now. Extract it from the response HTML if it's embedded
# Or better, we can use Flask's test client
print('\n=== TEST 2: Add WITH CSRF token ===')
# Get the csrf_token from the app context's session
# Since we're using requests, we need a different approach

# Let's create the token ourselves using Flask
csrf_token_value = 'dummy_token_for_testing'  # Just for testing the header requirement

resp = s.post(BASE + '/api/nutrition/add', 
              json=add_data,
              headers={'X-CSRF-Token': csrf_token_value})
print('Status:', resp.status_code)
print('Response:', resp.text[:200])
