import requests
import time
import sys

API_URL = "http://localhost:8000"
VIDEO_URL = "https://youtu.be/SRcnnId15BA?si=S9FehrOUNTi4YKG5"

def verify_download():
    print(f"Initiating download for: {VIDEO_URL}")
    try:
        response = requests.post(
            f"{API_URL}/api/download",
            json={"spotify_url": VIDEO_URL, "quality": "320K"}
        )
        response.raise_for_status()
        data = response.json()
        task_id = data["task_id"]
        print(f"Download started. Task ID: {task_id}")
        
        while True:
            progress_response = requests.get(f"{API_URL}/api/progress/{task_id}")
            progress_response.raise_for_status()
            progress_data = progress_response.json()
            
            status = progress_data.get("status")
            percent = progress_data.get("percent", 0)
            
            print(f"Status: {status}, Progress: {percent}%")
            
            if status == "completed":
                print("Download completed successfully!")
                return True
            elif status == "error":
                print(f"Download failed! Error: {progress_data.get('error')}")
                return False
            
            time.sleep(1)
            
    except Exception as e:
        print(f"Verification failed: {e}")
        return False

if __name__ == "__main__":
    success = verify_download()
    sys.exit(0 if success else 1)
