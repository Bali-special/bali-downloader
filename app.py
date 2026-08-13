import os
import sys
import logging
import html
import re
import urllib.request
import urllib.parse
import json
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import yt_dlp
from yt_dlp.networking.impersonate import ImpersonateTarget

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()
API_KEY = os.getenv("API_KEY")

app = Flask(__name__)
# Enable CORS for all routes so our Flutter app can communicate with it
CORS(app)

@app.route('/')
def index():
    return jsonify({'status': 'ok', 'message': 'Super Downloader Backend is running!'})

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["50 per minute"],
    storage_uri="memory://",
)

@app.before_request
def require_api_key():
    if request.method != 'OPTIONS' and request.path.startswith('/api/'):
        provided_key = request.headers.get('x-api-key')
        if not API_KEY or provided_key != API_KEY:
            logger.warning(f"Unauthorized access attempt from {get_remote_address()}")
            return jsonify({'error': 'Unauthorized: Invalid API Key'}), 401

@app.route('/api/extract', methods=['POST'])
def extract_video():
    try:
        return extract_video_internal()
    except Exception as fatal_error:
        logger.error(f"FATAL unhandled exception in extract_video: {fatal_error}", exc_info=True)
        return jsonify({
            'error': str(fatal_error),
            'details': 'A critical error occurred processing your request.'
        }), 400

