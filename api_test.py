import requests

BASE = 'http://127.0.0.1:5000'

s = requests.Session()
# ensure testuser exists by registering (ignoring failure)
s.post(BASE + '/api/auth/register', json={'username':'testuser','email':'test@example.com','password':'password123','full_name':'Test User'})

# login
resp = s.post(BASE + '/api/auth/login', json={'username':'testuser','password':'password123'})
print('login status', resp.status_code, resp.json())

# add nutrition
data = {
    'food_name': 'API Test Food',
    'quantity': 100,
    'calories': 120,
    'protein': 5,
    'fat': 3,
    'carbohydrates': 20,
    'meal_type': 'snack',
    'image_path': None,
    'confidence': 0.8
}

resp = s.post(BASE + '/api/nutrition/add', json=data)
print('add status', resp.status_code, resp.json())

# fetch history
resp = s.get(BASE + '/api/nutrition/history')
print('history status', resp.status_code, resp.json())
