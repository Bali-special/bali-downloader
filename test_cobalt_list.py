import requests

instances = [
    "https://cobalt.api.timetide.xyz",
    "https://cobalt.kwiatekmr.me",
    "https://cobalt.uncensored.app",
    "https://cobalt.canine.ly",
    "https://co.eepy.moe",
    "https://cobalt.ooguy.com",
    "https://dl.khub.app"
]

url = "https://www.tiktok.com/@tiktok/video/7106594312292453678"

headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
}

for inst in instances:
    print(f"\n--- Testing {inst} ---")
    try:
        r = requests.post(inst + "/", json={"url": url}, headers=headers, timeout=5)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            print(f"Success! Response: {r.text[:100]}...")
        else:
            print(f"Response: {r.text}")
    except Exception as e:
        print(f"Error: {e}")
