import requests
import json
import time

url = "https://soundcloud.com/keeton-schaff/sets/october?si=2741fb4b578840b2a150c54fa97fc3e0&utm_source=clipboard&utm_medium=text&utm_campaign=social_sharing"
api_url = "http://localhost:8001/api/download"
progress_url = "http://localhost:8001/api/progress/"

print(f"Testing /api/download with URL: {url}")
try:
    # 1. Start Download
    response = requests.post(api_url, json={"spotify_url": url, "quality": "320K"})
    print(f"Start Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        task_id = data.get('task_id')
        print(f"Task ID: {task_id}")
        
        if task_id:
            # 2. Poll Progress
            print("Polling progress...")
            for i in range(20): # Poll for 20 seconds max for testing
                res = requests.get(progress_url + task_id)
                if res.status_code == 200:
                    prog = res.json()
                    print(f"Progress: {prog}")
                    if prog.get('status') == 'completed':
                        print("Download completed!")
                        break
                    elif prog.get('status') == 'error':
                        print(f"Download error: {prog.get('error')}")
                        break
                else:
                    print(f"Poll Error: {res.status_code}")
                time.sleep(1)
        else:
            print("No task_id received")
    else:
        print(f"Error: {response.text}")

except Exception as e:
    print(f"Exception: {e}")
