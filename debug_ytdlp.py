import yt_dlp
import json

url = "https://soundcloud.com/keeton-schaff/sets/october?si=2741fb4b578840b2a150c54fa97fc3e0&utm_source=clipboard&utm_medium=text&utm_campaign=social_sharing"

ydl_opts = {
    'quiet': True,
    'extract_flat': 'in_playlist',
    'dump_single_json': True
}

print("Extracting info...")
with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    info = ydl.extract_info(url, download=False)
    print(f"Type: {info.get('_type')}")
    print(f"Keys: {list(info.keys())}")
    if 'entries' in info:
        print(f"Entries count: {len(info['entries'])}")
        print("First entry:", info['entries'][0])
    else:
        print("No entries found")
