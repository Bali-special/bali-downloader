import urllib.request
import json
import urllib.parse

def test_tikly(url):
    api_url = f"https://api.tiklydown.eu.org/api/download?url={urllib.parse.quote(url)}"
    req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as res:
            response_data = json.loads(res.read().decode())
            print(json.dumps(response_data, indent=2))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    test_tikly('https://www.tiktok.com/@mrbeast/video/7338166946059128107')