def extract_video_internal():
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({'error': 'URL parameter is required'}), 400

    url = data['url'].strip()
    lang = data.get('lang', 'ar')
    logger.info(f"Extracting video from URL: {url} (lang: {lang})")

    # Custom extraction for Meta AI
    if 'meta.ai' in url:
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
            }
            response = requests.get(url, headers=headers, timeout=15)
            html_content = response.text
            
            # Find title
            title_match = re.search(r'<title>(.*?)</title>', html_content)
            title = html.unescape(title_match.group(1)) if title_match else 'Meta AI Video'
            
            # Find thumbnail
            thumb_match = re.search(r'<meta property="og:image" content="([^"]+)"', html_content)
            thumbnail = html.unescape(thumb_match.group(1)) if thumb_match else ''
            
            # Find video URL via og:video or fallback regex
            video_match = re.search(r'<meta\s+property=["\']og:video(?::secure_url)?["\']\s+content=["\']([^"\']+)["\']', html_content, re.IGNORECASE)
            if not video_match:
                video_matches = re.findall(r'(https://[^"\']+\.mp4[^"\']*)', html_content)
                if not video_matches:
                    logger.error(f"Meta AI Extraction failed. Could not find any video tag or .mp4 URL.")
                    logger.error(f"Meta AI HTML Response (First 1000 chars): {html_content[:1000]}")
                    return jsonify({'error': 'Could not find video in Meta AI page'}), 400
                v = video_matches[0].replace('\\u0026amp;', '&').replace('\\u0026', '&')
                v = html.unescape(v)
            else:
                v = html.unescape(video_match.group(1))
            
            result = {
                'url': v,
                'title': title,
                'thumbnail': thumbnail,
                'duration': 0,
                'extractor': 'Meta AI',
                'uploader': 'Meta AI User',
                'ext': 'mp4',
                'http_headers': headers,
                'original_url': url
            }
            logger.info(f"Successfully extracted Meta AI video: {title}")
            return jsonify(result)
        except requests.exceptions.RequestException as e:
            err_text = e.response.text if getattr(e, 'response', None) else 'No response body'
            logger.error(f"Meta AI network error: {e}, Response: {err_text}")
            return jsonify({'error': f"Meta AI Request Failed: {str(e)}"}), 400
        except Exception as e:
            logger.error(f"Error extracting Meta AI video: {e}")
            return jsonify({'error': str(e)}), 400

    # Primary extraction for social platforms via Cobalt/Piped/Invidious APIs (Render Datacenter IPs are blocked)
    social_domains = [
        'youtube.com', 'youtu.be', 'facebook.com', 'fb.watch', 'fb.com', 
        'instagram.com', 'twitter.com', 'x.com', 'reddit.com', 'pinterest.com', 'pin.it',
        'tiktok.com', 'dailymotion.com', 'dai.ly'
    ]
    if any(domain in url for domain in social_domains):
        instances = [
            ("cobalt", "https://co.wuk.sh"),
            ("cobalt", "https://cobalt.ooguy.com"),
            ("cobalt", "https://cobalt.kwiatekmr.me"),
            ("cobalt", "https://dl.khub.app")
        ]
        
        # YouTube has dedicated Invidious and Piped instances that we prioritize
        if 'youtube.com' in url or 'youtu.be' in url:
            instances = [
                ("invidious", "https://vid.puffyan.us"),
                ("invidious", "https://invidious.nerdvpn.de"),
                ("invidious", "https://invidious.privacydev.net"),
                ("piped", "https://pipedapi.kavin.rocks"),
                ("piped", "https://pipedapi.syncpundit.io")
            ] + instances

        for inst_type, api_base in instances:
            try:
                if inst_type == "invidious":
                    video_id = None
                    if 'youtu.be/' in url: video_id = url.split('youtu.be/')[1].split('?')[0]
                    elif 'youtube.com/watch' in url: video_id = urllib.parse.parse_qs(urllib.parse.urlparse(url).query).get('v', [None])[0]
                    elif 'youtube.com/shorts/' in url: video_id = url.split('youtube.com/shorts/')[1].split('?')[0]
                    
                    if not video_id: continue
                        
                    res = requests.get(f"{api_base}/api/v1/videos/{video_id}", timeout=10)
                    res.raise_for_status()
                    data = res.json()
                    formats = data.get('formatStreams', [])
                    if formats:
                        video_url = formats[-1].get('url') # Get highest quality format
                        if video_url:
                            result = {
                                'url': video_url,
                                'title': data.get('title', 'Video (Invidious)'),
                                'thumbnail': data.get('videoThumbnails', [{}])[0].get('url', ''),
                                'duration': data.get('lengthSeconds', 0),
                                'extractor': f'YouTube (Invidious - {api_base})',
                                'uploader': data.get('author', ''),
                                'ext': 'mp4',
                                'http_headers': {},
                                'original_url': url,
                                'requires_proxy': False
                            }
                            logger.info(f"Successfully extracted video via {api_base} directly")
                            return jsonify(result)

                elif inst_type == "piped":
                    video_id = None
                    if 'youtu.be/' in url:
                        video_id = url.split('youtu.be/')[1].split('?')[0]
                    elif 'youtube.com/watch' in url:
                        parsed_url = urllib.parse.urlparse(url)
                        video_id = urllib.parse.parse_qs(parsed_url.query).get('v', [None])[0]
                    elif 'youtube.com/shorts/' in url:
                        video_id = url.split('youtube.com/shorts/')[1].split('?')[0]
                        
                    if not video_id:
                        continue
                        
                    piped_api = f"{api_base}/streams/{video_id}"
                    res = requests.get(piped_api, timeout=10)
                    res.raise_for_status()
                    data = res.json()
                    
                    streams = data.get('videoStreams', [])
                    if streams:
                        valid_streams = [s for s in streams if not s.get('videoOnly') and s.get('format') == 'MPEG_4']
                        if not valid_streams:
                            valid_streams = [s for s in streams if not s.get('videoOnly')]
                            
                        if valid_streams:
                            valid_streams.sort(key=lambda x: int(str(x.get('quality', '0')).replace('p','')) if str(x.get('quality', '0')).replace('p','').isdigit() else 0, reverse=True)
                            video_url = valid_streams[0].get('url')
                            
                            if video_url:
                                result = {
                                    'url': video_url,
                                    'title': data.get('title', 'Video (Piped)'),
                                    'thumbnail': data.get('thumbnailUrl', ''),
                                    'duration': data.get('duration', 0),
                                    'extractor': f'YouTube (Piped - {api_base})',
                                    'uploader': data.get('uploader', ''),
                                    'ext': 'mp4',
                                    'http_headers': {},
                                    'original_url': url,
                                    'requires_proxy': False
                                }
                                logger.info(f"Successfully extracted video via {api_base} directly")
                                return jsonify(result)
                                
                elif inst_type == "cobalt":
                    # Cobalt handles almost all social platforms
                    headers = {
                        'Accept': 'application/json',
                        'Content-Type': 'application/json',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                    }
                    payload = {'url': url}
                    res = requests.post(api_base, json=payload, headers=headers, timeout=10)
                    res.raise_for_status()
                    cobalt_data = res.json()
                    
                    video_url = cobalt_data.get('url')
                    if video_url:
                        result = {
                            'url': video_url,
                            'title': 'Social Video (Cobalt)',
                            'thumbnail': '',
                            'duration': 0,
                            'extractor': f'Cobalt ({api_base})',
                            'uploader': '',
                            'ext': 'mp4',
                            'http_headers': {},
                            'original_url': url,
                            'requires_proxy': False
                        }
                        logger.info(f"Successfully extracted video via Cobalt ({api_base})")
                        return jsonify(result)
                    else:
                        logger.error(f"Cobalt {api_base} succeeded but returned no 'url'. Response: {json.dumps(cobalt_data)}")
            except requests.exceptions.RequestException as e:
                err_text = e.response.text if getattr(e, 'response', None) else 'No response body'
                logger.error(f"EXPLICIT LOG: Fallback {inst_type} network error on {api_base}. Status Code: {getattr(e.response, 'status_code', 'N/A')}. Response Body: {err_text}")
                print(f"FAILED {inst_type} {api_base} -> Status: {getattr(e.response, 'status_code', 'N/A')} Body: {err_text}")
            except Exception as e:
                logger.error(f"EXPLICIT LOG: Fallback {inst_type} extraction failed on {api_base}: {str(e)}")
                print(f"FAILED {inst_type} {api_base} -> Exception: {str(e)}")
        logger.warning("All Fallbacks failed. Falling back to yt-dlp.")


    ydl_opts = {
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'no_color': True,
        'geo_bypass': True,
        'extractor_args': {'youtube': {'player_client': ['android', 'ios']}}
    }

    # Use impersonation and headers for sites that need it to bypass bot detection (YouTube, TikTok, Facebook).
    # However, Reddit's API blocks requests that have forced user-agents or impersonation.
    if 'reddit.com' not in url:
        ydl_opts['impersonate'] = ImpersonateTarget(client='chrome')
        ydl_opts['http_headers'] = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,ar;q=0.8',
            'Sec-Fetch-Mode': 'navigate'
        }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extract info without downloading
            info = ydl.extract_info(url, download=False)
            
            # Reject live streams
            if info.get('is_live'):
                return jsonify({'error': 'Cannot download live streams. Please provide a link to a recorded video.' if lang == 'en' else 'لا يمكن تنزيل البث المباشر. يرجى توفير رابط لمقطع فيديو مسجل.'}), 400

            # Resolve the best video stream URL
            video_url = info.get('url')
            requires_proxy = False
            
            # Check root info attributes
            protocol = info.get('protocol', '')
            ext = info.get('ext', '')
            acodec = info.get('acodec')
            vcodec = info.get('vcodec')
            
            needs_proxy = (
                not video_url or 
                'm3u8' in protocol or 'mpd' in protocol or 
                'm3u8' in ext or 
                (video_url and ('.m3u8' in video_url or '.mpd' in video_url or 'manifest' in video_url)) or
                acodec == 'none' or vcodec == 'none'
            )
            
            if needs_proxy:
                formats = info.get('formats', [])
                playable_formats = [
                    f for f in formats 
                    if f.get('acodec') != 'none' and f.get('vcodec') != 'none' and f.get('url') and 'm3u8' not in f.get('protocol', '') and 'm3u8' not in f.get('ext', '')
                ]
                if playable_formats:
                    # Pick the best resolution format
                    playable_formats.sort(key=lambda x: x.get('width', 0) or 0, reverse=True)
                    video_url = playable_formats[0]['url']
                    requires_proxy = False
                else:
                    # Fallback to proxy to let yt-dlp merge formats
                    video_url = 'proxy'
                    requires_proxy = True
            
            if video_url == 'proxy':
                # If we still don't have a direct playable URL, or it's an m3u8 playlist,
                # we must use the proxy to download and merge using ffmpeg on the backend.
                video_url = 'proxy'
                requires_proxy = True

            # Formulate the response metadata
            result = {
                'url': video_url,
                'title': info.get('title', 'Social Media Video'),
                'description': info.get('description', ''),
                'thumbnail': info.get('thumbnail', ''),
                'duration': info.get('duration', 0),  # in seconds
                'extractor': info.get('extractor_key', 'Generic'),
                'uploader': info.get('uploader', ''),
                'ext': info.get('ext', 'mp4') if not requires_proxy else 'mp4',
                'http_headers': info.get('http_headers', {}),
                'original_url': url,
                'requires_proxy': requires_proxy
            }
            
            logger.info(f"Successfully extracted: {result['title']} ({result['extractor']})")
            return jsonify(result)

    except Exception as e:
        error_msg = str(e)
                
        # Remove ANSI color codes manually just in case yt-dlp ignores no_color in exception string
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        error_msg = ansi_escape.sub('', error_msg)
        
        if 'No video formats found' in error_msg or 'Requested format is not available' in error_msg or 'Sign in to confirm' in error_msg:
            messages = {
                'en': 'This link does not contain a playable video, or the platform blocked access (e.g. requires login/captcha).',
                'ar': 'هذا الرابط لا يحتوي على مقطع فيديو قابل للتشغيل، أو أن المنصة حظرت الوصول (قد يتطلب تسجيل الدخول).'
            }
            error_msg = messages.get(lang, messages['ar'])
            
        logger.error(f"Error extracting video from {url}: {error_msg}")
        # Always return 400 for extraction failures so the app doesn't trigger 500 error handlers
        return jsonify({
            'error': error_msg,
            'details': 'Extraction failed. Please check the URL or try again later.'
        }), 400

