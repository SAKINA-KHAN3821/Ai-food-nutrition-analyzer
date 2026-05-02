import sys, os, requests
import logging

# Enable HTTP logging to see what's being sent
logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Log HTTP requests/responses
import http.client as http_client
http_client.HTTPConnection.debuglevel = 1

sys.path.insert(0, os.path.abspath(os.getcwd()))

from app import create_app
from backend.models import User, db

app = create_app('development')
with app.app_context():
    user = User.query.filter_by(username='apitest2').first()
    if user:
        db.session.delete(user)
        db.session.commit()
    
    user = User(username='apitest2', email='apitest2@test.com', full_name='API Test 2')
    user.set_password('testpass')
    db.session.add(user)
    db.session.commit()
    print(f'Created user')

import time
time.sleep(1)

BASE = 'http://127.0.0.1:5000'
s = requests.Session()

# Login
print('\n=== LOGIN ===')
resp = s.post(BASE + '/api/auth/login', json={'username': 'apitest2', 'password': 'testpass'})
print('Status:', resp.status_code)

# Prepare request
print('\n=== PREPARE ADD REQUEST ===')
add_data = {
    'food_name': 'Test',
    'quantity': 100,
    'calories': 150,
    'protein': 5,
    'fat': 3,
    'carbohydrates': 25
}

print('URL: /api/nutrition/add')
print(f'Headers would be: Content-Type: application/json')
print(f'Body: {add_data}')

print('\n=== SENDING ADD REQUEST ===')
resp = s.post(BASE + '/api/nutrition/add', json=add_data)
print('\nResponse status:', resp.status_code)
print('Response text:', resp.text[:500])
