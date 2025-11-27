import sys
import os

# Add api directory to path
sys.path.insert(0, os.path.join(os.getcwd(), 'api'))

from SpotDown.utils.os import file_utils

print("Checking FFmpeg...")
file_utils.get_system_summary()
print(f"FFmpeg Path: {file_utils.ffmpeg_path}")

if file_utils.ffmpeg_path and os.path.exists(file_utils.ffmpeg_path):
    print("FFmpeg found and exists.")
else:
    print("FFmpeg NOT found or does not exist.")
