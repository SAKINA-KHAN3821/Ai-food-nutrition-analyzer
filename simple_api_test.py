import sys, os
sys.path.insert(0, os.path.abspath(os.getcwd()))

from app import create_app
from backend.models import User, db
import requests
import json

# Reset password for testuser
app = create_app('development')
with app.app_context():
    user = User.query.filter_by(username='testuser').first()
    if user:
        user.set_password('newpass123')
        db.session.commit()
        print('Reset testuser password')

# Give server a moment
import time
time.sleep(5)

# Login and test API
BASE = 'http://127.0.0.1:5000'
s = requests.Session()
resp1 = s.post(BASE + '/api/auth/login', json={'username':'testuser','password':'newpass123'})
print('Login response:', resp1.status_code, resp1.text[:200])

# Try to add nutrition entry
data = {
    'food_name': 'TestFood',
    'quantity': 100,
    'calories': 150,
    'protein': 5,
    'fat': 3,
    'carbohydrates': 25,
    'meal_type': 'lunch',
    'image_path': None,
    'confidence': 0.8
}

print('\n=== Sending POST to /api/nutrition/add ===')
print('Data:', json.dumps(data))

resp2 = s.post(BASE + '/api/nutrition/add', json=data)
print('\nAdd response status:', resp2.status_code)
print('Add response text:', repr(resp2.text))
print('Add response headers:', dict(resp2.headers))

if resp2.status_code not in (200, 201):
    print('\nERROR: Got status', resp2.status_code)
else:
    print('Success!')
    print(resp2.json())
