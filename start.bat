@echo off
echo Iniciando Alejandria of Music...

:: Iniciar Backend
start "Alejandria Backend" cmd /k "cd api && venv\Scripts\activate && uvicorn main:app --reload --port 8000"

:: Iniciar Frontend
start "Alejandria Frontend" cmd /k "cd web && npm run dev"

:: Esperar un momento antes de abrir el navegador
timeout /t 3 /nobreak >nul

:: Abrir navegador automáticamente
start http://localhost:3000

echo.
echo ========================================================
echo  Alejandria of Music se esta ejecutando!
echo  Frontend: http://localhost:3000
echo  Backend:  http://localhost:8000
echo ========================================================
echo.
pause
