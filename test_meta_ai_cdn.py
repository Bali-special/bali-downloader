import yt_dlp
import re
import urllib.request
import urllib.parse

def test_yt_dlp_cdn():
    url = "https://www.meta.ai/@hectornavarro887/post/ON4Dkwq34Ol?open_in_meta_ai=true&utm_source=android_meta_ai_sl"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    }

    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response:
        html = response.read().decode('utf-8')
        video_matches = re.findall(r'(https://[^"\']+\.mp4[^"\']*)', html)
        videos = []
        for v in video_matches:
            v = v.replace('\\u0026', '&').replace('\\u0026amp;', '&')
            videos.append(v)
            
        print("Found video:", videos[0])
        
        # Test yt-dlp on the CDN link!
        ydl_opts = {'quiet': True, 'skip_download': True}
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(videos[0], download=False)
                print("yt-dlp success:", info.get('url'))
        except Exception as e:
            print("yt-dlp failed:", e)

if __name__ == '__main__':
    test_yt_dlp_cdn()
