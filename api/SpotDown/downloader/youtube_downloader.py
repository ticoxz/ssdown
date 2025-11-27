# 05.04.2024

import logging
import os
from typing import Dict, Optional, Callable
import traceback

# External imports
import httpx
import yt_dlp
from rich.console import Console

# Internal utils
from SpotDown.utils.os import file_utils
from SpotDown.utils.config_json import config_manager
from SpotDown.helpers.ffmpeg import convert_to_jpg_with_ffmpeg, add_cover_art

# Variable
console = Console()
allow_metadata = config_manager.get("DOWNLOAD", "allow_metadata")
auto_first = config_manager.get("DOWNLOAD", "auto_first")


class YouTubeDownloader:
    def download(self, video_info: Dict, spotify_info: Dict, quality: str = "320K", progress_hook: Optional[Callable] = None) -> bool:
        """
        Download YouTube video as mp3 using yt_dlp library

        Args:
            video_info (Dict): YouTube video info
            spotify_info (Dict): Spotify track info
            quality (str): Audio quality (e.g. "320K", "192K")
            progress_hook (Callable): Function to call with progress updates

        Returns:
            bool: True if download succeeded
        """
        try:
            music_folder = file_utils.get_music_folder()
            filename = file_utils.create_filename(
                spotify_info.get('artist', 'Unknown Artist'),
                spotify_info.get('title', video_info.get('title', 'Unknown Title'))
            )
            # yt-dlp template for filename
            output_template = str(music_folder / f"{filename}.%(ext)s")
            
            logging.info(f"Start download: {video_info.get('url')} as {output_template}")

            # Download cover image if available
            cover_path = None
            if allow_metadata:
                cover_url = spotify_info.get('cover_url')
                if cover_url:
                    try:
                        cover_path = music_folder / f"{filename}_cover.jpg"
                        with httpx.Client(timeout=10) as client:
                            resp = client.get(cover_url)
                            if resp.status_code == 200:
                                
                                # Check if it's WebP or needs conversion
                                content_type = resp.headers.get("content-type", "").lower()
                                is_webp = content_type.endswith("webp") or cover_url.lower().endswith(".webp")
                                
                                if is_webp or not content_type.startswith("image/jpeg"):
                                    
                                    # Use ffmpeg for conversion to JPG
                                    if convert_to_jpg_with_ffmpeg(resp.content, cover_path):
                                        if not auto_first:
                                            console.print(f"[blue]Downloaded and converted thumbnail: {cover_path}[/blue]")
                                        logging.info(f"Downloaded and converted thumbnail: {cover_path}")
                                    else:
                                        cover_path = None
                                        logging.warning("Failed to convert image with ffmpeg")

                                else:
                                    # Direct save for JPG images
                                    with open(cover_path, 'wb') as f:
                                        f.write(resp.content)

                                    if not auto_first:
                                        console.print(f"[blue]Downloaded thumbnail: {cover_path}[/blue]")
                                    logging.info(f"Downloaded thumbnail: {cover_path}")

                            else:
                                cover_path = None
                                logging.warning(f"Failed to download cover image, status code: {resp.status_code}")
                                
                    except Exception as e:
                        if not auto_first:
                            console.print(f"[yellow]Unable to download cover: {e}[/yellow]")
                        logging.error(f"Unable to download cover: {e}")
                        cover_path = None

            # Configure yt-dlp options
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': output_template,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': quality.replace('K', ''),
                }],
                'ffmpeg_location': file_utils.ffmpeg_path,
                'quiet': True,
                'no_warnings': True,
                'noplaylist': True,
                'verbose': True # Enable verbose logging
            }
            
            logging.info(f"DEBUG: ffmpeg_path: {file_utils.ffmpeg_path}")
            logging.info(f"DEBUG: ydl_opts: {ydl_opts}")

            if allow_metadata:
                ydl_opts['writethumbnail'] = False 
                ydl_opts['postprocessors'].append({'key': 'FFmpegMetadata', 'add_metadata': True})
            
            # Add progress hook if provided
            if progress_hook:
                ydl_opts['progress_hooks'] = [progress_hook]

            # Run download
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_info['url']])

            # Check if file exists
            final_filename = f"{filename}.mp3"
            downloaded_file = music_folder / final_filename
            
            if downloaded_file.exists():
                if not auto_first:
                    console.print("[red]Download completed![/red]")
                logging.info(f"Download completed: {downloaded_file}")

                # Manually embed cover art if available
                if cover_path and cover_path.exists():
                    try:
                        if add_cover_art(downloaded_file, cover_path):
                            logging.info(f"Embedded cover art into {downloaded_file}")
                        else:
                            logging.warning("Failed to embed cover art")
                            
                        # Cleanup cover file
                        cover_path.unlink()
                        logging.info(f"Removed temporary cover file: {cover_path}")
                    except Exception as ex:
                        logging.warning(f"Failed to process cover art: {ex}")

                return True
            else:
                logging.error("Download apparently succeeded but file not found")
                return False

        except Exception as e:
            if not auto_first:
                console.print(f"[red]Error during download: {e}[/red]")
            logging.error(f"Error during download: {e}")
            traceback.print_exc()
            return False