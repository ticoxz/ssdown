# 🎵 SSDown - Spotify Downloader

Un descargador de música de Spotify potente y fácil de usar, con interfaz web moderna y backend en Python.

## ✨ Características

- 🎵 **Descarga canciones individuales** desde Spotify
- 📋 **Descarga playlists completas** con facilidad
- 🎨 **Carátulas embebidas automáticamente** (formato JPEG)  
- 🖥️ **Interfaz web moderna** con Next.js
- ⚡ **API REST rápida** con FastAPI
- 🔒 **Configuración segura** con variables de entorno
- 🎧 **Alta calidad de audio** (hasta 320kbps)

## 🚀 Instalación

### Prerrequisitos

- Python 3.8+
- Node.js 18+ (para la interfaz web)
- Credenciales de Spotify API

### Configuración

1. **Obtén tus credenciales de Spotify:**
   - Ve al [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/)
   - Inicia sesión y crea una nueva aplicación
   - Copia tu **Client ID** y **Client Secret**

2. **Configura las variables de entorno:**
   
   Crea un archivo `.env` en la raíz del proyecto:
   ```env
   SPOTIPY_CLIENT_ID=tu_client_id_aqui
   SPOTIPY_CLIENT_SECRET=tu_client_secret_aqui
   ```

3. **Instala las dependencias del backend:**
   ```bash
   cd api
   pip install -r requirements.txt
   ```

4. **Instala las dependencias del frontend:**
   ```bash
   cd web
   npm install
   ```

## 💻 Uso

### Ejecutar el backend (API)

```bash
cd api
python main.py
```

La API estará disponible en `http://localhost:8000`

### Ejecutar el frontend (Interfaz Web)

```bash
cd web
npm run dev
```

La interfaz web estará disponible en `http://localhost:3000`

### Uso desde línea de comandos

También puedes usar el script directamente:

```bash
python run.py
```

## ⚙️ Configuración

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
- **`debug`**: Activar/desactivar modo debug
- **`clean_console`**: Limpiar consola para interfaz más limpia
- **`show_message`**: Mostrar mensajes informativos

#### DOWNLOAD
- **`allow_metadata`**: Descargar miniaturas y embeber metadata
- **`auto_first`**: Seleccionar automáticamente el primer resultado
- **`quality`**: Calidad de audio (320K recomendado)
- **`thread`**: Número de descargas concurrentes

#### SEARCH
- **`limit`**: Número máximo de resultados de búsqueda
- **`exclude_emoji`**: Excluir emojis de resultados

## 📁 Estructura del Proyecto

```
ssdown/
├── api/                 # Backend FastAPI
│   ├── SpotDown/       # Módulo principal de descarga
│   ├── main.py         # Servidor API
│   └── requirements.txt
├── web/                # Frontend Next.js
│   ├── app/           # Páginas y componentes
│   ├── public/        # Recursos estáticos
│   └── package.json
├── config.json        # Archivo de configuración
├── .env              # Variables de entorno (no incluido en git)
└── README.md         # Este archivo
```

## 🛠️ Tecnologías Utilizadas

- **Backend:** Python, FastAPI, Spotipy
- **Frontend:** Next.js, React, TypeScript
- **Descarga:** yt-dlp
- **Metadata:** mutagen

## ⚠️ Disclaimer

Este software se proporciona "tal cual", sin garantía de ningún tipo. 

**Importante**: Esta herramienta está destinada únicamente para fines educativos y uso personal. Los usuarios son responsables de asegurarse de cumplir con las leyes aplicables y los términos de servicio de las plataformas. Los desarrolladores no fomentan ni condonan la piratería o la infracción de derechos de autor.

## 📝 Licencia

Este proyecto está bajo la licencia GPL-3.0. Ver el archivo [LICENSE](LICENSE) para más detalles.

---

<div align="center">

**Hecho con ❤️ por ticoxz**

*Última actualización: Noviembre 2025*

</div>
