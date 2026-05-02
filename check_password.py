import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(),'')))

from app import create_app
from backend.models import User

app = create_app('development')
with app.app_context():
    u = User.query.filter_by(username='testuser').first()
    print('user', u)
    if u:
        print('check_password password123:', u.check_password('password123'))
        print('check_password wrong:', u.check_password('foo'))
