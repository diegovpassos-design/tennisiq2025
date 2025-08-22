from flask import Flask, jsonify
import os
import sys
import threading
import time
from datetime import datetime

# Adicionar diretório backend ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Importar serviços do TennisQ
try:
    from services.monitoring_service import LineMonitoringService
    from core.database import PreLiveDatabase
    TENNISQ_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Serviços TennisQ não disponíveis: {e}")
    TENNISQ_AVAILABLE = False

app = Flask(__name__)

# Variáveis globais
monitoring_service = None
system_status = {
    "started_at": datetime.now().isoformat(),
    "monitoring_active": False,
    "last_scan": None,
    "opportunities_found": 0,
    "notifications_sent": 0
}

def initialize_tennisq():
    """Inicializa o sistema TennisQ se disponível"""
    global monitoring_service, system_status
    
    if not TENNISQ_AVAILABLE:
        print("❌ TennisQ não disponível - rodando apenas servidor básico")
        return False
        
    try:
        # Verificar variáveis de ambiente
        required_vars = ['API_KEY', 'API_BASE_URL', 'TELEGRAM_BOT_TOKEN', 'TELEGRAM_CHAT_ID']
        missing_vars = [var for var in required_vars if not os.environ.get(var)]
        
        if missing_vars:
            print(f"⚠️ Variáveis faltando: {missing_vars}")
            return False
            
        # Criar arquivo de configuração temporário se não existir
        config_path = "backend/config/config.json"
        config_dir = os.path.dirname(config_path)
        os.makedirs(config_dir, exist_ok=True)
        
        config_data = {
            "api_key": os.environ.get('API_KEY'),
            "api_base_url": os.environ.get('API_BASE_URL'),
            "telegram_token": os.environ.get('TELEGRAM_BOT_TOKEN'),
            "chat_id": os.environ.get('TELEGRAM_CHAT_ID'),
            "channel_id": os.environ.get('TELEGRAM_CHANEL_ID')  # Note: typo no Railway
        }
        
        with open(config_path, 'w') as f:
            import json
            json.dump(config_data, f, indent=2)
        
        print(f"📝 Arquivo de configuração criado: {config_path}")
        
        # Inicializar database
        print("🔧 Inicializando database...")
        database = PreLiveDatabase()
        
        # Inicializar monitoring service
        print("🔧 Inicializando monitoring service...")
        monitoring_service = LineMonitoringService(config_path="backend/config/config.json")
        
        # Enviar notificação de startup
        print("📱 Enviando notificação de startup...")
        startup_thread = threading.Thread(target=monitoring_service.send_startup_notification)
        startup_thread.daemon = True
        startup_thread.start()
        
        system_status["monitoring_active"] = True
        print("✅ TennisQ inicializado com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao inicializar TennisQ: {e}")
        return False

def start_monitoring():
    """Inicia o monitoramento em background"""
    global system_status
    
    if not monitoring_service:
        return
        
    def monitor_loop():
        while True:
            try:
                print("🔍 Executando scan...")
                system_status["last_scan"] = datetime.now().isoformat()
                
                # Executar scan (isso chamará o monitoring_service internamente)
                # Por enquanto, apenas um placeholder
                time.sleep(300)  # 5 minutos entre scans
                
            except Exception as e:
                print(f"❌ Erro no monitoring: {e}")
                time.sleep(60)  # Esperar 1 minuto antes de tentar novamente
    
    monitor_thread = threading.Thread(target=monitor_loop)
    monitor_thread.daemon = True
    monitor_thread.start()
    print("🚀 Monitoring iniciado em background")

@app.route('/')
def home():
    status_icon = "🟢" if system_status["monitoring_active"] else "🟡"
    tennisq_status = "ATIVO" if TENNISQ_AVAILABLE and system_status["monitoring_active"] else "BÁSICO"
    
    return f"""
    <h1>🎾 TennisQ v2.0 - Sistema Online</h1>
    <p>Status: <strong>{status_icon} {tennisq_status}</strong></p>
    <p>Deploy: <strong>SUCESSO</strong></p>
    <p>Iniciado: <strong>{system_status["started_at"][:19]}</strong></p>
    <p>Último Scan: <strong>{system_status["last_scan"][:19] if system_status["last_scan"] else "Aguardando..."}</strong></p>
    <hr>
    <p><a href="/health">Health Check</a></p>
    <p><a href="/status">Status Completo</a></p>
    <p><a href="/api/stats">Estatísticas API</a></p>
    <p><a href="/api/start-monitoring">Iniciar Monitoring</a></p>
    """

@app.route('/health')
def health():
    return jsonify({
        "status": "ok", 
        "service": "TennisQ", 
        "version": "2.0",
        "tennisq_available": TENNISQ_AVAILABLE,
        "monitoring_active": system_status["monitoring_active"]
    })

