import sys, os
sys.path.insert(0, os.path.abspath(os.getcwd()))

from app import create_app
from backend.models import User, db

app = create_app('development')

# Use Flask's test client which will handle sessions properly
client = app.test_client()

with app.app_context():
    # Create test user
    user = User.query.filter_by(username='testflaskclient').first()
    if user:
        db.session.delete(user)
        db.session.commit()
    
    user = User(username='testflaskclient', email='test@test.com')
    user.set_password('testpass')
    db.session.add(user)
    db.session.commit()
    print('Created user')

# Login using form POST (which sets csrf_token in session)
print('\n=== FORM LOGIN ===')
resp = client.post('/login', data={
    'username': 'testflaskclient',
    'password': 'testpass',
    'csrf_token': 'dummy'  # This will be generated server-side
}, follow_redirects=False)
print('Login response status:', resp.status_code)
print('Location:', resp.headers.get('Location'))

# Now try API call with test client (which preserves session)
print('\n=== API ADD without CSRF (should fail) ===')
resp = client.post('/api/nutrition/add', json={
    'food_name': 'Test',
    'quantity': 100,
    'calories': 150,
    'protein': 5,
    'fat': 3,
    'carbohydrates': 25,
    'meal_type': 'lunch'
})
print('Status:', resp.status_code)
print('Response:', resp.get_json() if resp.content_type and 'json' in resp.content_type else resp.data[:200])

# Get CSRF token from session  
print('\n=== Extract CSRF token from session ===')
with client:
    resp = client.get('/dashboard')
    # The csrf_token is in the Flask session
    from flask import session
    csrf_token = session.get('csrf_token')
    print(f'CSRF token from session: {csrf_token}')
    
    # Now try with the correct CSRF token
    print('\n=== API ADD WITH correct CSRF ===')
    resp = client.post('/api/nutrition/add', 
                       json={
                           'food_name': 'Test2',
                           'quantity': 100,
                           'calories': 150,
                           'protein': 5,
                           'fat': 3,
                           'carbohydrates': 25,
                           'meal_type': 'lunch'
                       },
                       headers={'X-CSRF-Token': csrf_token})
    print('Status:', resp.status_code)
    data = resp.get_json()
    print('Response:', data)

