"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { UrlInput } from "./components/UrlInput";
import { Download, Music, Disc, CheckCircle2, AlertCircle, Settings as SettingsIcon, Loader2 } from "lucide-react";
import Link from "next/link";

interface SpotifyInfo {
  type: "track" | "playlist";
  data: any;
  count?: number;
}

export default function Home() {
  const [isLoading, setIsLoading] = useState(false);
  const [info, setInfo] = useState<SpotifyInfo | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [downloadStatus, setDownloadStatus] = useState<string | null>(null);
  const [taskId, setTaskId] = useState<string | null>(null);
  const [progress, setProgress] = useState<number>(0);

  const handleSearch = async (url: string) => {
    setIsLoading(true);
    setError(null);
    setInfo(null);
    setDownloadStatus(null);
    setTaskId(null);
    setProgress(0);

    try {
      const response = await fetch("http://localhost:8000/api/info", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      });

      if (!response.ok) {
        throw new Error("No se pudo obtener información. Verifica el enlace.");
      }

      const data = await response.json();
      setInfo(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDownload = async () => {
    if (!info) return;

    setDownloadStatus("Iniciando descarga...");
    setProgress(0);
    setTaskId(null);

    // Llamada real al backend
    try {
      console.log("Info object:", info);
      const urlToDownload = info.data.url || info.data.original_url || info.data.external_urls?.spotify;
      if (!urlToDownload) {
        console.error("URL missing in info.data:", info.data);
        throw new Error("URL no encontrada en la respuesta");
      }

      // Leer la calidad guardada desde localStorage, por defecto 320K
      const quality = localStorage.getItem("audio_quality") || "320K";

      const response = await fetch("http://localhost:8000/api/download", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          spotify_url: urlToDownload,
          quality: quality
        }),
      });

      if (response.ok) {
        const data = await response.json();
        console.log("Download response data:", data);
        setDownloadStatus("Descarga iniciada...");
        if (data.task_id) {
          console.log("Setting taskId:", data.task_id);
          setTaskId(data.task_id);
        } else {
          console.error("No task_id in response");
        }
      } else {
        console.error("Response not ok");
        setDownloadStatus("Error al iniciar descarga.");
      }
    } catch (e: any) {
      console.error("Download error:", e);
      setDownloadStatus(`Error: ${e.message || "Error de conexión"}`);
    }
  };

  // Polling for progress
  useEffect(() => {
    if (!taskId) return;

    const interval = setInterval(async () => {
      try {
        const res = await fetch(`http://localhost:8000/api/progress/${taskId}`);
        if (res.ok) {
          const data = await res.json();
          console.log("Progress data:", data);

          if (data.status === 'downloading') {
            setDownloadStatus(`Descargando: ${data.percent.toFixed(1)}%`);
            setProgress(data.percent);
          } else if (data.status === 'processing') {
            setDownloadStatus("Procesando audio...");
            setProgress(100);
          } else if (data.status === 'completed') {
            setDownloadStatus("¡Descarga completada!");
            setProgress(100);
            clearInterval(interval);
            setTaskId(null); // Stop polling
          } else if (data.status === 'error') {
            setDownloadStatus(`Error: ${data.error || "Falló la descarga"}`);
            clearInterval(interval);
            setTaskId(null);
          } else if (data.status === 'starting') {
            setDownloadStatus("Iniciando...");
          }
        }
      } catch (e) {
        console.error("Polling error", e);
      }
    }, 500);

    return () => clearInterval(interval);
  }, [taskId]);

  return (
    <main className="min-h-screen bg-black text-white selection:bg-green-500 selection:text-black overflow-hidden">
      <div className="absolute inset-0 bg-[url('/grid.svg')] bg-center mask-[linear-gradient(180deg,white,rgba(255,255,255,0))]"></div>

      <div className="relative container mx-auto px-4 py-20 flex flex-col items-center justify-center min-h-screen">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center mb-12"
        >
          <h1 className="text-6xl md:text-8xl font-bold tracking-tighter mb-6 bg-clip-text text-transparent bg-linear-to-b from-white to-gray-400">
            Alejandria of Music
          </h1>
          <p className="text-xl text-gray-400 max-w-2xl mx-auto">
            Descarga tu música favorita de Spotify, YouTube y SoundCloud en alta calidad.
            <br />
            <span className="text-green-500 font-semibold">Gratis, rápido y simple.</span>
          </p>
        </motion.div>

        <Link
          href="/settings"
          className="absolute top-8 right-8 p-3 text-gray-400 hover:text-white bg-gray-900/50 rounded-full hover:bg-gray-800 transition-all"
        >
          <SettingsIcon className="w-6 h-6" />
        </Link>

        <div className="w-full mb-12">
          <UrlInput onSubmit={handleSearch} isLoading={isLoading} />
        </div>

        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              className="bg-red-500/10 border border-red-500/20 text-red-500 px-6 py-4 rounded-lg flex items-center gap-3 mb-8"
            >
              <AlertCircle className="w-6 h-6" />
              <p>{error}</p>
            </motion.div>
          )}

          {info && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              className="w-full max-w-md bg-gray-900/50 backdrop-blur-xl border border-gray-800 rounded-2xl p-6 shadow-2xl"
            >
              <div className="flex items-start gap-4 mb-6">
                {info.data.cover_url ? (
                  <img
                    src={info.data.cover_url}
                    alt="Cover"
                    className="w-24 h-24 rounded-lg shadow-lg object-cover"
                  />
                ) : (
                  <div className="w-24 h-24 bg-gray-800 rounded-lg flex items-center justify-center">
                    <Disc className="w-10 h-10 text-gray-600" />
                  </div>
                )}
                <div className="flex-1 min-w-0">
                  <h3 className="text-xl font-bold truncate text-white">
                    {info.data.title || info.data.name}
                  </h3>
                  <p className="text-gray-400 truncate">
                    {info.data.artist || info.data.owner?.display_name}
                  </p>
                  <div className="mt-2 flex items-center gap-2 text-xs text-gray-500 uppercase tracking-wider font-semibold">
                    {info.type === "track" ? (
                      <span className="flex items-center gap-1">
                        <Music className="w-3 h-3" /> Canción
                      </span>
                    ) : (
                      <span className="flex items-center gap-1">
                        <Disc className="w-3 h-3" /> Playlist ({info.count})
                      </span>
                    )}
                  </div>
                </div>
              </div>

              {/* Progress Bar */}
              {taskId && (
                <div className="w-full bg-gray-700 rounded-full h-2.5 mb-4 overflow-hidden">
                  <motion.div
                    className="bg-green-500 h-2.5 rounded-full"
                    initial={{ width: 0 }}
                    animate={{ width: `${progress}%` }}
                    transition={{ duration: 0.5 }}
                  />
                </div>
              )}

              <button
                onClick={handleDownload}
                disabled={!!taskId || downloadStatus === "¡Descarga completada!"}
                className="w-full bg-white text-black font-bold py-4 rounded-xl hover:bg-gray-200 transition-colors flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {taskId ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    {downloadStatus}
                  </>
                ) : downloadStatus === "¡Descarga completada!" ? (
                  <>
                    <CheckCircle2 className="w-5 h-5 text-green-600" />
                    {downloadStatus}
                  </>
                ) : downloadStatus && downloadStatus.startsWith("Error") ? (
                  <>
                    <AlertCircle className="w-5 h-5 text-red-600" />
                    {downloadStatus}
                  </>
                ) : (
                  <>
                    <Download className="w-5 h-5" />
                    Descargar Ahora
                  </>
                )}
              </button>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </main>
  );
}
