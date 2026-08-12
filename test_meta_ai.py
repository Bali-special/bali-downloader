import urllib.request
import re

url = "https://www.meta.ai/@hectornavarro887/post/ON4Dkwq34Ol?open_in_meta_ai=true&utm_source=android_meta_ai_sl"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
}

req = urllib.request.Request(url, headers=headers)
try:
    with urllib.request.urlopen(req) as response:
        html = response.read().decode('utf-8')
        print(f"Fetched {len(html)} bytes of HTML.")
        
        # Look for video URLs
        video_matches = re.findall(r'https?://[^"\']+\.(?:mp4|webm)', html)
        print("Found direct video URLs:", set(video_matches))
        
        # Look for og:video
        og_video = re.findall(r'<meta property="og:video" content="([^"]+)"', html)
        print("og:video:", og_video)
        
        # Look for any URL containing 'video'
        other_videos = re.findall(r'https?://[^"\']+video[^"\']+', html)
        print("Other possible video URLs:", set(other_videos))
except Exception as e:
    print(f"Error fetching: {e}")
