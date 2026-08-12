import urllib.request
import re

url = "https://www.meta.ai/@hectornavarro887/post/ON4Dkwq34Ol?open_in_meta_ai=true&utm_source=android_meta_ai_sl"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}

req = urllib.request.Request(url, headers=headers)
try:
    with urllib.request.urlopen(req) as response:
        html = response.read().decode('utf-8')
        
        # Look for video URLs that end in .mp4 or .webm but might have query parameters
        video_matches = re.findall(r'(https://[^"\']+\.mp4[^"\']*)', html)
        
        # Decode JSON unicode escapes (e.g. \u0026 -> &)
        videos = []
        for v in video_matches:
            v = v.replace('\\u0026', '&').replace('\\u0026amp;', '&')
            videos.append(v)
            
        print("Found videos:", len(videos))
        if videos:
            print("First video URL:", videos[0])
            
            # Let's test downloading a tiny chunk of the first video
            req2 = urllib.request.Request(videos[0], headers=headers)
            with urllib.request.urlopen(req2) as res2:
                print("Video response:", res2.status, res2.headers.get('Content-Type'))
except Exception as e:
    print(f"Error fetching: {e}")
