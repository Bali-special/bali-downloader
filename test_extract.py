import urllib.request
import json
req = urllib.request.Request(
    'http://localhost:5000/api/extract',
    data=json.dumps({'url': 'https://www.tiktok.com/@mrbeast/video/7338166946059128107'}).encode(),
    headers={'Content-Type': 'application/json'}
)
try:
    res = urllib.request.urlopen(req)
    print(res.read().decode())
except Exception as e:
    print(e.read().decode())
