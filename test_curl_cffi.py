from curl_cffi import requests

instances = [
    "https://co.wuk.sh",
    "https://cobalt.ooguy.com",
    "https://cobalt.kwiatekmr.me",
    "https://dl.khub.app"
]

url = "https://www.tiktok.com/@tiktok/video/7106594312292453678"

headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
}

for inst in instances:
    print(f"\n--- Testing {inst} with curl_cffi ---")
    try:
        r = requests.post(inst + "/", json={"url": url}, headers=headers, impersonate="chrome110", timeout=10)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            print(f"Success! Response: {r.text[:100]}...")
        else:
            print(f"Response: {r.text}")
    except Exception as e:
        print(f"Error: {e}")
