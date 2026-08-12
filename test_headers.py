import yt_dlp
import json

ydl_opts = {'quiet': True, 'skip_download': True, 'cookiesfrombrowser': ('chrome',)}
with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    info = ydl.extract_info('https://www.youtube.com/watch?v=jNQXAC9IVRw', download=False)
    print(json.dumps(info.get('http_headers', {})))
