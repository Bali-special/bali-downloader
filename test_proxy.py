import urllib.request
import urllib.parse
import json

def test_proxy():
    # A dummy URL that is valid
    video_url = 'https://httpbin.org/get'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'}
    
    encoded_url = urllib.parse.quote(video_url)
    encoded_headers = urllib.parse.quote(json.dumps(headers))
    
    proxy_url = f'http://127.0.0.1:5000/api/proxy?url={encoded_url}&headers={encoded_headers}'
    print("Testing proxy URL:", proxy_url)
    
    try:
        res = urllib.request.urlopen(proxy_url)
        print("Proxy response status:", res.status)
        print("Headers:", res.headers)
    except Exception as e:
        print("Proxy failed:", e)
        if hasattr(e, 'read'):
            print(e.read().decode())

if __name__ == '__main__':
    test_proxy()
