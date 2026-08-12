import urllib.request
import json

def test_cobalt(url):
    api_url = 'https://cobalt-api.kwiatekit.com/'
    data = json.dumps({
        'url': url
    }).encode('utf-8')
    req = urllib.request.Request(api_url, data=data, headers={
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    })
    try:
        with urllib.request.urlopen(req) as res:
            response_data = json.loads(res.read().decode())
            print(json.dumps(response_data, indent=2))
    except Exception as e:
        if hasattr(e, 'read'):
            print(f"Error: {e.read().decode()}")
        else:
            print(f"Error: {e}")

if __name__ == '__main__':
    test_cobalt('https://www.tiktok.com/@mrbeast/video/7338166946059128107')
