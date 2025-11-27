# 05.04.2024

import os
import re
import sys
import json
import logging
from typing import Dict, List, Optional
from dotenv import load_dotenv


# External library
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from rich.console import Console
from rich.progress import Progress


# Variable
console = Console()
load_dotenv()


def extract_track_id(spotify_url):
    patterns = [
        r'track/([a-zA-Z0-9]{22})',
        r'spotify:track:([a-zA-Z0-9]{22})'
    ]
    for pattern in patterns:
        match = re.search(pattern, spotify_url)
        if match:
            return match.group(1)
    return None


def extract_playlist_id(spotify_url):
    patterns = [
        r'playlist/([a-zA-Z0-9]{22})',
        r'spotify:playlist:([a-zA-Z0-9]{22})'
    ]
    for pattern in patterns:
        match = re.search(pattern, spotify_url)
        if match:
            return match.group(1)
    return None


def extract_album_id(spotify_url):
    patterns = [
        r'album/([a-zA-Z0-9]{22})',
        r'spotify:album:([a-zA-Z0-9]{22})'
    ]
    for pattern in patterns:
        match = re.search(pattern, spotify_url)
        if match:
            return match.group(1)
    return None


class SpotifyExtractor:
    def __init__(self):
        client_id = os.getenv("SPOTIPY_CLIENT_ID")
        client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")

        if not client_id or not client_secret:
            raise ValueError("Faltan las credenciales de Spotify. Configúralas en la web.")

        try:
            self.sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
                client_id=client_id,
                client_secret=client_secret
            ))
            logging.info("SpotifyExtractor initialized")
        except Exception as e:
            logging.error(f"Spotify init error: {e}")
            raise ValueError("Credenciales de Spotify inválidas. Verifícalas en Configuración.")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def extract_track_info(self, spotify_url: str) -> Optional[Dict]:
        track_id = extract_track_id(spotify_url)

        if not track_id:
            logging.error("Invalid Spotify URL")
            return None

        try:
            track = self.sp.track(track_id)
            
            # Extract album info
            album = track['album']
            release_date = album['release_date']
            year = release_date.split('-')[0] if release_date else None

            # Extract duration in seconds
            duration_ms = track['duration_ms']
            duration_seconds = duration_ms // 1000 if duration_ms else None

            # Extract cover URL
            cover_url = album['images'][0]['url'] if album['images'] else None

            # Extract artists
            artists = [artist['name'] for artist in track['artists']]

            track_info = {
                "title": track['name'],
                "artist": ', '.join(artists),
                "album": album['name'],
                "year": year,
                "duration_seconds": duration_seconds,
                "cover_url": cover_url,
                "url": spotify_url,
                "original_url": spotify_url
            }
            return track_info

        except Exception as e:
            logging.error(f"Error extracting track info: {e}")
            return None

    def extract_playlist_tracks(self, playlist_url: str) -> Dict:
        playlist_id = extract_playlist_id(playlist_url)

        if not playlist_id:
            logging.error("Invalid Spotify playlist URL")
            return {}
        
        try:
            # Extract playlist info
            playlist = self.sp.playlist(playlist_id)
            total_tracks = playlist['tracks']['total']
            tracks_info = []
            offset = 0
            limit = 100
            console.print(f"[green]Playlist has [red]{total_tracks}[/red] tracks.")

            with Progress() as progress:
                task = progress.add_task("[cyan]Extracting tracks...", total=total_tracks)

                while offset < total_tracks:
                    progress.update(task, advance=0, description=f"[cyan]Loading tracks {offset + 1}-{min(offset + limit, total_tracks)} of {total_tracks}...")
                    results = self.sp.playlist_items(
                        playlist_id,
                        offset=offset,
                        limit=limit,
                        fields='items(track(name,artists(name),album(name,release_date,images),duration_ms))'
                    )

                    if not results['items']:
                        break

                    for idx, item in enumerate(results['items']):
                        if item['track'] is None:
                            continue
                        
                        # Extract track details
                        track = item['track']

                        # Extract album info
                        album = track['album']

                        # Extract duration in seconds
                        duration_ms = track['duration_ms']
                        duration_seconds = duration_ms // 1000 if duration_ms else None

                        # Extract cover URL
                        cover_url = album['images'][0]['url'] if album['images'] else None

                        # Extract artists
                        artists = [artist['name'] for artist in track['artists']]

                        # Compile track info
                        track_info = {
                            "title": track['name'],
                            "artist": ', '.join(artists),
                            "album": album['name'],
                            "added_at": None,
                            "cover_art": cover_url,
                            "duration_ms": duration_ms,
                            "duration_seconds": duration_seconds,
                            "play_count": None
                        }

                        # Append to list
                        tracks_info.append(track_info)
                        progress.update(task, advance=1)
                    offset += limit

            # Remove duplicates based on title and artist
            unique = {}
            for item in tracks_info:
                key = (item.get("title", ""), item.get("artist", ""))
                if key not in unique:
                    unique[key] = item

            # Convert back to list
            unique_tracks = list(unique.values())
            console.print(f"[green]Extracted [red]{len(unique_tracks)}[/red] unique tracks from playlist")
            
            return {
                "title": playlist['name'],
                "cover_url": playlist['images'][0]['url'] if playlist['images'] else None,
                "url": playlist_url,
                "tracks": unique_tracks
            }
        
        except Exception as e:
            logging.error(f"Error extracting playlist: {e}")
            return {}

    def extract_album_tracks(self, album_url: str) -> Dict:
        album_id = extract_album_id(album_url)

        if not album_id:
            logging.error("Invalid Spotify album URL")
            return {}
        
        try:
            # Extract album info
            album = self.sp.album(album_id)
            total_tracks = album['tracks']['total']
            tracks_info = []
            offset = 0
            limit = 50 # Album tracks limit is usually 50
            console.print(f"[green]Album has [red]{total_tracks}[/red] tracks.")

            with Progress() as progress:
                task = progress.add_task("[cyan]Extracting tracks...", total=total_tracks)

                while offset < total_tracks:
                    progress.update(task, advance=0, description=f"[cyan]Loading tracks {offset + 1}-{min(offset + limit, total_tracks)} of {total_tracks}...")
                    results = self.sp.album_tracks(
                        album_id,
                        offset=offset,
                        limit=limit
                    )

                    if not results['items']:
                        break

                    for item in results['items']:
                        # Extract track details
                        # Note: album_tracks returns simplified track objects, missing album info (but we have it from album object)
                        
                        # Extract duration in seconds
                        duration_ms = item['duration_ms']
                        duration_seconds = duration_ms // 1000 if duration_ms else None

                        # Extract artists
                        artists = [artist['name'] for artist in item['artists']]

                        # Compile track info
                        track_info = {
                            "title": item['name'],
                            "artist": ', '.join(artists),
                            "album": album['name'],
                            "added_at": None,
                            "cover_art": album['images'][0]['url'] if album['images'] else None,
                            "duration_ms": duration_ms,
                            "duration_seconds": duration_seconds,
                            "play_count": None
                        }

                        # Append to list
                        tracks_info.append(track_info)
                        progress.update(task, advance=1)
                    offset += limit

            return {
                "title": album['name'],
                "cover_url": album['images'][0]['url'] if album['images'] else None,
                "url": album_url,
                "tracks": tracks_info
            }
        
        except Exception as e:
            logging.error(f"Error extracting album: {e}")
            return {}