from werkzeug.exceptions import HTTPException

@app.errorhandler(Exception)
def handle_exception(e):
    # pass through HTTP errors (like 404, 405)
    if isinstance(e, HTTPException):
        return jsonify({'error': str(e)}), e.code
        
    logger.error(f"Unhandled server error: {str(e)}")
    return jsonify({
        'error': f"Internal Server Error: {str(e)}"
    }), 500

from flask import Response, stream_with_context, send_file
import urllib.request
import urllib.parse
from urllib.error import HTTPError, URLError
import tempfile
import threading
import time

@app.route('/api/proxy')
def proxy_download():
    video_url = request.args.get('url')
    if not video_url:
        return "Missing url parameter", 400

    logger.info(f"Proxying download for: {video_url}")
    
    # We will use yt-dlp to download the video to a temp file first
    # This guarantees we bypass any 403s because yt-dlp handles cookies/headers internally
    try:
        temp_dir = tempfile.gettempdir()
        temp_filename = os.path.join(temp_dir, f"proxy_{int(time.time())}.mp4")
        
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': temp_filename,
            'quiet': True,
            'no_warnings': True,
            'geo_bypass': True,
        }
        
        if 'reddit.com' not in video_url:
            ydl_opts['impersonate'] = ImpersonateTarget(client='chrome')
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
            
        if not os.path.exists(temp_filename):
            return "Download failed", 500
            
        # Send the file and clean it up after a delay
        def cleanup_temp():
            time.sleep(600) # Delete after 10 mins
            try:
                if os.path.exists(temp_filename):
                    os.remove(temp_filename)
            except:
                pass
                
        threading.Thread(target=cleanup_temp, daemon=True).start()
        
        return send_file(temp_filename, as_attachment=True, download_name="video.mp4")
        
    except Exception as e:
        logger.error(f"Proxy error: {str(e)}")
        return str(e), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'message': 'Super Downloader extraction backend is running'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting backend on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=True)
