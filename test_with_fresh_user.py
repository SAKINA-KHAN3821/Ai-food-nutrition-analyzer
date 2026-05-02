import sys, os, requests
sys.path.insert(0, os.path.abspath(os.getcwd()))

# First, create test data directly in the database
from app import create_app
from backend.models import User, db

app = create_app('development')
with app.app_context():
    # Fresh user for testing
    user = User.query.filter_by(username='apitest').first()
    if user:
        db.session.delete(user)
        db.session.commit()
    
    user = User(username='apitest', email='apitest@test.com', full_name='API Test')
    user.set_password('testpass')
    db.session.add(user)
    db.session.commit()
    print(f'Created user: id={user.user_id}, username={user.username}')

# Now test the API
import time
print('\nWaiting for server...')
time.sleep(2)

BASE = 'http://127.0.0.1:5000'

# Create a session but don't set cookies yet
resp = requests.post(BASE + '/api/auth/login', json={
    'username': 'apitest',
    'password': 'testpass'
})
print('\nLogin response code:', resp.status_code)
if resp.status_code == 200:
    print('Login successful')
    data = resp.json()
    print('User:', data.get('user', {}).get('username'))
    
    # Extract session from response  
    cookies = resp.cookies
    print(f'Cookies from login: {list(cookies.keys())}')
    
    # Now use a new session with the cookies
    s = requests.Session()
    s.cookies.update(cookies)
    
    # Try the add endpoint with explicit session cookies
    add_data = {
        'food_name': 'APITestFood',
        'quantity': 100,
        'calories': 150,
        'protein': 5,
        'fat': 3,
        'carbohydrates': 25,
        'meal_type': 'lunch'
    }
    
    print(f'\nSending nutrition/add with cookies={list(s.cookies.keys())}')
    resp2 = s.post(BASE + '/api/nutrition/add', json=add_data)
    print('nutrition/add status:', resp2.status_code)
    print('nutrition/add response text:', resp2.text[:300])
else:
    print('Login failed:', resp.text[:200])
