import sys
import os
import uuid
from typing import Optional, List, Dict
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware

# Añadir el directorio actual al path para poder importar SpotDown
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from SpotDown.extractor.spotify_extractor import SpotifyExtractor
from SpotDown.main import search_on_youtube, download_track
from SpotDown.utils.console_utils import ConsoleUtils
from SpotDown.utils.os import file_utils
from dotenv import load_dotenv

# Initialize system paths (ffmpeg, etc)
file_utils.get_system_summary()

load_dotenv()

app = FastAPI(title="SpotDown API")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todos los orígenes para evitar problemas de conexión
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global dictionary to store download progress
download_progress: Dict[str, Dict] = {}

class SpotifyUrl(BaseModel):
    url: str

class DownloadRequest(BaseModel):
    spotify_url: str
    quality: Optional[str] = "320K"  # Por defecto: calidad máxima

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
                    tracks = extractor.extract_playlist_tracks(url)
                    if tracks:
                        return {"type": "playlist", "data": tracks, "count": len(tracks)}
                    else:
                        raise HTTPException(status_code=404, detail="No se encontraron canciones en la playlist")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        else:
             raise HTTPException(status_code=400, detail="URL de Spotify no soportada.")
    
    else:
        # Assume it's YouTube/SoundCloud/Other supported by yt-dlp
        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # Normalize data to match our frontend expectation
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


@app.post("/api/download")
async def download_song(data: DownloadRequest, background_tasks: BackgroundTasks):
    """
    Inicia la descarga de una canción.
    Retorna un task_id para trackear el progreso.
    """
    url = data.spotify_url # Keep field name for compatibility
    quality = data.quality
    
    # Generar ID de tarea único
    task_id = str(uuid.uuid4())
    
    try:
        if "spotify.com" in url:
            # --- Spotify Logic ---
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
            
        else:
            # --- Direct Download Logic (YouTube/SoundCloud) ---
            # Re-extract info to ensure we have valid data for the downloader
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
            
            spotify_info = {
                "title": info.get('title'),
                "artist": info.get('uploader') or info.get('artist') or "Unknown",
                "album": info.get('album') or "Single",
                "cover_url": info.get('thumbnail')
            }
            
            video_info = {
                'url': url,
                'title': info.get('title'),
                'id': info.get('id')
            }

        # Inicializar progreso
        download_progress[task_id] = {
            "status": "starting",
            "percent": 0,
            "filename": f"{spotify_info['artist']} - {spotify_info['title']}"
        }
        
        # Definir hook de progreso
        def progress_hook(d):
            print(f"DEBUG: progress_hook called. Status: {d.get('status')}")
            if d['status'] == 'downloading':
                try:
                    p = 0
                    if d.get('total_bytes'):
                        p = d['downloaded_bytes'] / d['total_bytes'] * 100
                    elif d.get('total_bytes_estimate'):
                        p = d['downloaded_bytes'] / d['total_bytes_estimate'] * 100
                    else:
                        # Fallback to string parsing
                        import re
                        p_str = d.get('_percent_str', '0%').replace('%','')
                        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
                        p_str = ansi_escape.sub('', p_str)
                        p = float(p_str)
                    
                    print(f"DEBUG: Calculated progress: {p}%")
                    download_progress[task_id]["percent"] = p
                    download_progress[task_id]["status"] = "downloading"
                except Exception as e:
                    print(f"Error in progress hook: {e}")
            elif d['status'] == 'finished':
                print("DEBUG: Download finished in hook")
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
        background_tasks.add_task(download_wrapper, video_info, spotify_info, quality, progress_hook)
        
        return {
            "status": "started", 
            "task_id": task_id,
            "message": f"Descargando {spotify_info['title']}..."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/progress/{task_id}")
def get_progress(task_id: str):
    """Devuelve el progreso de una descarga"""
    if task_id in download_progress:
        return download_progress[task_id]
    else:
        raise HTTPException(status_code=404, detail="Task not found")

class Settings(BaseModel):
    client_id: str
    client_secret: str

@app.get("/api/settings")
def get_settings():
    """Devuelve la configuración actual (ocultando parcialmente el secreto)"""
    return {
        "client_id": os.getenv("SPOTIPY_CLIENT_ID", ""),
        "client_secret": os.getenv("SPOTIPY_CLIENT_SECRET", "")
    }

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
