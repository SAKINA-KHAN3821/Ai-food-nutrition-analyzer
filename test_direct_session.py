import sys, os
sys.path.insert(0, os.path.abspath(os.getcwd()))

from app import create_app
from backend.models import User, db

app = create_app('development')
client = app.test_client()

with app.app_context():
    # Create test user
    user = User.query.filter_by(username='directtest').first()
    if user:
        db.session.delete(user)
        db.session.commit()
    
    user = User(username='directtest', email='directtest@test.com', full_name='Direct Test')
    user.set_password('testpass')
    db.session.add(user)
    db.session.commit()
    user_id = user.user_id
    print(f'Created user: id={user_id}')

# Test API call with session manually set
with client:
    # Simulate logged-in session
    with client.session_transaction() as sess:
        sess['user_id'] = user_id
        sess['username'] = 'directtest'
    
    print('\n=== API ADD (login via session, no CSRF) ===')
    resp = client.post('/api/nutrition/add', json={
        'food_name': 'TestFood',
        'quantity': 100,
        'calories': 150,
        'protein': 5,
        'fat': 3,
        'carbohydrates': 25,
        'meal_type': 'lunch'
    })
    print('Status:', resp.status_code)
    data = resp.get_json()
    print('Response:', data)
    if resp.status_code == 201:
        print('✓ SUCCESS! Nutrition entry added')
        entry = data.get('entry')
        if entry:
            print(f'  Entry ID: {entry.get("history_id")}')
            print(f'  Food: {entry.get("food_name")}')
            print(f'  Calories: {entry.get("calories")}')
    else:
        print(f'✗ FAILED with status {resp.status_code}')
