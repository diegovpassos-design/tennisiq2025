# Script para capturar logs do Railway via Web ou instrucoes
# Executar: .\scripts\capturar_logs_railway.ps1

Write-Host "Analise de logs do Railway..." -ForegroundColor Yellow
Write-Host "=" * 50

# Verificar se Railway CLI esta instalado
if (!(Get-Command "railway" -ErrorAction SilentlyContinue)) {
    Write-Host "Railway CLI nao encontrado!" -ForegroundColor Red
    Write-Host ""
    Write-Host "INSTRUCOES PARA ACESSAR LOGS:" -ForegroundColor Cyan
    Write-Host "1. Acesse: https://railway.app/dashboard" -ForegroundColor White
    Write-Host "2. Entre no projeto: tennisiq2025" -ForegroundColor White
    Write-Host "3. Clique na aba 'Logs' ou 'Deployments'" -ForegroundColor White
    Write-Host "4. Visualize os logs das ultimas 3 horas" -ForegroundColor White
    Write-Host "5. Copie os logs e cole para analise" -ForegroundColor White
    Write-Host ""
    Write-Host "INSTALACAO DO RAILWAY CLI (OPCIONAL):" -ForegroundColor Yellow
    Write-Host "1. Instale Node.js: https://nodejs.org" -ForegroundColor White
    Write-Host "2. Execute: npm install -g @railway/cli" -ForegroundColor White
    Write-Host "3. Execute: railway login" -ForegroundColor White
    Write-Host "4. Execute: railway link" -ForegroundColor White
    Write-Host "5. Execute: railway logs" -ForegroundColor White
    Write-Host ""
    Write-Host "O QUE PROCURAR NOS LOGS:" -ForegroundColor Green
    Write-Host "- Quantos ciclos de analise foram executados" -ForegroundColor White
    Write-Host "- Quantas partidas foram encontradas por ciclo" -ForegroundColor White
    Write-Host "- Quantas passaram no filtro de timing (prioridade = 4)" -ForegroundColor White
    Write-Host "- Se houve alguma virada mental detectada" -ForegroundColor White
    Write-Host "- Se houve erros de API ou conexao" -ForegroundColor White
    Write-Host "- Performance do sistema (tempo de resposta)" -ForegroundColor White
    Write-Host ""
    Write-Host "ANALISE ESPERADA EM 3 HORAS:" -ForegroundColor Yellow
    Write-Host "- Aproximadamente 36 ciclos (5 minutos cada)" -ForegroundColor White
    Write-Host "- Centenas de partidas analisadas" -ForegroundColor White
    Write-Host "- Poucas (ou nenhuma) com prioridade exatamente 4" -ForegroundColor White
    Write-Host "- Sistema funcionando mas criterios muito especificos" -ForegroundColor White
    
    # Verificar logs locais existentes
    $logDir = "storage\logs\system"
    if (Test-Path $logDir) {
        $localLogs = Get-ChildItem $logDir -Filter "*.log" -ErrorAction SilentlyContinue
        if ($localLogs.Count -gt 0) {
            Write-Host ""
            Write-Host "LOGS LOCAIS ENCONTRADOS:" -ForegroundColor Green
            foreach ($log in $localLogs) {
                Write-Host "   - $($log.Name) ($($log.Length) bytes)" -ForegroundColor White
            }
        }
    }
    
    exit 0
}

# Se Railway CLI estiver instalado, capturar logs
Write-Host "Railway CLI encontrado!" -ForegroundColor Green

# Criar diretorio de logs se nao existir
$logDir = "storage\logs\system"
if (!(Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
}

# Capturar logs das ultimas 3 horas
$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$logFile = "$logDir\railway_logs_$timestamp.txt"

Write-Host "Capturando logs..." -ForegroundColor Green
railway logs --tail 2000 > $logFile

if (Test-Path $logFile) {
    $lineCount = (Get-Content $logFile).Count
    Write-Host "Logs capturados: $lineCount linhas" -ForegroundColor Green
    Write-Host "Arquivo: $logFile" -ForegroundColor Cyan
    
    # Mostrar estatisticas basicas
    Write-Host ""
    Write-Host "ANALISE RAPIDA:" -ForegroundColor Yellow
    $content = Get-Content $logFile -Raw
    
    $errors = ($content | Select-String "ERROR|ERRO" -AllMatches).Matches.Count
    $warnings = ($content | Select-String "WARNING|WARN" -AllMatches).Matches.Count
    $partidas = ($content | Select-String "partidas encontradas|PARTIDAS ENCONTRADAS" -AllMatches).Matches.Count
    $oportunidades = ($content | Select-String "oportunidades encontradas|OPORTUNIDADES" -AllMatches).Matches.Count
    
    Write-Host "Erros: $errors" -ForegroundColor Red
    Write-Host "Avisos: $warnings" -ForegroundColor Yellow
    Write-Host "Partidas: $partidas" -ForegroundColor Green
    Write-Host "Oportunidades: $oportunidades" -ForegroundColor Green
    
} else {
    Write-Host "Erro ao capturar logs" -ForegroundColor Red
}

Write-Host ""
Write-Host "Processo concluido!" -ForegroundColor Green
