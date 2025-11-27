import requests
import time
import sys

API_URL = "http://localhost:8001"
# A short song or a known track
SPOTIFY_URL = "https://open.spotify.com/track/4cOdK2wGLETKBW3PvgPWqT?si=8c5b5b5b5b5b5b5b" 

def verify_download():
    print(f"Testing /api/download with URL: {SPOTIFY_URL}")
    try:
        # 1. Start Download
        response = requests.post(
            f"{API_URL}/api/download",
            json={"spotify_url": SPOTIFY_URL, "quality": "320K"}
        )
        print(f"Start Status Code: {response.status_code}")
        if response.status_code != 200:
            print(f"Start Response: {response.text}")
            return False
            
        data = response.json()
        task_id = data.get("task_id")
        print(f"Task ID: {task_id}")
        
        if not task_id:
            print("No task_id returned")
            return False

        # 2. Poll Progress
        print("Polling progress...")
        for _ in range(60): # Wait up to 60 seconds
            progress_res = requests.get(f"{API_URL}/api/progress/{task_id}")
            if progress_res.status_code == 200:
                progress_data = progress_res.json()
                status = progress_data.get("status")
                percent = progress_data.get("percent", 0)
                print(f"Status: {status}, Percent: {percent}%")
                
                if status == "completed":
                    print("Download completed!")
                    return True
                if status == "error":
                    print(f"Download failed: {progress_data.get('error')}")
                    return False
            else:
                print(f"Progress Error: {progress_res.status_code}")
            
            time.sleep(1)
            
        print("Timeout waiting for download")
        return False

    except Exception as e:
        print(f"Exception: {e}")
        return False

if __name__ == "__main__":
    success = verify_download()
    sys.exit(0 if success else 1)
