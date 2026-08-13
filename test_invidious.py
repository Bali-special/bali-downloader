import requests
video_id = "dQw4w9WgXcQ"
apis = [
    f"https://vid.puffyan.us/api/v1/videos/{video_id}",
    f"https://invidious.nerdvpn.de/api/v1/videos/{video_id}",
    f"https://invidious.privacydev.net/api/v1/videos/{video_id}"
]

for api in apis:
    try:
        r = requests.get(api, timeout=10)
        print(f"{api} -> Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            formats = data.get('formatStreams', [])
            if formats:
                print(f"Success! Found {len(formats)} streams. Best: {formats[-1]['url'][:50]}...")
            else:
                print("No formatStreams found.")
    except Exception as e:
        print(f"{api} -> Error: {e}")
