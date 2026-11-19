@echo off
rem Vector Hub: arranca wire-pod (si hace falta) y la web del proyecto en http://localhost:8090
title Vector Hub
cd /d "%~dp0"

netstat -ano | findstr ":8080 " | findstr LISTENING >nul
if errorlevel 1 (
  echo Abriendo wire-pod...
  start "" "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\WirePod.lnk"
)

netstat -ano | findstr ":8090 " | findstr LISTENING >nul
if not errorlevel 1 (
  echo La web ya estaba en marcha.
  start "" http://localhost:8090
  exit /b 0
)

rem Abre el navegador cuando el servidor ya esta escuchando
start "" /min cmd /c "timeout /t 2 >nul & start http://localhost:8090"
echo Vector Hub en http://localhost:8090  (cierra esta ventana para pararla)
python web\server.py
if errorlevel 1 pause
