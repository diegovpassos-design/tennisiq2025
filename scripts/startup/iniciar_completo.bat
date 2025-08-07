@echo off
cd /d "%~dp0..\.."
echo.
echo ========================================
echo   TennisIQ Bot + Dashboard Web
echo ========================================
echo.
echo 🤖 Iniciando sistema completo...
echo.

REM Criar diretórios se não existirem
if not exist "storage\logs" mkdir "storage\logs"
if not exist "storage\database" mkdir "storage\database"
if not exist "logs" mkdir logs

REM Iniciar dashboard web em background
echo 🌐 Iniciando Dashboard Web...
start "TennisIQ Dashboard" /MIN python dashboard.py

REM Aguardar 3 segundos para dashboard inicializar
timeout /t 3 /nobreak >nul

REM Abrir dashboard no navegador
echo 📊 Abrindo dashboard no navegador...
start http://localhost:5000

REM Aguardar mais 2 segundos
timeout /t 2 /nobreak >nul

REM Iniciar bot principal
echo 🎾 Iniciando TennisIQ Bot...
echo.
echo ========================================
echo   STATUS DO SISTEMA:
echo   🌐 Dashboard: http://localhost:5000
echo   🤖 Bot: Executando...
echo   📊 Dados: Sincronizados em tempo real
echo ========================================
echo.

python main.py

echo.
echo ⚠️ Bot finalizado. Pressione qualquer tecla para sair...
pause >nul