@app.route('/status')
def status():
    return jsonify({
        "status": "online",
        "service": "TennisQ",
        "version": "2.0", 
        "timestamp": datetime.now().isoformat(),
        "port": os.environ.get("PORT", "8080"),
        "tennisq_available": TENNISQ_AVAILABLE,
        "system_status": system_status,
        "environment_vars": {
            "API_BASE_URL": "✅" if os.environ.get("API_BASE_URL") else "❌",
            "TELEGRAM_BOT_TOKEN": "✅" if os.environ.get("TELEGRAM_BOT_TOKEN") else "❌", 
            "TELEGRAM_CHAT_ID": "✅" if os.environ.get("TELEGRAM_CHAT_ID") else "❌",
            "TELEGRAM_CHANNEL_ID": "✅" if os.environ.get("TELEGRAM_CHANEL_ID") else "❌",
            "DEBUG_ALL_VARS": {k: v for k, v in os.environ.items() if k.startswith('TELEGRAM')}
        }
    })

@app.route('/api/stats')
def api_stats():
    return jsonify({
        "service": "TennisQ Stats",
        "started_at": system_status["started_at"],
        "monitoring_active": system_status["monitoring_active"],
        "last_scan": system_status["last_scan"],
        "opportunities_found": system_status["opportunities_found"],
        "notifications_sent": system_status["notifications_sent"],
        "tennisq_available": TENNISQ_AVAILABLE
    })

@app.route('/api/start-monitoring')
def api_start_monitoring():
    if not TENNISQ_AVAILABLE:
        return jsonify({"error": "TennisQ não disponível"}), 400
        
    if not monitoring_service:
        return jsonify({"error": "Monitoring service não inicializado"}), 400
        
    if not system_status["monitoring_active"]:
        start_monitoring()
        return jsonify({"message": "Monitoring iniciado", "status": "success"})
    else:
        return jsonify({"message": "Monitoring já está ativo", "status": "info"})

@app.route('/api/matches')
def api_matches():
    """Retorna partidas sendo monitoradas"""
    if not monitoring_service:
        return jsonify({"error": "Monitoring service não disponível"}), 400
    
    try:
        # Buscar partidas do database
        db = monitoring_service.db
        opportunities = db.get_recent_opportunities(limit=50)
        
        matches_data = []
        for opp in opportunities:
            matches_data.append({
                "id": opp.get("id"),
                "event_id": opp.get("event_id"),
                "home_team": opp.get("home_team"),
                "away_team": opp.get("away_team"),
                "start_time": opp.get("start_time"),
                "probability": opp.get("probability"),
                "current_odds": opp.get("current_odds"),
                "recommended_odds": opp.get("recommended_odds"),
                "created_at": opp.get("created_at"),
                "status": "active" if opp.get("probability", 0) > 0.6 else "low_prob"
            })
        
        return jsonify({
            "total_matches": len(matches_data),
            "active_opportunities": len([m for m in matches_data if m["status"] == "active"]),
            "matches": matches_data
        })
        
    except Exception as e:
        return jsonify({"error": f"Erro ao buscar partidas: {str(e)}"}), 500

@app.route('/api/live-scan')
def api_live_scan():
    """Força um scan manual e retorna resultados"""
    if not monitoring_service:
        return jsonify({"error": "Monitoring service não disponível"}), 400
    
    try:
        print("🔍 Executando scan manual via API...")
        
        # Executar scan
        scanner = monitoring_service.scanner
        events = scanner.get_upcoming_events()
        
        scan_results = {
            "scan_time": datetime.now().isoformat(),
            "total_events": len(events),
            "events": []
        }
        
        for event in events[:10]:  # Limitar a 10 para não sobrecarregar
            try:
                probability = scanner.calculate_probability(event)
                scan_results["events"].append({
                    "id": event.get("id"),
                    "home": event.get("home", {}).get("name", "N/A"),
                    "away": event.get("away", {}).get("name", "N/A"),
                    "start_time": event.get("time"),
                    "probability": round(probability, 3) if probability else 0,
                    "status": "opportunity" if probability and probability > 0.6 else "normal"
                })
            except Exception as e:
                scan_results["events"].append({
                    "id": event.get("id", "unknown"),
                    "error": str(e)
                })
        
        return jsonify(scan_results)
        
    except Exception as e:
        return jsonify({"error": f"Erro no scan: {str(e)}"}), 500

