import requests
import json
import sys

API_URL = "http://localhost:8001/api/info"
PLAYLIST_URL = "https://open.spotify.com/playlist/0gnca9xextwxYpV39WwurS?si=e86ac7ab59ac403b"

def verify_playlist():
    print(f"Fetching info for: {PLAYLIST_URL}")
    try:
        response = requests.post(
            API_URL,
            json={"url": PLAYLIST_URL}
        )
        response.raise_for_status()
        data = response.json()
        
        print("\nResponse Status Code:", response.status_code)
        print("Response Type:", data.get("type"))
        
        playlist_data = data.get("data", {})
        print("\nPlaylist Data Keys:", list(playlist_data.keys()))
        print("Title:", playlist_data.get("title"))
        print("Cover URL:", playlist_data.get("cover_url"))
        print("URL:", playlist_data.get("url"))
        print("Tracks Count:", len(playlist_data.get("tracks", [])))
        
        if "title" in playlist_data and "cover_url" in playlist_data and "url" in playlist_data:
            print("\nSUCCESS: Playlist metadata found.")
            return True
        else:
            print("\nFAILURE: Missing playlist metadata.")
            print("Full Data:", json.dumps(data, indent=2))
            return False
            
    except Exception as e:
        print(f"Verification failed: {e}")
        if hasattr(e, 'response') and e.response:
            print("Error Response:", e.response.text)
        return False

if __name__ == "__main__":
    success = verify_playlist()
    sys.exit(0 if success else 1)
