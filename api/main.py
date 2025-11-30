import sys
import os
import uuid
from typing import Optional, List, Dict
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import logging
from dotenv import load_dotenv

# Añadir el directorio actual al path para poder importar SpotDown
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from SpotDown.extractor.spotify_extractor import SpotifyExtractor
from SpotDown.main import search_on_youtube, download_track
from SpotDown.utils.console_utils import ConsoleUtils
from SpotDown.utils.os import file_utils
from SpotDown.utils.text_parser import parse_tracklist
import SpotDown

# Configure logging
log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_path),
        logging.StreamHandler()
    ]
)

# Initialize system paths (ffmpeg, etc)
file_utils.get_system_summary()

load_dotenv()

app = FastAPI(title="SpotDown API")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global dictionary to store download progress
download_progress: Dict[str, Dict] = {}

class SpotifyUrl(BaseModel):
    url: str

class DownloadRequest(BaseModel):
    spotify_url: Optional[str] = None
    quality: str = "320K"
    tracklist_mode: bool = False
    tracks: Optional[List[Dict]] = None

class TracklistRequest(BaseModel):
    text: str

class Settings(BaseModel):
    client_id: str
    client_secret: str

@app.get("/")
def read_root():
    return {"message": "SpotDown API v2 (Multi-platform)"}

import yt_dlp

