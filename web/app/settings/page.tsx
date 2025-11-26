"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Save, ArrowLeft, Key, CheckCircle2 } from "lucide-react";
import Link from "next/link";

export default function Settings() {
    const [clientId, setClientId] = useState("");
    const [clientSecret, setClientSecret] = useState("");
    const [quality, setQuality] = useState("320K");
    const [status, setStatus] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(false);

    useEffect(() => {
        // Cargar configuración actual al montar
        fetch("http://localhost:8000/api/settings")
            .then((res) => res.json())
            .then((data) => {
                if (data.client_id) setClientId(data.client_id);
                if (data.client_secret) setClientSecret(data.client_secret);
            })
            .catch(() => { });

        // Cargar calidad guardada desde localStorage
        const savedQuality = localStorage.getItem("audio_quality");
        if (savedQuality) {
            setQuality(savedQuality);
        }
    }, []);

    const handleSave = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setStatus(null);

        try {
            // Guardar calidad en localStorage
            localStorage.setItem("audio_quality", quality);

            const response = await fetch("http://localhost:8000/api/settings", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ client_id: clientId, client_secret: clientSecret }),
            });

            if (response.ok) {
                setStatus("¡Guardado correctamente! Reinicia el backend para aplicar cambios.");
            } else {
                setStatus("Error al guardar.");
            }
        } catch (error) {
            setStatus("Error de conexión.");
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <main className="min-h-screen bg-black text-white selection:bg-green-500 selection:text-black p-8">
            <div className="max-w-2xl mx-auto">
                <Link href="/" className="inline-flex items-center text-gray-400 hover:text-white mb-8 transition-colors">
                    <ArrowLeft className="w-5 h-5 mr-2" /> Volver al inicio
                </Link>

                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="bg-gray-900/50 border border-gray-800 rounded-2xl p-8"
                >
                    <div className="flex items-center gap-4 mb-8">
                        <div className="p-3 bg-green-500/10 rounded-lg">
                            <Key className="w-8 h-8 text-green-500" />
                        </div>
                        <div>
                            <h1 className="text-2xl font-bold">Configuración de API</h1>
                            <p className="text-gray-400">Ingresa tus credenciales de Spotify Developer.</p>
                        </div>
                    </div>

                    <form onSubmit={handleSave} className="space-y-6">
                        <div>
                            <label className="block text-sm font-medium text-gray-300 mb-2">
                                Client ID
                            </label>
                            <input
                                type="text"
                                value={clientId}
                                onChange={(e) => setClientId(e.target.value)}
                                className="w-full bg-black border border-gray-700 rounded-lg p-3 text-white focus:border-green-500 focus:ring-1 focus:ring-green-500 transition-colors"
                                placeholder="Pegar Client ID aquí"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-300 mb-2">
                                Client Secret
                            </label>
                            <input
                                type="password"
                                value={clientSecret}
                                onChange={(e) => setClientSecret(e.target.value)}
                                className="w-full bg-black border border-gray-700 rounded-lg p-3 text-white focus:border-green-500 focus:ring-1 focus:ring-green-500 transition-colors"
                                placeholder="Pegar Client Secret aquí"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-300 mb-2">
                                Calidad de Audio
                            </label>
                            <select
                                value={quality}
                                onChange={(e) => setQuality(e.target.value)}
                                className="w-full bg-black border border-gray-700 rounded-lg p-3 text-white focus:border-green-500 focus:ring-1 focus:ring-green-500 transition-colors cursor-pointer"
                            >
                                <option value="128K">128 kbps - Calidad Estándar</option>
                                <option value="192K">192 kbps - Calidad Alta</option>
                                <option value="256K">256 kbps - Calidad Muy Alta</option>
                                <option value="320K">320 kbps - Calidad Máxima (Recomendado)</option>
                            </select>
                            <p className="mt-2 text-xs text-gray-500">
                                Esta configuración se aplicará a todas las descargas futuras.
                            </p>
                        </div>

                        <div className="bg-gray-800/50 p-4 rounded-lg text-sm text-gray-400">
                            <p>
                                ¿No tienes credenciales? Ve al{" "}
                                <a
                                    href="https://developer.spotify.com/dashboard/"
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="text-green-500 hover:underline"
                                >
                                    Spotify Developer Dashboard
                                </a>
                                , crea una app y copia los datos.
                            </p>
                        </div>

                        <button
                            type="submit"
                            disabled={isLoading}
                            className="w-full bg-green-500 text-black font-bold py-3 rounded-lg hover:bg-green-400 transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
                        >
                            {isLoading ? (
                                "Guardando..."
                            ) : (
                                <>
                                    <Save className="w-5 h-5" /> Guardar Configuración
                                </>
                            )}
                        </button>

                        {status && (
                            <motion.div
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                className="flex items-center justify-center gap-2 text-green-400 mt-4"
                            >
                                <CheckCircle2 className="w-5 h-5" />
                                {status}
                            </motion.div>
                        )}
                    </form>
                </motion.div>
            </div>
        </main>
    );
}
