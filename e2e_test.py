import http.cookiejar, urllib.request, urllib.parse, re

BASE = 'http://127.0.0.1:5000'
LOGIN_PATH = '/login'
DASH_PATH = '/dashboard'

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

# Login payload (form)
data = urllib.parse.urlencode({'username': 'demo_user', 'password': 'demo123'}).encode('utf-8')
req = urllib.request.Request(BASE + LOGIN_PATH, data=data)
resp = opener.open(req)
print('Login response:', resp.getcode())

# Fetch dashboard
resp = opener.open(BASE + DASH_PATH)
html = resp.read().decode('utf-8')
print('Dashboard response:', resp.getcode())

ids = ['cal-progress','pro-progress','fat-progress','carbs-progress']
for id_ in ids:
    m = re.search(r'%s"[^>]*style=[\"\']?[^>]*width:\s*([0-9]+)%%' % id_, html)
    if m:
        print(f'{id_} -> {m.group(1)}%')
    else:
        # fallback: find style attribute by id
        m2 = re.search(r'id="%s"[^>]*style=[\"\']?([^\"\'>]+)' % id_, html)
        print(f'{id_} -> style attr: ' + (m2.group(1) if m2 else 'NOT FOUND'))

# Quick sanity: print a short snippet around cal-progress
idx = html.find('id="cal-progress"')
if idx!=-1:
    print('\nSnippet:')
    print(html[max(0,idx-80):idx+120])
else:
    print('cal-progress id not in HTML')
