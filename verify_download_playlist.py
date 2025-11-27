import requests
import time
import sys

API_URL = "http://localhost:8001"
PLAYLIST_URL = "https://open.spotify.com/playlist/0gnca9xextwxYpV39WwurS?si=e86ac7ab59ac403b"

def verify_download():
    print(f"Testing /api/download with URL: {PLAYLIST_URL}")
    try:
        # 1. Start Download
        response = requests.post(
            f"{API_URL}/api/download",
            json={"spotify_url": PLAYLIST_URL, "quality": "320K"}
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
        for _ in range(120): # Wait up to 120 seconds
            progress_res = requests.get(f"{API_URL}/api/progress/{task_id}")
            if progress_res.status_code == 200:
                progress_data = progress_res.json()
                status = progress_data.get("status")
                percent = progress_data.get("percent", 0)
                current_track = progress_data.get("current_track")
                total_tracks = progress_data.get("total_tracks")
                filename = progress_data.get("filename")
                
                print(f"Status: {status}, Track: {current_track}/{total_tracks}, File: {filename}, Percent: {percent}%")
                
                if status == "completed":
                    print("Download completed!")
                    return True
                if status == "error":
                    print(f"Download failed: {progress_data.get('error')}")
                    return False
            else:
                print(f"Progress Error: {progress_res.status_code}")
            
            time.sleep(2)
            
        print("Timeout waiting for download")
        return False

    except Exception as e:
        print(f"Exception: {e}")
        return False

if __name__ == "__main__":
    success = verify_download()
    sys.exit(0 if success else 1)
