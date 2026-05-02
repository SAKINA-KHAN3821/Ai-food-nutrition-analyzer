import sqlite3, os

db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'nutrition.db')
conn = sqlite3.connect(db_path)
cur = conn.cursor()
cur.execute('SELECT user_id, username, email, password_hash FROM users')
for row in cur.fetchall():
    print(row)
conn.close()
