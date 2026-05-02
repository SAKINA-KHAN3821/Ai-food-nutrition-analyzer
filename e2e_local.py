from app import create_app
import re

app = create_app('development')
with app.test_client() as client:
    # Attempt login using demo user credentials
    resp = client.post('/login', data={'username':'demo_user','password':'demo123'}, follow_redirects=True)
    print('Login status code:', resp.status_code)

    resp = client.get('/dashboard')
    print('Dashboard status code:', resp.status_code)
    html = resp.get_data(as_text=True)

    ids = ['cal-progress','pro-progress','fat-progress','carbs-progress']
    for id_ in ids:
        m = re.search(r'id="%s"[^>]*style=[\"\']?[^>]*width:\s*([0-9]+)%%' % id_, html)
        if m:
            print(f'{id_} -> {m.group(1)}%')
        else:
            print(f'{id_} -> NOT FOUND')

    # Print snippet
    idx = html.find('id="cal-progress"')
    if idx!=-1:
        print('\nSnippet:')
        print(html[max(0,idx-80):idx+120])
    else:
        print('cal-progress id not found')
