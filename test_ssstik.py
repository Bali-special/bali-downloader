import urllib.request
import urllib.parse
import re

def extract_ssstik(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }
    
    # 1. Get homepage to get 'tt' token
    req1 = urllib.request.Request('https://ssstik.io/en', headers=headers)
    tt_token = '0'
    try:
        with urllib.request.urlopen(req1) as res1:
            html = res1.read().decode('utf-8')
            # The token is usually hidden in a script or form input
            match = re.search(r's_tt\s*=\s*["\']([^"\']+)["\']', html)
            if match:
                tt_token = match.group(1)
            else:
                match2 = re.search(r'name="tt"\s+value=["\']([^"\']+)["\']', html)
                if match2:
                    tt_token = match2.group(1)
            print("Found token:", tt_token)
    except Exception as e:
        print("Failed to get homepage:", e)
        return
        
    # 2. Post to API
    api_url = 'https://ssstik.io/abc?url=dl'
    data = urllib.parse.urlencode({'id': url, 'locale': 'en', 'tt': tt_token}).encode('utf-8')
    headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
    headers['Hx-Request'] = 'true'
    headers['Hx-Trigger'] = '_gcaptcha_pt'
    headers['Hx-Target'] = 'target'
    headers['Hx-Current-Url'] = 'https://ssstik.io/en'
    
    req2 = urllib.request.Request(api_url, data=data, headers=headers)
    try:
        with urllib.request.urlopen(req2) as res2:
            result_html = res2.read().decode('utf-8')
            print("Result HTML snippet:")
            print(result_html[:500])
            
            # Find the download link
            dl_match = re.search(r'href=["\'](https://tikcdn\.io/[^"\']+)["\']', result_html)
            if not dl_match:
                dl_match = re.search(r'href=["\']([^"\']+watermark=1[^"\']*)["\']', result_html)
                
            if dl_match:
                print("\nExtracted URL:", dl_match.group(1))
            else:
                print("\nCould not extract URL from HTML")
    except Exception as e:
        print("Failed to post:", e)
        if hasattr(e, 'read'):
            print(e.read().decode())

if __name__ == '__main__':
    extract_ssstik('https://www.tiktok.com/@mrbeast/video/7338166946059128107')