@app.route('/dashboard')
def dashboard():
    """Dashboard visual para monitoramento"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>TennisQ Dashboard</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
            .header { background: #2c3e50; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
            .stats { display: flex; gap: 20px; margin-bottom: 20px; }
            .stat-card { background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); flex: 1; }
            .matches { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .match { border-bottom: 1px solid #eee; padding: 10px 0; }
            .high-prob { background: #e8f5e8; border-left: 4px solid #27ae60; }
            .refresh-btn { background: #3498db; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; }
            .refresh-btn:hover { background: #2980b9; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🎾 TennisQ Dashboard</h1>
            <p>Monitoramento em Tempo Real</p>
        </div>
        
        <div class="stats" id="stats">
            <div class="stat-card">
                <h3>Status Sistema</h3>
                <p id="system-status">Carregando...</p>
            </div>
            <div class="stat-card">
                <h3>Último Scan</h3>
                <p id="last-scan">Carregando...</p>
            </div>
            <div class="stat-card">
                <h3>Oportunidades</h3>
                <p id="opportunities">Carregando...</p>
            </div>
        </div>
        
        <div class="matches">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <h2>Partidas Monitoradas</h2>
                <div>
                    <button class="refresh-btn" onclick="refreshData()">🔄 Atualizar</button>
                    <button class="refresh-btn" onclick="forceScan()">🔍 Scan Manual</button>
                </div>
            </div>
            <div id="matches-list">Carregando partidas...</div>
        </div>
        
        <script>
            function formatTime(isoTime) {
                if (!isoTime) return 'N/A';
                return new Date(isoTime).toLocaleString('pt-BR');
            }
            
            async function loadStats() {
                try {
                    const response = await fetch('/api/stats');
                    const data = await response.json();
                    
                    document.getElementById('system-status').innerHTML = 
                        data.monitoring_active ? '🟢 Ativo' : '🔴 Inativo';
                    document.getElementById('last-scan').innerHTML = 
                        formatTime(data.last_scan);
                    document.getElementById('opportunities').innerHTML = 
                        `${data.opportunities_found} encontradas`;
                } catch (e) {
                    console.error('Erro ao carregar stats:', e);
                }
            }
            
            async function loadMatches() {
                try {
                    const response = await fetch('/api/matches');
                    const data = await response.json();
                    
                    const matchesList = document.getElementById('matches-list');
                    
                    if (data.matches && data.matches.length > 0) {
                        matchesList.innerHTML = data.matches.map(match => `
                            <div class="match ${match.probability > 0.6 ? 'high-prob' : ''}">
                                <strong>${match.home_team} vs ${match.away_team}</strong><br>
                                <small>Probabilidade: ${(match.probability * 100).toFixed(1)}% | 
                                Odds: ${match.current_odds} | 
                                ${formatTime(match.start_time)}</small>
                            </div>
                        `).join('');
                    } else {
                        matchesList.innerHTML = '<p>Nenhuma partida encontrada no momento.</p>';
                    }
                } catch (e) {
                    document.getElementById('matches-list').innerHTML = '<p>Erro ao carregar partidas.</p>';
                    console.error('Erro ao carregar partidas:', e);
                }
            }
            
            async function forceScan() {
                document.getElementById('matches-list').innerHTML = '<p>🔍 Executando scan...</p>';
                try {
                    const response = await fetch('/api/live-scan');
                    const data = await response.json();
                    
                    const matchesList = document.getElementById('matches-list');
                    if (data.events && data.events.length > 0) {
                        matchesList.innerHTML = '<h3>Resultados do Scan:</h3>' + 
                            data.events.map(event => `
                                <div class="match ${event.probability > 0.6 ? 'high-prob' : ''}">
                                    <strong>${event.home} vs ${event.away}</strong><br>
                                    <small>Probabilidade: ${(event.probability * 100).toFixed(1)}% | 
                                    ${formatTime(event.start_time)}</small>
                                </div>
                            `).join('');
                    } else {
                        matchesList.innerHTML = '<p>Nenhum evento encontrado no scan.</p>';
                    }
                } catch (e) {
                    document.getElementById('matches-list').innerHTML = '<p>Erro no scan manual.</p>';
                }
            }
            
            function refreshData() {
                loadStats();
                loadMatches();
            }
            
            // Carregar dados iniciais
            refreshData();
            
            // Auto-refresh a cada 30 segundos
            setInterval(refreshData, 30000);
        </script>
    </body>
    </html>
    """

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    print(f"🚀 TennisQ iniciando na porta {port}")
    
    # Inicializar TennisQ
    if initialize_tennisq():
        print("✅ Sistema completo inicializado!")
        # Aguardar um pouco antes de iniciar monitoring
        time.sleep(3)
        start_monitoring()
    else:
        print("⚠️ Rodando apenas servidor básico")
    
    app.run(host='0.0.0.0', port=port, debug=False)
