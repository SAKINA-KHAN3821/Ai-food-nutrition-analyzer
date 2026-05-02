import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(),'')))

from app import create_app
from backend.models import User, db
import requests

# reset password for testuser
app = create_app('development')
with app.app_context():
    user = User.query.filter_by(username='testuser').first()
    if user:
        user.set_password('newpass123')
        db.session.commit()
        print('Password reset for testuser')
    else:
        print('testuser not found!')
        from backend.auth import register_user
        success,msg,udata = register_user('testuser','test@example.com','newpass123','Test User')
        print('registered new testuser', success, msg, udata)

import time

# now perform login via API and add entry using requests
BASE = 'http://127.0.0.1:5000'
s = requests.Session()
# give the server a moment to start
print('waiting for server to be ready...')
time.sleep(3)
resp = s.post(BASE + '/api/auth/login', json={'username':'testuser','password':'newpass123'})
print('login status', resp.status_code, resp.json())

if resp.ok:
    data = {'food_name':'API Food','quantity':100,'calories':100,'protein':5,'fat':3,'carbohydrates':20,'meal_type':'dinner','image_path':None,'confidence':0.5}
    resp2 = s.post(BASE + '/api/nutrition/add', json=data)
    print('add response', resp2.status_code, resp2.json())
    resp3 = s.get(BASE + '/api/nutrition/history')
    print('history response', resp3.status_code, resp3.json())
