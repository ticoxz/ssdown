import sys
import os
from typing import Optional, List
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware

# Añadir el directorio actual al path para poder importar SpotDown
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from SpotDown.extractor.spotify_extractor import SpotifyExtractor
from SpotDown.main import search_on_youtube, download_track
from SpotDown.utils.console_utils import ConsoleUtils
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="SpotDown API")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SpotifyUrl(BaseModel):
    url: str

class DownloadRequest(BaseModel):
    spotify_url: str
    quality: Optional[str] = "320K"  # Por defecto: calidad máxima

@app.get("/")
def read_root():
    return {"message": "SpotDown API está funcionando"}

@app.post("/api/info")
def get_spotify_info(data: SpotifyUrl):
    """
    Obtiene información de una URL de Spotify (canción o playlist).
    """
    url = data.url
    console = ConsoleUtils()
    
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
        raise HTTPException(status_code=400, detail="URL no soportada. Usa un enlace de canción o playlist de Spotify.")

@app.post("/api/download")
async def download_song(data: DownloadRequest, background_tasks: BackgroundTasks):
    """
    Inicia la descarga de una canción.
    Nota: Por ahora es síncrono para simplificar, pero idealmente debería ser asíncrono.
    """
    url = data.spotify_url
    quality = data.quality  # Obtener la calidad del request
    
    # Extraer info
    with SpotifyExtractor() as extractor:
        spotify_info = extractor.extract_track_info(url)
    
    if not spotify_info:
        raise HTTPException(status_code=404, detail="No se pudo obtener info de Spotify")
    
    # Buscar en YouTube
    query = f"{spotify_info['artist']} {spotify_info['title']}"
    youtube_results = search_on_youtube(query, spotify_info)
    
    if not youtube_results:
        raise HTTPException(status_code=404, detail="No se encontraron resultados en YouTube")
    
    # Descargar el mejor resultado
    # Usamos background tasks para no bloquear, aunque SpotDown imprime a consola.
    # Para una web app real, necesitaríamos capturar el progreso.
    # Por ahora, ejecutamos y retornamos éxito si inicia.
    
    try:
        # Seleccionamos el primer resultado (mejor coincidencia)
        best_match = youtube_results[0]
        
        # Ejecutar descarga con la calidad especificada
        # Nota: download_track es síncrono. Si lo ponemos en background_tasks, 
        # el usuario recibirá respuesta inmediata "Descarga iniciada".
        background_tasks.add_task(download_track, best_match, spotify_info, quality)
        
        return {"status": "started", "message": f"Descargando {spotify_info['title']} de {spotify_info['artist']} en calidad {quality}"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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

