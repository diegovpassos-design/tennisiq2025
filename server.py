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
            "channel_id": os.environ.get('TELEGRAM_CHANNEL_ID')
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
            "TELEGRAM_CHANNEL_ID": "✅" if os.environ.get("TELEGRAM_CHANNEL_ID") else "❌"
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
