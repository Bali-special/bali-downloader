import urllib.request
import json
import requests
import re
import html
from urllib.parse import urlparse, parse_qs

def extract_youtube_piped(url):
    # Get video_id
    video_id = None
    if 'youtu.be/' in url:
        video_id = url.split('youtu.be/')[1].split('?')[0]
    elif 'youtube.com/watch' in url:
        parsed_url = urlparse(url)
        video_id = parse_qs(parsed_url.query).get('v', [None])[0]
    elif 'youtube.com/shorts/' in url:
        video_id = url.split('youtube.com/shorts/')[1].split('?')[0]
        
    if not video_id:
        return "Could not find video ID"
        
    api_url = f"https://pipedapi.kavin.rocks/streams/{video_id}"
    try:
        res = requests.get(api_url, timeout=10)
        res.raise_for_status()
        data = res.json()
        
        # Piped returns videoStreams
        streams = data.get('videoStreams', [])
        if not streams:
            return "No streams found"
            
        # Get 1080p or 720p mp4 stream with both video and audio (if available, otherwise we might need proxy)
        # Piped separates video and audio, but some streams have both (videoOnly=False).
        # Actually piped usually provides mixed formats for lower qualities, and videoOnly for 1080p.
        valid_streams = [s for s in streams if not s.get('videoOnly') and s.get('format') == 'MPEG_4']
        if not valid_streams:
            valid_streams = [s for s in streams if not s.get('videoOnly')]
            
        if valid_streams:
            valid_streams.sort(key=lambda x: x.get('quality', '0').replace('p',''), reverse=True)
            return valid_streams[0]['url']
        else:
            return "No mixed streams found"
    except Exception as e:
        return str(e)

def extract_dailymotion(url):
    video_id = None
    if 'dai.ly/' in url:
        video_id = url.split('dai.ly/')[1].split('?')[0]
    elif 'dailymotion.com/video/' in url:
        video_id = url.split('dailymotion.com/video/')[1].split('?')[0]
        
    if not video_id:
        return "Could not find Dailymotion video ID"
        
    embed_url = f"https://www.dailymotion.com/embed/video/{video_id}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    try:
        res = requests.get(embed_url, headers=headers, timeout=10)
        res.raise_for_status()
        html_content = res.text
        
        # Search for "__PLAYER_CONFIG__ = {" or similar
        # Dailymotion embed config is usually stored in a script tag
        config_match = re.search(r'__PLAYER_CONFIG__\s*=\s*(\{.*?\});', html_content)
        if config_match:
            config = json.loads(config_match.group(1))
            qualities = config.get('metadata', {}).get('qualities', {})
            if 'auto' in qualities:
                for item in qualities['auto']:
                    if item.get('type') == 'application/x-mpegURL':
                        return item.get('url')
                        
        return "Could not find stream URL in Dailymotion embed"
    except Exception as e:
        return str(e)

def extract_meta_ai(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }
    try:
        res = requests.get(url, headers=headers, timeout=15)
        html_content = res.text
        
        # Look for <meta property="og:video" content="..."> or <meta property="og:video:secure_url" content="...">
        video_match = re.search(r'<meta\s+property=["\']og:video(?::secure_url)?["\']\s+content=["\']([^"\']+)["\']', html_content, re.IGNORECASE)
        if video_match:
            video_url = html.unescape(video_match.group(1))
            return video_url
            
        return "Could not find og:video in Meta AI page"
    except Exception as e:
        return str(e)

print("YouTube:", extract_youtube_piped("https://www.youtube.com/watch?v=dQw4w9WgXcQ"))
print("Dailymotion:", extract_dailymotion("https://www.dailymotion.com/video/x8jxvnm"))
print("Meta AI:", extract_meta_ai("https://www.meta.ai/shared/fake_url"))
