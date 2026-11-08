@echo off
title Conectar Google Flow a ViralForge
color 0A
echo ================================================================
echo    CONECTANDO GOOGLE FLOW A VIRALFORGE STUDIO (ACADEMIA ZENIT)
echo ================================================================
echo.
echo Se abrira una ventana de Google Chrome.
echo 1. Inicia sesion con tu cuenta de Google.
echo 2. Entra a Google Flow / ImageFX.
echo 3. Cuando estes dentro, simplemente cierra la ventana de Chrome.
echo.
cd /d "C:\Users\cabel\Music\avatars-realistas"
"C:\Users\cabel\AppData\Local\Programs\Python\Python312\python.exe" -m viralforge.google_flow_bridge --setup
echo.
echo ================================================================
echo  Sesion configurada con exito. Presiona cualquier tecla para salir.
echo ================================================================
pause
