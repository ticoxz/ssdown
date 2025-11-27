import requests
import json
import time

url = "https://soundcloud.com/keeton-schaff/sets/october?si=2741fb4b578840b2a150c54fa97fc3e0&utm_source=clipboard&utm_medium=text&utm_campaign=social_sharing"
api_url = "http://localhost:8001/api/info"

print(f"Testing /api/info with URL: {url}")
try:
    response = requests.post(api_url, json={"url": url})
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Type: {data.get('type')}")
        print(f"Count: {data.get('count')}")
        if 'data' in data:
            print(f"Title: {data['data'].get('title')}")
            if 'tracks' in data['data']:
                print(f"Tracks found: {len(data['data']['tracks'])}")
                print("First track sample:")
                print(json.dumps(data['data']['tracks'][0], indent=2))
            else:
                print("No tracks found in data")
        else:
            print("No data field in response")
    else:
        print(f"Error: {response.text}")

except Exception as e:
    print(f"Exception: {e}")
