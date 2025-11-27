import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv

load_dotenv()

def debug_spotify():
    client_id = os.getenv("SPOTIPY_CLIENT_ID")
    client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        print("Missing credentials")
        return

    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
        client_id=client_id,
        client_secret=client_secret
    ))
    
    playlist_id = "0gnca9xextwxYpV39WwurS" # The playlist used before
    
    print("Fetching playlist items...")
    results = sp.playlist_items(
        playlist_id,
        limit=1,
        fields='items(track(name,artists(name),album(name,release_date,images),duration_ms))'
    )
    
    if results['items']:
        item = results['items'][0]
        track = item['track']
        print(f"Track: {track['name']}")
        print(f"Album: {track['album']['name']}")
        print(f"Album Images: {track['album'].get('images')}")
    else:
        print("No items found")

if __name__ == "__main__":
    debug_spotify()
