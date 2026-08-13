import requests

url = "https://www.tiktok.com/@tiktok/video/7106594312292453678"

headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
}

print("\n--- Testing Cobalt V10 for TikTok ---")
try:
    r = requests.post("https://api.cobalt.tools/", json={"url": url}, headers=headers, timeout=10)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text}")
except Exception as e:
    print(f"Error: {e}")
