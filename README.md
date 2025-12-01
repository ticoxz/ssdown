# 🎵 Alejandria of Music

Una biblioteca musical universal que te permite descargar música de múltiples plataformas con una interfaz web moderna y elegante.

## ✨ Características

- 🎵 **Descarga desde Spotify** - Canciones individuales y playlists completas
- 🎬 **Descarga desde YouTube** - Extrae audio de alta calidad de videos
- 🎧 **Descarga desde SoundCloud** - Accede a música independiente
- 🎨 **Carátulas embebidas automáticamente** en formato JPEG
- 🎯 **Selector de calidad** - Elige entre 128K, 192K, 320K o **FLAC** (sin pérdida)
- 💿 **Soporte FLAC** - Descarga audio sin pérdida de calidad
- 🎧 **DJ Priority** - Prioriza versiones Extended/Original/Club Mix para DJs
- 📂 **Organización Inteligente** - Crea subcarpetas automáticas por Playlist/Álbum
- 📍 **Ruta de Descarga Personalizada** - Elige dónde guardar tu música
- 📁 **Explorador de Archivos Integrado** - Navega y crea carpetas desde la app
- 🖥️ **Interfaz web moderna** construida con Next.js
- ⚡ **API REST rápida** con FastAPI
- 🔒 **Configuración segura** con variables de entorno
- 📋 **Descarga por lotes** - Múltiples canciones simultáneamente
- 🌐 **Modo Tracklist** - Pega una lista de canciones (Artista - Título) y descárgalas todas

## 🚀 Guía de Inicio Detallada

Sigue estos pasos uno por uno para poner en marcha el proyecto.

### 1. Prerrequisitos (Lo que necesitas instalar antes)

Asegúrate de tener instalados los siguientes programas. Si no los tienes, descárgalos e instálalos.

- **Python 3.8 o superior**: [Descargar Python](https://www.python.org/downloads/)
- **Node.js 20.9.0 o superior** (IMPORTANTE: La versión 18 no funcionará): [Descargar Node.js](https://nodejs.org/)
- **Git**: [Descargar Git](https://git-scm.com/downloads)

### 2. Configuración Inicial

1. **Clona el repositorio** (si aún no lo has hecho):
   ```bash
   git clone https://github.com/tuusuario/alejandria-of-music.git
   cd alejandria-of-music
   ```

2. **Configura las credenciales de Spotify:**
   
   Necesitas crear un archivo "secreto" para que la app pueda hablar con Spotify.
   
   - Crea un archivo llamado `.env` en la carpeta principal del proyecto.
   - Pega el siguiente contenido dentro:
     ```env
     SPOTIPY_CLIENT_ID=tu_client_id_aqui
     SPOTIPY_CLIENT_SECRET=tu_client_secret_aqui
     ```
   
   > 💡 **¿Cómo consigo estos códigos? (Guía Paso a Paso)**
   > 
   > 1. **Ve al Dashboard:** Entra a [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/) e inicia sesión con tu cuenta de Spotify.
   > 2. **Crea la App:** Haz clic en el botón **"Create app"** (arriba a la derecha).
   > 3. **Llena los datos:**
   >    - **App name:** Ponle `Alejandria` (o lo que quieras).
   >    - **App description:** Pon `Music downloader`.
   >    - **Redirect URI:** Escribe `http://localhost:8001/callback` y dale a "Add".
   >    - Marca la casilla de "I understand..." y dale a **"Save"**.
   > 4. **Obtén las claves:**
   >    - Una vez creada, ve a la sección **"Settings"** (o "Basic Information").
   >    - Verás el **Client ID** (copia y pega en tu `.env`).
   >    - Haz clic en "View client secret" para ver el **Client Secret** (copia y pega en tu `.env`).

---

## 💻 Cómo Ejecutar el Proyecto (Paso a Paso)

Necesitarás abrir **dos terminales** diferentes. Una para el cerebro (Backend) y otra para la cara (Frontend).

### Terminal 1: El Backend (API)

Esta terminal se encargará de procesar las descargas.

1. **Entra a la carpeta del API:**
   ```bash
   cd api
   ```

2. **Instala las librerías necesarias:**
   (Solo necesitas hacer esto la primera vez)
   ```bash
   # Usamos el python del entorno virtual para evitar errores de permisos
   ../.venv/bin/python -m pip install -r requirements.txt
   ```

3. **Enciende el servidor:**
   ```bash
   ../.venv/bin/python main.py
   ```
   
   ✅ **Deberías ver:** Un mensaje diciendo que el servidor está corriendo en `http://0.0.0.0:8001`.
   ⛔ **No cierres esta terminal.**

### Terminal 2: El Frontend (Web)

Esta terminal mostrará la página web en tu navegador.

1. **Abre una NUEVA terminal** (mantén la otra abierta).

2. **Entra a la carpeta web:**
   ```bash
   cd web
   ```

3. **Instala las librerías necesarias:**
   (Solo necesitas hacer esto la primera vez)
   ```bash
   npm install
   ```

4. **Enciende la página web:**
   ```bash
   npm run dev
   ```

   ✅ **Deberías ver:** Un mensaje diciendo `Ready in ...` y `http://localhost:3000`.
   ⛔ **No cierres esta terminal.**

---

## 🎯 ¡Listo!

Ahora abre tu navegador (Chrome, Safari, etc.) y entra a:
👉 **http://localhost:3000**

---

## 🔧 Solución de Problemas Comunes

### 🔴 Error: "Unsupported engine" o "Node.js version ... is required"
**Causa:** Tienes una versión vieja de Node.js (probablemente la 18).
**Solución:**
1. Ve a [nodejs.org](https://nodejs.org/)
2. Descarga la versión **LTS** (que suele ser la 20 o 22).
3. Instálala.
4. Cierra todas tus terminales y ábrelas de nuevo.
5. Verifica la versión escribiendo: `node -v` (debe decir v20.x.x o superior).

### 🔴 Error: "command not found: python" o "pip"
**Causa:** Tu computadora no sabe dónde está Python instalado globalmente.
**Solución:**
Usa siempre el comando largo que apunta al entorno virtual del proyecto:
- En lugar de `python`, usa: `../.venv/bin/python`
- En lugar de `pip`, usa: `../.venv/bin/python -m pip`

### 🔴 La descarga no inicia o da error
1. Revisa la **Terminal 1 (Backend)**. ¿Hay algún mensaje de error en rojo?
2. Verifica que tu archivo `.env` tenga las credenciales correctas.
3. Asegúrate de que ambas terminales sigan abiertas y corriendo.

### 🔴 Error: "Sign in to confirm you're not a bot" (Bloqueo de YouTube)
**Causa:** YouTube está bloqueando la descarga por seguridad.
**Solución:**
1. Instala la extensión **"Get cookies.txt LOCALLY"** en tu navegador (Chrome o Edge).
2. Ve a YouTube y asegúrate de haber iniciado sesión.
3. Usa la extensión para exportar tus cookies como un archivo `cookies.txt`.
4. Coloca ese archivo `cookies.txt` en la carpeta raíz de la aplicación (donde está `Alejandria.exe` o `main.py`).
5. Intenta descargar de nuevo. La app usará este archivo para "demostrar" que eres un humano.

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
