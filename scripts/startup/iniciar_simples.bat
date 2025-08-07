@echo off
cd /d "%~dp0..\.."
title TennisIQ Bot Simples
echo.
echo ==========================================
echo   TENNISIQ BOT SIMPLES
echo ==========================================
echo.
echo Iniciando sistema...
echo Para parar: Ctrl+C
echo.

REM Criar diretórios se não existirem
if not exist "storage\logs" mkdir "storage\logs"
if not exist "storage\database" mkdir "storage\database"

python main.py

pause
