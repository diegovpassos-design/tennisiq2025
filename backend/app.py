"""
TennisQ Pré-Live - Sistema para Railway
Sistema automatizado que roda em background e envia notificações via Telegram
"""

import json
import logging
import sys
import os
import time
import signal
import threading
from datetime import datetime
from flask import Flask

# Adiciona o path do backend
sys.path.append(os.path.dirname(__file__))

from services.monitoring_service import PreLiveManager
from core.database import PreLiveDatabase

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TennisQRailwayApp:
    """Aplicação principal para Railway"""
    
    def __init__(self):
        self.manager = None
        self.db = PreLiveDatabase()
        self.flask_app = Flask(__name__)
        self.running = False
        self.setup_flask_routes()
        
    def setup_flask_routes(self):
        """Configura rotas Flask"""
        
        @self.flask_app.route('/')
        def health_check():
            return {
                "status": "running",
                "service": "TennisQ Pré-Live",
                "timestamp": datetime.utcnow().isoformat()
            }
        
    def start(self):
        """Inicia o sistema"""
        logger.info("🎾 Iniciando TennisQ Pré-Live no Railway...")
        
        try:
            # Verifica configuração
            config = self._verify_config()
            
            # Inicializa o manager
            # Configura manager com path correto
            config_file_path = os.path.join(os.path.dirname(__file__), "config", "config.json")
            self.manager = PreLiveManager(config_path=config_file_path)
            
            # Inicia o serviço de monitoramento em thread separada
            monitor_thread = threading.Thread(target=self._start_monitoring, daemon=True)
            monitor_thread.start()
            
            self.running = True
            
            # Envia notificação de início
            self._send_startup_notification()
            
            logger.info("✅ Sistema iniciado com sucesso!")
            
            # Inicia Flask server
            port = int(os.getenv('PORT', 8080))
            self.flask_app.run(host='0.0.0.0', port=port, debug=False)
            
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar sistema: {e}")
            self._send_error_notification(str(e))
    
    def _start_monitoring(self):
        """Inicia o serviço de monitoramento"""
        try:
            self.manager.start()
        except Exception as e:
            logger.error(f"Erro no monitoramento: {e}")
            raise
    
    def stop(self):
        """Para o sistema"""
        logger.info("⏹️ Parando TennisQ Pré-Live...")
        
        self.running = False
        
        if self.manager:
            self.manager.stop()
        
        logger.info("✅ Sistema parado com sucesso!")
    
    def _verify_config(self):
        """Verifica se a configuração está correta"""
        config_path = os.path.join(os.path.dirname(__file__), "config", "config.json")
        
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Arquivo de configuração não encontrado: {config_path}")
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        required_keys = ["api_key", "telegram_token", "chat_id", "api_base_url"]
        missing_keys = [key for key in required_keys if not config.get(key)]
        
        if missing_keys:
            raise ValueError(f"Chaves de configuração faltando: {missing_keys}")
        
        logger.info("✅ Configuração verificada com sucesso")
    
    def _send_startup_notification(self):
        """Envia notificação de que o sistema foi iniciado"""
        try:
            import requests
            
            config_path = os.path.join(os.path.dirname(__file__), "config", "config.json")
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            message = (
                "🚀 **TennisQ Pré-Live INICIADO**\\n\\n"
                f"⏰ Hora: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC\\n"
                "🔍 Monitoramento ativo para oportunidades pré-live\\n"
                "📊 Sistema rodando no Railway\\n\\n"
                "O sistema irá escanear automaticamente e enviar "
                "notificações quando encontrar oportunidades!"
            )
            
            url = f"https://api.telegram.org/bot{config['telegram_token']}/sendMessage"
            data = {
                "chat_id": config["chat_id"],
                "text": message,
                "parse_mode": "Markdown"
            }
            
            response = requests.post(url, data=data, timeout=10)
            response.raise_for_status()
            
            logger.info("📱 Notificação de início enviada")
            
        except Exception as e:
            logger.warning(f"⚠️ Erro ao enviar notificação de início: {e}")
    
    def _send_error_notification(self, error_message: str):
        """Envia notificação de erro"""
        try:
            import requests
            
            config_path = os.path.join(os.path.dirname(__file__), "config", "config.json")
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            message = (
                "❌ **ERRO NO TENNISQ PRÉ-LIVE**\\n\\n"
                f"⏰ Hora: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC\\n"
                f"💥 Erro: {error_message}\\n\\n"
                "O sistema tentará reiniciar automaticamente."
            )
            
            url = f"https://api.telegram.org/bot{config['telegram_token']}/sendMessage"
            data = {
                "chat_id": config["chat_id"],
                "text": message,
                "parse_mode": "Markdown"
            }
            
            requests.post(url, data=data, timeout=10)
            
        except Exception as e:
            logger.error(f"Erro ao enviar notificação de erro: {e}")
    
    def _main_loop(self):
        """Loop principal que mantém o processo vivo"""
        logger.info("🔄 Entrando no loop principal...")
        
        last_health_check = datetime.utcnow()
        health_check_interval = 3600  # 1 hora
        
        while self.running:
            try:
                # Health check periódico
                now = datetime.utcnow()
                if (now - last_health_check).total_seconds() >= health_check_interval:
                    self._health_check()
                    last_health_check = now
                
                # Dorme por 60 segundos
                time.sleep(60)
                
            except KeyboardInterrupt:
                logger.info("🛑 Interrompido pelo usuário")
                break
            except Exception as e:
                logger.error(f"❌ Erro no loop principal: {e}")
                self._send_error_notification(f"Erro no loop principal: {e}")
                time.sleep(300)  # 5 minutos antes de tentar novamente
    
    def _health_check(self):
        """Verifica se o sistema está funcionando corretamente"""
        try:
            status = self.manager.get_dashboard_data()
            service_status = status.get("service_status", {})
            
            if not service_status.get("running", False):
                logger.warning("⚠️ Serviço não está rodando, tentando reiniciar...")
                self.manager.start()
            
            stats = status.get("statistics", {})
            active_opps = stats.get("active_opportunities", 0)
            
            logger.info(f"💓 Health check: {active_opps} oportunidades ativas")
            
        except Exception as e:
            logger.error(f"❌ Erro no health check: {e}")
    
    def get_status(self):
        """Retorna status do sistema para monitoramento externo"""
        if not self.manager:
            return {"status": "stopped", "message": "Manager não inicializado"}
        
        try:
            data = self.manager.get_dashboard_data()
            return {
                "status": "running" if self.running else "stopped",
                "service_running": data.get("service_status", {}).get("running", False),
                "active_opportunities": len(data.get("active_opportunities", [])),
                "statistics": data.get("statistics", {}),
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

# Variável global para a aplicação
app_instance = None

def signal_handler(signum, frame):
    """Handler para sinais do sistema"""
    logger.info(f"📡 Sinal recebido: {signum}")
    if app_instance:
        app_instance.stop()
    sys.exit(0)

def main():
    """Função principal"""
    global app_instance
    
    # Configura handlers de sinal
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Cria e inicia a aplicação
    app_instance = TennisQRailwayApp()
    
    try:
        app_instance.start()
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
