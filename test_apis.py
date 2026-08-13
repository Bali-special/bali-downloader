import requests
import json

urls = [
    "https://www.tiktok.com/@tiktok/video/7106594312292453678",
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "https://www.dailymotion.com/video/x84sh87"
]

headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
}

for u in urls:
    print(f"\n--- Testing Cobalt for {u} ---")
    try:
        r = requests.post("https://api.cobalt.tools/api/json", json={"url": u}, headers=headers, timeout=10)
        print(f"Status: {r.status_code}")
        print(f"Response: {r.text}")
    except Exception as e:
        print(f"Error: {e}")

print("\n--- Testing Invidious ---")
try:
    r = requests.get("https://vid.puffyan.us/api/v1/videos/dQw4w9WgXcQ", timeout=10)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text[:300]}...")
except Exception as e:
    print(f"Error: {e}")
