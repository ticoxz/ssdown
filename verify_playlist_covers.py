import requests
import json
import sys

API_URL = "http://localhost:8001/api/info"
PLAYLIST_URL = "https://open.spotify.com/playlist/0gnca9xextwxYpV39WwurS?si=e86ac7ab59ac403b"

def verify_covers():
    print(f"Fetching info for: {PLAYLIST_URL}")
    try:
        response = requests.post(
            API_URL,
            json={"url": PLAYLIST_URL}
        )
        response.raise_for_status()
        data = response.json()
        
        playlist_data = data.get("data", {})
        tracks = playlist_data.get("tracks", [])
        
        print(f"Found {len(tracks)} tracks.")
        
        missing_covers = 0
        for i, track in enumerate(tracks[:1]):
            print(f"COVER_ART: {track.get('cover_art')}")
            if not track.get('cover_art'):
                missing_covers += 1
                
        if missing_covers > 0:
            print(f"\nFAILURE: Found tracks without cover_url.")
            return False
            
        print("\nSUCCESS: Tracks have cover_url.")
        return True

    except Exception as e:
        print(f"Verification failed: {e}")
        return False

if __name__ == "__main__":
    success = verify_covers()
    sys.exit(0 if success else 1)