@app.post("/api/info")
def get_spotify_info(data: SpotifyUrl):
    """
    Obtiene información de una URL (Spotify, YouTube, SoundCloud, etc).
    """
    url = data.url
    console = ConsoleUtils()
    
    # Check if it's a Spotify URL
    if "spotify.com" in url:
        # Determinar tipo de URL (básico)
        if "track" in url:
            try:
                with SpotifyExtractor() as extractor:
                    info = extractor.extract_track_info(url)
                    if info:
                        return {"type": "track", "data": info}
                    else:
                        raise HTTPException(status_code=404, detail="No se pudo encontrar información de la canción")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
                
        elif "playlist" in url:
            try:
                with SpotifyExtractor() as extractor:
                    playlist_data = extractor.extract_playlist_tracks(url)
                    if playlist_data and playlist_data.get('tracks'):
                        return {"type": "playlist", "data": playlist_data, "count": len(playlist_data['tracks'])}
                    else:
                        raise HTTPException(status_code=404, detail="No se encontraron canciones en la playlist")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        elif "album" in url:
            try:
                with SpotifyExtractor() as extractor:
                    album_data = extractor.extract_album_tracks(url)
                    if album_data and album_data.get('tracks'):
                        return {"type": "playlist", "data": album_data, "count": len(album_data['tracks'])}
                    else:
                        raise HTTPException(status_code=404, detail="No se encontraron canciones en el álbum")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        else:
             raise HTTPException(status_code=400, detail="URL de Spotify no soportada.")
    
    else:
        # Assume it's YouTube/SoundCloud/Other supported by yt-dlp
        try:
            import os
            ffmpeg_dir = os.path.dirname(file_utils.ffmpeg_path) if file_utils.ffmpeg_path else None
            ydl_opts = {
                'quiet': True,
                'ffmpeg_location': ffmpeg_dir,
                'extract_flat': 'in_playlist' # Extract playlist entries without downloading
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if 'entries' in info:
                    # It's a playlist
                    tracks = []
                    for entry in info['entries']:
                        if not entry: continue
                        tracks.append({
                            "title": entry.get('title'),
                            "artist": entry.get('uploader') or entry.get('artist') or entry.get('channel') or "Unknown",
                            "album": entry.get('album') or info.get('title') or "Unknown Album",
                            "duration_seconds": entry.get('duration'),
                            "cover_url": entry.get('thumbnail'),
                            "url": entry.get('url') or entry.get('webpage_url'),
                            "original_url": entry.get('url') or entry.get('webpage_url')
                        })
                    
                    playlist_data = {
                        "title": info.get('title'),
                        "cover_url": info.get('thumbnail'),
                        "url": url,
                        "tracks": tracks
                    }
                    return {"type": "playlist", "data": playlist_data, "count": len(tracks)}
                
                else:
                    # It's a single track
                    track_info = {
                        "title": info.get('title'),
                        "artist": info.get('uploader') or info.get('artist') or info.get('channel') or "Unknown",
                        "album": info.get('album') or "Single",
                        "duration_seconds": info.get('duration'),
                        "cover_url": info.get('thumbnail'),
                        "url": url,
                        "original_url": url
                    }
                    return {"type": "track", "data": track_info}
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error al procesar URL: {str(e)}")


@app.post("/api/parse_tracklist")
def parse_tracklist_endpoint(request: TracklistRequest):
    """Parses a text tracklist and returns structured data"""
    try:
        tracks = parse_tracklist(request.text)
        return {"tracks": tracks, "count": len(tracks)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/download")
async def download_song(data: DownloadRequest, background_tasks: BackgroundTasks):
    """
    Inicia la descarga de una canción, playlist o álbum.
    Retorna un task_id para trackear el progreso.
    """
    url = data.spotify_url
    quality = data.quality
    
    # Generar ID de tarea único
    task_id = str(uuid.uuid4())
    
    # --- Helper for batch download ---
    def batch_download_wrapper(tracks, quality, task_id):
        total = len(tracks)
        success_count = 0
        
        for i, track in enumerate(tracks):
            try:
                # Update progress for current track
                download_progress[task_id]["current_track"] = i + 1
                download_progress[task_id]["status"] = "downloading"
                download_progress[task_id]["filename"] = f"{track.get('artist', 'Unknown')} - {track.get('title', 'Unknown')}"
                download_progress[task_id]["percent"] = 0 # Reset for new track
                
                # Determine if we need to search on YouTube or if we have a direct URL
                direct_url = track.get('url') or track.get('original_url')
                is_spotify_track = "spotify.com" in (direct_url or "")
                
                video_info_to_download = None
                
                # If it's a manual tracklist item (no URL) or Spotify, we search
                if not direct_url or is_spotify_track or ("youtube" not in direct_url and "soundcloud" not in direct_url):
                     # Search on YouTube logic
                     query = f"{track['artist']} {track['title']}"
                     # Adapt track dict keys if needed
                     # Ensure cover_url is present for the downloader
                     track['cover_url'] = track.get('cover_art') or track.get('cover_url')
                     
                     youtube_results = search_on_youtube(query, track)
                     if youtube_results:
                         best_match = youtube_results[0]
                         video_info_to_download = best_match
                         # Get cover art from YouTube thumbnail
                         if not track.get('cover_url') and best_match.get('thumbnail'):
                             track['cover_url'] = best_match.get('thumbnail')
                     else:
                         continue
                else:
                    # Generic playlist track (SoundCloud/YouTube) - Direct Download
                    # We construct a video_info dict from the track info
                    video_info_to_download = {
                        'url': direct_url,
                        'title': track.get('title'),
                        'uploader': track.get('artist'),
                        'webpage_url': direct_url
                    }

                if video_info_to_download:
                    # Define a per-track progress hook
                    def track_hook(d):
                        if d['status'] == 'downloading':
                            try:
                                p = 0
                                if d.get('total_bytes'):
                                    p = d['downloaded_bytes'] / d['total_bytes'] * 100
                                elif d.get('total_bytes_estimate'):
                                    p = d['downloaded_bytes'] / d['total_bytes_estimate'] * 100
                                else:
                                    import re
                                    p_str = d.get('_percent_str', '0%').replace('%','')
                                    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
                                    p_str = ansi_escape.sub('', p_str)
                                    p = float(p_str)
                                
                                # Update global progress (we could average it, but for now just show current track percent)
                                download_progress[task_id]["percent"] = p
                            except Exception:
                                pass
                        elif d['status'] == 'finished':
                            download_progress[task_id]["percent"] = 100

                    # Download
                    # Ensure spotify_info (track) has cover_url
                    if download_track(video_info_to_download, track, quality, track_hook, overwrite=True):
                        success_count += 1
            except Exception as e:
                print(f"Error downloading {track.get('title')}: {e}")
                download_progress[task_id]["error"] = str(e)
                # Continue to next track
        
        # Finish task
        download_progress[task_id]["status"] = "completed"
        download_progress[task_id]["percent"] = 100
        download_progress[task_id]["message"] = f"Descarga completada. {success_count}/{total} canciones descargadas."

    # --- Main Download Logic ---
    
    # Check if it's a manual tracklist download
    if data.tracklist_mode and data.tracks:
        # Initialize progress
        download_progress[task_id] = {
            "status": "starting",
            "percent": 0,
            "filename": "Tracklist Download",
            "total_tracks": len(data.tracks),
            "current_track": 0
        }
        
        background_tasks.add_task(batch_download_wrapper, data.tracks, quality, task_id)
        
        return {
            "status": "started",
            "task_id": task_id,
            "message": f"Iniciando descarga de {len(data.tracks)} canciones..."
        }

    if "spotify.com" in url:
        if "track" in url:
            # --- Single Track Logic (Spotify) ---
            try:
                with SpotifyExtractor() as extractor:
                    spotify_info = extractor.extract_track_info(url)
                
                if not spotify_info:
                    raise HTTPException(status_code=404, detail="No se pudo obtener info de Spotify")
                
                # Buscar en YouTube
                query = f"{spotify_info['artist']} {spotify_info['title']}"
                youtube_results = search_on_youtube(query, spotify_info)
                
                if not youtube_results:
                    raise HTTPException(status_code=404, detail="No se encontraron resultados en YouTube")
                
                best_match = youtube_results[0]
                video_info = best_match
                
                # Inicializar progreso
                download_progress[task_id] = {
                    "status": "starting",
                    "percent": 0,
                    "filename": f"{spotify_info['artist']} - {spotify_info['title']}"
                }
                
                # Define hook
                def progress_hook(d):
                    if d['status'] == 'downloading':
                        try:
                            p = 0
                            if d.get('total_bytes'):
                                p = d['downloaded_bytes'] / d['total_bytes'] * 100
                            elif d.get('total_bytes_estimate'):
                                p = d['downloaded_bytes'] / d['total_bytes_estimate'] * 100
                            else:
                                import re
                                p_str = d.get('_percent_str', '0%').replace('%','')
                                ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
                                p_str = ansi_escape.sub('', p_str)
                                p = float(p_str)
                            
                            download_progress[task_id]["percent"] = p
                            download_progress[task_id]["status"] = "downloading"
                        except Exception:
                            pass
                    elif d['status'] == 'finished':
                        download_progress[task_id]["percent"] = 100
                        download_progress[task_id]["status"] = "processing"
                
                # Wrapper
                def download_wrapper(video_info, spotify_info, quality, hook):
                    try:
                        success = download_track(video_info, spotify_info, quality, hook, overwrite=True)
                        if success:
                            download_progress[task_id]["status"] = "completed"
                            download_progress[task_id]["percent"] = 100
                        else:
                            download_progress[task_id]["status"] = "error"
                    except Exception as e:
                        download_progress[task_id]["status"] = "error"
                        download_progress[task_id]["error"] = str(e)

                background_tasks.add_task(download_wrapper, video_info, spotify_info, quality, progress_hook)
                
                return {
                    "status": "started", 
                    "task_id": task_id,
                    "message": f"Descargando {spotify_info['title']}..."
                }
            except Exception as e:
                 raise HTTPException(status_code=500, detail=str(e))

        elif "playlist" in url or "album" in url:
            # --- Playlist/Album Logic (Spotify) ---
            try:
                with SpotifyExtractor() as extractor:
                    if "playlist" in url:
                        collection_data = extractor.extract_playlist_tracks(url)
                        collection_type = "Playlist"
                    else:
                        collection_data = extractor.extract_album_tracks(url)
                        collection_type = "Álbum"
                
                tracks = collection_data.get('tracks', [])
                if not tracks:
                    raise HTTPException(status_code=404, detail=f"No se encontraron canciones en {collection_type}")
                
                # Inicializar progreso
                download_progress[task_id] = {
                    "status": "starting",
                    "percent": 0,
                    "filename": f"{collection_type}: {collection_data.get('title', 'Unknown')}",
                    "total_tracks": len(tracks),
                    "current_track": 0
                }

                background_tasks.add_task(batch_download_wrapper, tracks, quality, task_id)
                
                return {
                    "status": "started", 
                    "task_id": task_id,
                    "message": f"Iniciando descarga de {len(tracks)} canciones..."
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

    else:
        # Assume it's YouTube/SoundCloud/Other supported by yt-dlp
        try:
            import os
            ffmpeg_dir = os.path.dirname(file_utils.ffmpeg_path) if file_utils.ffmpeg_path else None
            ydl_opts = {
                'quiet': True,
                'ffmpeg_location': ffmpeg_dir,
                'extract_flat': 'in_playlist'
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
            
            if 'entries' in info:
                # --- Generic Playlist ---
                tracks = []
                for entry in info['entries']:
                    if not entry: continue
                    tracks.append({
                        "title": entry.get('title'),
                        "artist": entry.get('uploader') or entry.get('artist') or "Unknown",
                        "album": entry.get('album') or info.get('title') or "Unknown Album",
                        "percent": 0,
                        "filename": f"{entry.get('uploader', 'Unknown')} - {entry.get('title', 'Unknown')}"
                    })
                
                # Definir hook de progreso
                def progress_hook(d):
                    if d['status'] == 'downloading':
                        try:
                            p = 0
                            if d.get('total_bytes'):
                                p = d['downloaded_bytes'] / d['total_bytes'] * 100
                            elif d.get('total_bytes_estimate'):
                                p = d['downloaded_bytes'] / d['total_bytes_estimate'] * 100
                            else:
                                import re
                                p_str = d.get('_percent_str', '0%').replace('%','')
                                ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
                                p_str = ansi_escape.sub('', p_str)
                                p = float(p_str)
                            
                            download_progress[task_id]["percent"] = p
                            download_progress[task_id]["status"] = "downloading"
                        except Exception as e:
                            print(f"Error in progress hook: {e}")
                    elif d['status'] == 'finished':
                        download_progress[task_id]["percent"] = 100
                        download_progress[task_id]["status"] = "processing"
                
                # Wrapper
                def download_wrapper(video_info, spotify_info, quality, hook):
                    try:
                        success = download_track(video_info, spotify_info, quality, hook, overwrite=True)
                        if success:
                            download_progress[task_id]["status"] = "completed"
                            download_progress[task_id]["percent"] = 100
                        else:
                            download_progress[task_id]["status"] = "error"
                    except Exception as e:
                        download_progress[task_id]["status"] = "error"
                        download_progress[task_id]["error"] = str(e)

                # Ejecutar descarga en background
                background_tasks.add_task(batch_download_wrapper, tracks, quality, task_id)
                
                response = {
                    "status": "started", 
                    "task_id": task_id,
                    "message": f"Descargando playlist de {len(tracks)} canciones..."
                }
                print(f"DEBUG: Returning response: {response}")
                return response

            else:
                # --- Generic Single Video ---
                video_info = info
                spotify_info = {
                    "title": info.get('title'),
                    "artist": info.get('uploader') or info.get('artist') or "Unknown",
                    "album": info.get('album') or "Single",
                    "cover_url": info.get('thumbnail'),
                    "url": url
                }

                # Inicializar progreso
                download_progress[task_id] = {
                    "status": "starting",
                    "percent": 0,
                    "filename": f"{spotify_info['artist']} - {spotify_info['title']}"
                }

                # Define hook
                def progress_hook(d):
                    if d['status'] == 'downloading':
                        try:
                            p = 0
                            if d.get('total_bytes'):
                                p = d['downloaded_bytes'] / d['total_bytes'] * 100
                            elif d.get('total_bytes_estimate'):
                                p = d['downloaded_bytes'] / d['total_bytes_estimate'] * 100
                            else:
                                import re
                                p_str = d.get('_percent_str', '0%').replace('%','')
                                ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
                                p_str = ansi_escape.sub('', p_str)
                                p = float(p_str)
                            
                            download_progress[task_id]["percent"] = p
                            download_progress[task_id]["status"] = "downloading"
                        except Exception:
                            pass
                    elif d['status'] == 'finished':
                        download_progress[task_id]["percent"] = 100
                        download_progress[task_id]["status"] = "processing"

                # Wrapper
                def download_wrapper(video_info, spotify_info, quality, hook):
                    try:
                        success = download_track(video_info, spotify_info, quality, hook, overwrite=True)
                        if success:
                            download_progress[task_id]["status"] = "completed"
                            download_progress[task_id]["percent"] = 100
                        else:
                            download_progress[task_id]["status"] = "error"
                    except Exception as e:
                        download_progress[task_id]["status"] = "error"
                        download_progress[task_id]["error"] = str(e)

                background_tasks.add_task(download_wrapper, video_info, spotify_info, quality, progress_hook)
                
                response = {
                    "status": "started", 
                    "task_id": task_id,
                    "message": f"Descargando {spotify_info['title']}..."
                }
                print(f"DEBUG: Returning response: {response}")
                return response
            
        except Exception as e:
            print(f"DEBUG: Exception in download_song: {e}")
            import traceback
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/progress/{task_id}")
def get_progress(task_id: str):
    return download_progress.get(task_id, {"status": "not_found"})

@app.post("/api/settings")
def save_settings(settings: Settings):
    """Guarda las credenciales en el archivo .env"""
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    
    with open(env_path, "w") as f:
        f.write(f"SPOTIPY_CLIENT_ID={settings.client_id}\n")
        f.write(f"SPOTIPY_CLIENT_SECRET={settings.client_secret}\n")
    
    # Actualizar variables de entorno en memoria para efecto inmediato (parcial)
    os.environ["SPOTIPY_CLIENT_ID"] = settings.client_id
    os.environ["SPOTIPY_CLIENT_SECRET"] = settings.client_secret
    
    return {"status": "saved"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
