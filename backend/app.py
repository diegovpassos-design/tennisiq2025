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

# Configuração de logging mais robusta para Railway
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    force=True  # Força reconfiguração do logging
)

# Configura logging para stdout (Railway)
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

# Handler para stdout
if not root_logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

logger = logging.getLogger(__name__)

class TennisQRailwayApp:
    """Aplicação principal para Railway"""
    
    def __init__(self):
        self.manager = None
        self.db = PreLiveDatabase()
        self.flask_app = Flask(__name__)
        self.running = False
        
        # Silencia logs do Werkzeug (servidor Flask)
        import logging
        werkzeug_logger = logging.getLogger('werkzeug')
        werkzeug_logger.setLevel(logging.WARNING)  # Apenas warnings e erros
        
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
            
        @self.flask_app.route('/dashboard')
        def dashboard():
            """Dashboard simples"""
            try:
                if self.manager:
                    data = self.manager.get_dashboard_data()
                    return {
                        "status": "ok",
                        "data": data,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                else:
                    return {"status": "initializing", "message": "System starting up"}
            except Exception as e:
                return {"status": "error", "error": str(e)}
        
        @self.flask_app.route('/api/stats')
        def api_stats():
            """API de estatísticas"""
            try:
                if self.manager:
                    stats = self.manager.get_dashboard_data().get("statistics", {})
                    return {"status": "ok", "stats": stats}
                else:
                    return {"status": "initializing"}
            except Exception as e:
                return {"status": "error", "error": str(e)}
        
        @self.flask_app.route('/api/matches')
        def api_matches():
            """API de partidas ativas"""
            try:
                if self.manager:
                    matches = self.manager.get_dashboard_data().get("active_opportunities", [])
                    return {"status": "ok", "matches": matches[:20]}  # Limita a 20
                else:
                    return {"status": "initializing", "matches": []}
            except Exception as e:
                return {"status": "error", "error": str(e)}
        
        @self.flask_app.route('/favicon.ico')
        def favicon():
            """Favicon para evitar 404s"""
            return '', 204  # No Content
        
        @self.flask_app.route('/debug')
        def debug_status():
            """Endpoint de debug para ver status detalhado"""
            try:
                status_info = {
                    "system": {
                        "running": self.running,
                        "manager_initialized": self.manager is not None,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                }
                
                if self.manager:
                    try:
                        # Status do serviço de monitoramento
                        service_status = self.manager.monitoring_service.get_service_status()
                        status_info["monitoring_service"] = service_status
                        
                        # Dashboard data
                        dashboard = self.manager.get_dashboard_data()
                        status_info["dashboard"] = dashboard
                        
                        # Status das threads
                        if hasattr(self.manager.monitoring_service, 'scan_thread'):
                            scan_thread = self.manager.monitoring_service.scan_thread
                            status_info["threads"] = {
                                "scan_thread_alive": scan_thread.is_alive() if scan_thread else False,
                                "scan_thread_id": scan_thread.ident if scan_thread else None,
                            }
                            
                        if hasattr(self.manager.monitoring_service, 'monitor_thread'):
                            monitor_thread = self.manager.monitoring_service.monitor_thread
                            status_info["threads"]["monitor_thread_alive"] = monitor_thread.is_alive() if monitor_thread else False
                            status_info["threads"]["monitor_thread_id"] = monitor_thread.ident if monitor_thread else None
                            
                    except Exception as e:
                        status_info["error"] = f"Erro ao buscar status detalhado: {e}"
                
                return status_info
                
            except Exception as e:
                return {"error": f"Erro geral no debug: {e}", "timestamp": datetime.utcnow().isoformat()}
        
        @self.flask_app.route('/force-log')
        def force_log():
            """Força um log de teste"""
            try:
                import time
                timestamp = datetime.utcnow().strftime('%H:%M:%S')
                
                # Tenta várias formas de fazer log
                print(f"🔴 [FORCE-LOG {timestamp}] Log forçado via print")
                logger.info(f"🔴 [FORCE-LOG {timestamp}] Log forçado via logger")
                
                # Flush explícito
                sys.stdout.flush()
                sys.stderr.flush()
                
                # Se o manager existir, força um log nele também
                if self.manager:
                    try:
                        service = self.manager.monitoring_service
                        print(f"🔴 [FORCE-LOG {timestamp}] Service running: {service.running}")
                        
                        if hasattr(service, 'scan_thread') and service.scan_thread:
                            print(f"🔴 [FORCE-LOG {timestamp}] Scan thread alive: {service.scan_thread.is_alive()}")
                            
                        if hasattr(service, 'monitor_thread') and service.monitor_thread:
                            print(f"🔴 [FORCE-LOG {timestamp}] Monitor thread alive: {service.monitor_thread.is_alive()}")
                            
                    except Exception as e:
                        print(f"🔴 [FORCE-LOG {timestamp}] Erro ao verificar threads: {e}")
                
                return {"status": "logs_forced", "timestamp": timestamp}
                
            except Exception as e:
                return {"error": str(e)}
        
        @self.flask_app.route('/manual-scan')
        def manual_scan():
            """Executa um scan manual para teste"""
            try:
                timestamp = datetime.utcnow().strftime('%H:%M:%S')
                print(f"🔴 [MANUAL-SCAN {timestamp}] Iniciando scan manual...")
                
                if not self.manager:
                    return {"error": "Manager não inicializado"}
                
                # Executa scan manual
                opportunities = self.manager.manual_scan()
                
                result = {
                    "status": "scan_completed",
                    "timestamp": timestamp,
                    "opportunities_found": len(opportunities) if opportunities else 0
                }
                
                if opportunities:
                    result["opportunities"] = [
                        {
                            "match": opp.match,
                            "side": opp.side,
                            "odd": opp.odd,
                            "ev": opp.ev,
                            "league": opp.league
                        } for opp in opportunities[:5]  # Primeiras 5
                    ]
                
                print(f"🔴 [MANUAL-SCAN {timestamp}] Concluído: {result['opportunities_found']} oportunidades")
                
                return result
                
            except Exception as e:
                error_msg = f"Erro no scan manual: {e}"
                print(f"🔴 [MANUAL-SCAN] {error_msg}")
                import traceback
                traceback.print_exc()
                return {"error": error_msg}
        
    def start(self):
        """Inicia o sistema"""
        print("🎾 [PRINT] Iniciando TennisQ Pré-Live no Railway...")
        logger.info("🎾 Iniciando TennisQ Pré-Live no Railway...")
        sys.stdout.flush()
        
        try:
            # Verifica configuração
            print("🔧 [PRINT] Verificando configuração...")
            config = self._verify_config()
            print("✅ [PRINT] Configuração verificada!")
            
            # Inicializa o manager
            print("🏗️ [PRINT] Inicializando manager...")
            config_file_path = os.path.join(os.path.dirname(__file__), "config", "config.json")
            self.manager = PreLiveManager(config_path=config_file_path)
            print("✅ [PRINT] Manager inicializado!")
            
            # Inicia o serviço de monitoramento em thread separada (não daemon para debug)
            print("🚀 [PRINT] Iniciando thread de monitoramento...")
            logger.info("🚀 Iniciando thread de monitoramento...")
            monitor_thread = threading.Thread(target=self._start_monitoring_with_debug, daemon=False)
            monitor_thread.start()
            print("✅ [PRINT] Thread de monitoramento iniciada!")
            
            self.running = True
            
            # Envia notificação de início
            print("📱 [PRINT] Enviando notificação de início...")
            self._send_startup_notification()
            print("✅ [PRINT] Notificação enviada!")
            
            logger.info("✅ Sistema iniciado com sucesso!")
            print("🎉 [PRINT] Sistema iniciado com sucesso!")
            
            # Inicia Flask server
            port = int(os.getenv('PORT', 8080))
            print(f"🌐 [PRINT] Iniciando servidor Flask na porta {port}")
            logger.info(f"🌐 Iniciando servidor Flask na porta {port}")
            sys.stdout.flush()
            
            # Roda Flask em modo não-debug para produção
            self.flask_app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
            
        except Exception as e:
            error_msg = f"❌ Erro ao iniciar sistema: {e}"
            print(f"❌ [PRINT] {error_msg}")
            logger.error(error_msg)
            import traceback
            traceback.print_exc()
            logger.error(f"Stack trace: {traceback.format_exc()}")
            self._send_error_notification(str(e))
    
    def _start_monitoring(self):
        """Inicia o serviço de monitoramento"""
        try:
            self.manager.start()
        except Exception as e:
            logger.error(f"Erro no monitoramento: {e}")
            raise
    
    def _start_monitoring_with_debug(self):
        """Inicia o serviço de monitoramento com logs detalhados"""
        try:
            print("🔍 DEBUG: Iniciando serviço de monitoramento...")
            logger.info("🔍 DEBUG: Iniciando serviço de monitoramento...")
            
            # Aguarda um pouco para garantir que tudo está inicializado
            time.sleep(2)
            
            # Inicia o manager
            print("🔍 DEBUG: Chamando manager.start()...")
            logger.info("🔍 DEBUG: Chamando manager.start()...")
            self.manager.start()
            
            print("✅ DEBUG: Monitoramento iniciado com sucesso!")
            logger.info("✅ DEBUG: Monitoramento iniciado com sucesso!")
            
            # Loop de debug simplificado
            debug_count = 0
            while self.running:
                try:
                    debug_count += 1
                    
                    # Log de debug a cada 2 minutos para ver atividade
                    if debug_count % 2 == 0:
                        msg = f"🔍 DEBUG #{debug_count}: Sistema ativo há {debug_count * 2} minutos"
                        print(msg)
                        logger.info(msg)
                        sys.stdout.flush()  # Força flush do stdout
                        
                        # Verifica status básico
                        try:
                            if hasattr(self.manager, 'monitoring_service'):
                                service = self.manager.monitoring_service
                                running_status = service.running
                                msg2 = f"🔍 DEBUG: Serviço running = {running_status}"
                                print(msg2)
                                logger.info(msg2)
                                sys.stdout.flush()
                        except Exception as e:
                            error_msg = f"🔍 DEBUG: Erro ao verificar status: {e}"
                            print(error_msg)
                            logger.error(error_msg)
                            sys.stdout.flush()
                    
                    # Aguarda 1 minuto
                    time.sleep(60)
                    
                except Exception as e:
                    error_msg = f"🔍 DEBUG: Erro no loop de debug: {e}"
                    print(error_msg)
                    logger.error(error_msg)
                    sys.stdout.flush()
                    time.sleep(60)
                    
        except Exception as e:
            critical_msg = f"❌ DEBUG: Erro crítico no monitoramento: {e}"
            print(critical_msg)
            logger.error(critical_msg)
            sys.stdout.flush()
            import traceback
            traceback.print_exc()
            self._send_error_notification(f"Erro crítico no monitoramento: {e}")
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
        
        loop_count = 0
        
        while self.running:
            try:
                loop_count += 1
                
                # Log de heartbeat a cada 10 loops (10 minutos)
                if loop_count % 10 == 0:
                    logger.info(f"💓 Loop principal ativo - ciclo {loop_count}")
                
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
                import traceback
                logger.error(f"Stack trace: {traceback.format_exc()}")
                self._send_error_notification(f"Erro no loop principal: {e}")
                time.sleep(300)  # 5 minutos antes de tentar novamente
    
    def _health_check(self):
        """Verifica se o sistema está funcionando corretamente"""
        try:
            logger.info("🔍 Executando health check...")
            
            status = self.manager.get_dashboard_data()
            service_status = status.get("service_status", {})
            
            # Verifica se as threads estão rodando
            scan_alive = service_status.get("scan_thread_alive", False)
            monitor_alive = service_status.get("monitor_thread_alive", False)
            
            logger.info(f"📊 Status threads - Scan: {scan_alive}, Monitor: {monitor_alive}")
            
            if not service_status.get("running", False):
                logger.warning("⚠️ Serviço não está rodando, tentando reiniciar...")
                self.manager.start()
            
            stats = status.get("statistics", {})
            active_opps = stats.get("active_opportunities", 0)
            total_opps = stats.get("total_opportunities", 0)
            
            logger.info(f"💓 Health check: {active_opps} oportunidades ativas / {total_opps} total")
            
        except Exception as e:
            logger.error(f"❌ Erro no health check: {e}")
            import traceback
            logger.error(f"Stack trace: {traceback.format_exc()}")
    
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
