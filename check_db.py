import sqlite3, os

db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'nutrition.db')
print('DB path:', db_path)
if not os.path.exists(db_path):
    print('DB file not found')
    raise SystemExit(1)

conn = sqlite3.connect(db_path)
cur = conn.cursor()
for tbl in ('nutrition_history', 'daily_nutrition', 'users'):
    try:
        cur.execute(f'SELECT count(*) FROM {tbl}')
        cnt = cur.fetchone()[0]
        print(f'{tbl} rows: {cnt}')
    except Exception as e:
        print(f'Error querying {tbl}:', e)

# Show last 5 entries from nutrition_history
try:
    cur.execute('SELECT history_id, user_id, food_name, calories, protein, carbohydrates, meal_type, timestamp FROM nutrition_history ORDER BY timestamp DESC LIMIT 5')
    rows = cur.fetchall()
    if rows:
        print('\nLast nutrition_history rows:')
        for r in rows:
            print(r)
    else:
        print('\nNo rows in nutrition_history')
except Exception as e:
    print('Error fetching last rows:', e)

conn.close()
