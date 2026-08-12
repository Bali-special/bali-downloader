import urllib.request
import json
import urllib.parse

def test_tikwm(url):
    api_url = 'https://www.tikwm.com/api/'
    data = urllib.parse.urlencode({'url': url, 'count': 12, 'cursor': 0, 'web': 1, 'hd': 1}).encode('utf-8')
    req = urllib.request.Request(api_url, data=data, headers={
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    })
    try:
        with urllib.request.urlopen(req) as res:
            response_data = json.loads(res.read().decode())
            print(json.dumps(response_data, indent=2))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    test_tikwm('https://www.tiktok.com/@mrbeast/video/7338166946059128107')
