# 🎵 Alejandria of Music

Una biblioteca musical universal que te permite descargar música de múltiples plataformas con una interfaz web moderna y elegante.

## ✨ Características

- 🎵 **Descarga desde Spotify** - Canciones individuales y playlists completas
- 🎬 **Descarga desde YouTube** - Extrae audio de alta calidad de videos
- 🎧 **Descarga desde SoundCloud** - Accede a música independiente
- 🎨 **Carátulas embebidas automáticamente** en formato JPEG
- 🖥️ **Interfaz web moderna** construida con Next.js
- ⚡ **API REST rápida** con FastAPI
- 🔒 **Configuración segura** con variables de entorno
- 🎧 **Alta calidad de audio** (hasta 320kbps)
- 🎯 **Selector de calidad** - Elige entre 128K, 192K o 320K
- 📋 **Descarga por lotes** - Múltiples canciones simultáneamente

## 🚀 Inicio Rápido

### Prerrequisitos

- Python 3.8+
- Node.js 18+
- Credenciales de Spotify API (para descargas de Spotify)

### Instalación Rápida

1. **Clona el repositorio:**
   ```bash
   git clone https://github.com/tuusuario/alejandria-of-music.git
   cd alejandria-of-music
   ```

2. **Configura las credenciales de Spotify:**
   
   Crea un archivo `.env` en la raíz del proyecto:
   ```env
   SPOTIPY_CLIENT_ID=tu_client_id_aqui
   SPOTIPY_CLIENT_SECRET=tu_client_secret_aqui
   ```
   
   > 💡 **Obtén tus credenciales:** Ve al [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/), crea una app y copia tus credenciales.

3. **Ejecuta el script de inicio:**
   ```bash
   start.bat
   ```
   
   ¡Eso es todo! La aplicación se abrirá automáticamente en tu navegador.

## 💻 Uso Manual

### Backend (API)

```bash
cd api
pip install -r requirements.txt
python main.py
```

La API estará disponible en `http://localhost:8001`

### Frontend (Interfaz Web)

```bash
cd web
npm install
npm run dev
```

La interfaz web estará disponible en `http://localhost:3000`

## 🎯 Cómo Usar

1. **Abre la aplicación** en tu navegador
2. **Pega el enlace** de Spotify, YouTube o SoundCloud
3. **Selecciona la calidad** de audio deseada (128K, 192K, 320K)
4. **Haz clic en descargar** y espera a que se procese
5. **Descarga tu música** en formato MP3 con metadata completa

> **Tip:** Haz clic en el icono de ayuda (?) en la esquina superior derecha para ver detalles sobre las plataformas soportadas.

## ⚙️ Configuración Avanzada

El archivo `config.json` permite personalizar el comportamiento:

```json
{
    "DEFAULT": {
        "debug": false,
        "clean_console": true,
        "show_message": true
    },
    "DOWNLOAD": {
        "allow_metadata": true,
        "auto_first": false,
        "quality": "320K",
        "thread": 5
    },
    "SEARCH": {
        "limit": 5,
        "exclude_emoji": false
    }
}
```

### Opciones de Configuración

#### DEFAULT
- **`debug`**: Activar modo debug para ver logs detallados
- **`clean_console`**: Limpiar consola para interfaz más limpia
- **`show_message`**: Mostrar mensajes informativos durante descargas

#### DOWNLOAD
- **`allow_metadata`**: Descargar carátulas y embeber metadata (artista, álbum, etc.)
- **`auto_first`**: Seleccionar automáticamente el primer resultado de búsqueda
- **`quality`**: Calidad de audio por defecto (128K, 192K, 320K)
- **`thread`**: Número de descargas concurrentes (máximo 10)

#### SEARCH
- **`limit`**: Número máximo de resultados de búsqueda
- **`exclude_emoji`**: Excluir emojis de los resultados

## 📁 Estructura del Proyecto

```
alejandria-of-music/
├── api/                    # Backend FastAPI (Puerto 8001)
├── web/                    # Frontend Next.js (Puerto 3000)
├── config.json             # Configuración
├── .env                    # Variables de entorno
├── start.bat               # Script de inicio
└── README.md               # Documentación
```

## 🛠️ Tecnologías Utilizadas

### Backend
- **FastAPI** - Framework web moderno y rápido
- **Spotipy** - Cliente de Spotify API
- **yt-dlp** - Descargador universal de audio/video
- **mutagen** - Manipulación de metadata de audio

### Frontend
- **Next.js 14** - Framework React con App Router
- **TypeScript** - JavaScript con tipado estático
- **Tailwind CSS** - Framework de estilos utilitarios
- **React Hooks** - Gestión de estado moderna
- **Lucide React** - Iconos modernos

## 🎨 Plataformas Soportadas

| Plataforma | Soporte | Características |
|------------|---------|-----------------|
| 🎵 Spotify | ✅ Completo | Canciones, álbumes, playlists (con portadas) |
| 🎬 YouTube | ✅ Completo | Videos individuales, extracción de audio |
| 🎧 SoundCloud | ✅ Completo | Tracks individuales |

## 🔧 Solución de Problemas

### Error de conexión con Spotify
- Verifica que tus credenciales en `.env` sean correctas
- Asegúrate de que tu app de Spotify esté activa en el Dashboard

### Error al descargar
- Verifica tu conexión a internet
- Asegúrate de que el enlace sea válido y público
- Intenta con una calidad de audio menor

### La interfaz no carga
- Verifica que el backend esté corriendo en el puerto 8001
- Verifica que el frontend esté corriendo en el puerto 3000
- Revisa la consola del navegador para errores

## 📝 API Endpoints

- `GET /` - Información de la API
- `POST /api/info` - Obtener información de URL (Spotify/YouTube/SoundCloud)
- `POST /api/download` - Iniciar descarga
- `GET /api/progress/{task_id}` - Consultar progreso de descarga
- `GET /api/download/{filename}` - Obtener archivo descargado

## ⚠️ Disclaimer

Este software se proporciona "tal cual", sin garantía de ningún tipo.

**Importante**: Esta herramienta está destinada únicamente para fines educativos y uso personal. Los usuarios son responsables de asegurarse de cumplir con las leyes aplicables y los términos de servicio de las plataformas. Los desarrolladores no fomentan ni condonan la piratería o la infracción de derechos de autor.

## 📄 Licencia

Este proyecto está bajo la licencia GPL-3.0. Ver el archivo [LICENSE](LICENSE) para más detalles.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:
1. Haz fork del proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

<div align="center">

**made with <3 by tico**

*Alejandria of Music - Tu biblioteca musical universal*

</div>
