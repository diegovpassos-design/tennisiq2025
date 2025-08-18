# Script completo para capturar logs do Railway
# Executar: .\scripts\setup_railway_logs.ps1

Write-Host "CONFIGURACAO E CAPTURA DE LOGS DO RAILWAY" -ForegroundColor Yellow
Write-Host "=" * 50

# Verificar se Railway CLI esta instalado
if (!(Get-Command "railway" -ErrorAction SilentlyContinue)) {
    Write-Host "Railway CLI nao encontrado!" -ForegroundColor Red
    Write-Host "Instale com: npm install -g @railway/cli" -ForegroundColor Cyan
    exit 1
}

Write-Host "Railway CLI encontrado!" -ForegroundColor Green

# Verificar se esta logado
$whoami = railway whoami 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Nao esta logado no Railway." -ForegroundColor Yellow
    Write-Host "Execute os comandos abaixo para fazer login:" -ForegroundColor Cyan
    Write-Host "1. railway login" -ForegroundColor White
    Write-Host "2. railway link (para conectar ao projeto tennisiq2025)" -ForegroundColor White
    Write-Host "3. Execute este script novamente" -ForegroundColor White
    exit 0
}

Write-Host "Usuario logado: $whoami" -ForegroundColor Green

# Verificar se esta conectado a um projeto
$status = railway status 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Nao esta conectado a um projeto." -ForegroundColor Yellow
    Write-Host "Execute: railway link" -ForegroundColor Cyan
    Write-Host "E selecione o projeto: tennisiq2025" -ForegroundColor White
    exit 0
}

Write-Host "Status do projeto:" -ForegroundColor Green
Write-Host $status

# Criar diretorio de logs
$logDir = "storage\logs\system"
if (!(Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
}

# Capturar logs
$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$logFile = "$logDir\railway_logs_$timestamp.txt"

Write-Host ""
Write-Host "Capturando logs do Railway..." -ForegroundColor Green

# Capturar logs sem parametros especiais
railway logs > $logFile 2>&1

if (Test-Path $logFile) {
    $content = Get-Content $logFile -Raw
    $lineCount = (Get-Content $logFile).Count
    
    Write-Host "Logs capturados: $lineCount linhas" -ForegroundColor Green
    Write-Host "Arquivo: $logFile" -ForegroundColor Cyan
    
    # Analise basica
    Write-Host ""
    Write-Host "ANALISE DOS LOGS:" -ForegroundColor Yellow
    
    $errors = ($content | Select-String "ERROR|ERRO|Exception|Error" -AllMatches).Matches.Count
    $partidas = ($content | Select-String "partidas encontradas|PARTIDAS ENCONTRADAS|partidas analisadas" -AllMatches).Matches.Count
    $oportunidades = ($content | Select-String "oportunidades encontradas|OPORTUNIDADES|sinais" -AllMatches).Matches.Count
    $ciclos = ($content | Select-String "Iniciando|Starting|ciclo|analise" -AllMatches).Matches.Count
    
    Write-Host "Erros encontrados: $errors" -ForegroundColor Red
    Write-Host "Referencias a partidas: $partidas" -ForegroundColor Green
    Write-Host "Referencias a oportunidades: $oportunidades" -ForegroundColor Green
    Write-Host "Possiveis ciclos: $ciclos" -ForegroundColor Green
    
    # Mostrar ultimas 20 linhas
    Write-Host ""
    Write-Host "ULTIMAS 20 LINHAS DOS LOGS:" -ForegroundColor Yellow
    Write-Host "-" * 50
    $lastLines = Get-Content $logFile | Select-Object -Last 20
    foreach ($line in $lastLines) {
        Write-Host $line
    }
    
} else {
    Write-Host "Erro ao capturar logs" -ForegroundColor Red
}

Write-Host ""
Write-Host "Processo concluido!" -ForegroundColor Green
Write-Host "Para analise completa, copie o conteudo do arquivo:" -ForegroundColor Cyan
Write-Host $logFile -ForegroundColor White
