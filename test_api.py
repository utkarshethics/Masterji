import urllib.request
import urllib.error
import json

req = urllib.request.Request(
    'https://v97j2s2fo3.execute-api.us-east-1.amazonaws.com/create-order',
    data=json.dumps({'amount': 5000, 'currency': 'INR'}).encode('utf-8'),
    headers={'Content-Type': 'application/json', 'Origin': 'https://www.masterji.online'}
)
try:
    resp = urllib.request.urlopen(req)
    print(resp.status)
    print(resp.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print(e.code)
    print(e.headers)
    print(e.read().decode('utf-8'))
