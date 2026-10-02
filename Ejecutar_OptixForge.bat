@echo off
chcp 65001 > nul
title OPTIX FORGE // Engine & FOV / Ultrawide Tweaker
echo ===================================================
echo   OPTIX FORGE // NVIDIA Power Green Architecture
echo   Iniciando suite de optimizacion grafica y FOV...
echo ===================================================
python main.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Error al iniciar Optix Forge.
    pause
)
