import urllib.request
import re
import html

def test_meta_ai_download():
    url = "https://www.meta.ai/@hectornavarro887/post/ON4Dkwq34Ol?open_in_meta_ai=true&utm_source=android_meta_ai_sl"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    }

    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response:
        html_content = response.read().decode('utf-8')
        
        # Look for Facebook CDN mp4 links
        video_matches = re.findall(r'https://[^"\']+\.mp4[^"\']*oe=[0-9A-Fa-f]{8}', html_content)
        videos = []
        for v in video_matches:
            v = v.replace('\\u0026amp;', '&')
            v = v.replace('\\u0026', '&')
            v = html.unescape(v)
            videos.append(v)
            
        video_url = videos[0]
        print("Testing TRULY RESTORED URL:", video_url)
        
        req2 = urllib.request.Request(video_url, headers=headers)
        try:
            with urllib.request.urlopen(req2) as res2:
                print("Download success! Status:", res2.status)
        except Exception as e:
            print("Download failed:", e)

if __name__ == '__main__':
    test_meta_ai_download()
