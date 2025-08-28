"""
Serviço de monitoramento de linha - executa periodicamente
para acompanhar movimento de odds e atualizar oportunidades
"""

import time
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict
import threading
from pathlib import Path

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.prelive_scanner import PreLiveScanner
from core.database import PreLiveDatabase

logger = logging.getLogger(__name__)

class LineMonitoringService:
    def __init__(self, config_path: str = "backend/config/config.json"):
        # Tentar carregar config de várias localizações
        config_paths = [
            config_path,
            "../config/config.json", 
            "config/config.json",
            "backend/config/config.json"
        ]
        
        config_loaded = False
        for path in config_paths:
            try:
                with open(path, 'r') as f:
                    self.config = json.load(f)
                logger.info(f"✅ Config carregada de: {path}")
                config_loaded = True
                break
            except FileNotFoundError:
                continue
        
        if not config_loaded:
            # Usar variáveis de ambiente como fallback
            logger.warning("⚠️ Config file não encontrado, usando variáveis de ambiente")
            self.config = {
                "api_key": os.environ.get("API_KEY", "226997-BVn3XP4cGLAUfL"),
                "api_base_url": os.environ.get("API_BASE_URL", "https://api.b365api.com"),
                "telegram_token": os.environ.get("TELEGRAM_TOKEN", ""),
                "chat_id": os.environ.get("CHAT_ID", ""),
                "channel_id": os.environ.get("CHANNEL_ID", "")
            }
        
        logger.info(f"🔑 Usando API Key: {self.config['api_key'][:10]}...")
        
        self.scanner = PreLiveScanner(
            api_token=self.config["api_key"],
            api_base=self.config["api_base_url"]
        )
        
        self.db = PreLiveDatabase()
        self.running = False
        self.scan_thread = None
        self.monitor_thread = None
        
        # Arquivo para manter contador contínuo de oportunidades
        self.counter_file = "storage/opportunity_counter.json"
        self._ensure_counter_file()
        
    def start_service(self):
        """Inicia o serviço de monitoramento"""
        if self.running:
            logger.warning("⚠️ LineMonitoringService: Serviço já está rodando")
            return
            
        logger.info("🔄 LineMonitoringService: Iniciando serviço...")
        self.running = True
        
        # Thread para escanear novas oportunidades
        logger.info("🧵 LineMonitoringService: Criando thread de scan...")
        self.scan_thread = threading.Thread(target=self._scan_loop, daemon=True)
        self.scan_thread.start()
        logger.info(f"✅ LineMonitoringService: Thread de scan iniciada - ID: {self.scan_thread.ident}")
        
        # Thread para monitorar movimento de linha
        logger.info("🧵 LineMonitoringService: Criando thread de monitoramento...")
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info(f"✅ LineMonitoringService: Thread de monitoramento iniciada - ID: {self.monitor_thread.ident}")
        
        logger.info("🎉 LineMonitoringService: Serviço de monitoramento completamente iniciado!")
    
    def stop_service(self):
        """Para o serviço de monitoramento"""
        logger.info("⏹️ LineMonitoringService: Parando serviço...")
        self.running = False
        logger.info("✅ LineMonitoringService: Serviço de monitoramento parado")
    
    def _ensure_counter_file(self):
        """Garante que o arquivo de contador existe"""
        try:
            os.makedirs("storage", exist_ok=True)
            if not os.path.exists(self.counter_file):
                with open(self.counter_file, 'w') as f:
                    json.dump({"counter": 0}, f)
                logger.info("📊 Arquivo de contador criado")
        except Exception as e:
            logger.warning(f"⚠️ Erro ao criar arquivo de contador: {e}")
    
    def _get_next_opportunity_number(self):
        """Obtém o próximo número da oportunidade (contínuo entre ciclos)"""
        try:
            with open(self.counter_file, 'r') as f:
                data = json.load(f)
            
            current_counter = data.get("counter", 0)
            next_counter = current_counter + 1
            
            # Atualiza o contador no arquivo
            with open(self.counter_file, 'w') as f:
                json.dump({"counter": next_counter}, f)
            
            return next_counter
        except Exception as e:
            logger.warning(f"⚠️ Erro ao ler contador: {e}, usando 1")
            return 1
    
    def _get_current_counter(self):
        """Obtém o contador atual sem incrementar"""
        try:
            with open(self.counter_file, 'r') as f:
                data = json.load(f)
            return data.get("counter", 0)
        except Exception as e:
            logger.warning(f"⚠️ Erro ao ler contador atual: {e}")
            return 0
    
    def _update_counter_batch(self, count):
        """Atualiza o contador após enviar um lote de oportunidades"""
        try:
            current_counter = self._get_current_counter()
            new_counter = current_counter + count
            
            with open(self.counter_file, 'w') as f:
                json.dump({"counter": new_counter}, f)
            
            logger.info(f"📊 Contador atualizado: {current_counter} → {new_counter}")
        except Exception as e:
            logger.warning(f"⚠️ Erro ao atualizar contador: {e}")
    
    def stop_service(self):
        """Para o serviço de monitoramento"""
        logger.info("⏹️ LineMonitoringService: Parando serviço...")
        self.running = False
        logger.info("✅ LineMonitoringService: Serviço de monitoramento parado")
    
    def _scan_loop(self):
        """Loop principal para escanear novas oportunidades"""
        while self.running:
            try:
                logger.info("🔍 Iniciando escaneamento de novas oportunidades...")
                
                # Limpeza de oportunidades enviadas expiradas
                logger.info("🧹 Limpando oportunidades expiradas...")
                self.db.cleanup_expired_sent_opportunities()
                
                # Escaneia oportunidades com timeout
                logger.info("📡 Fazendo scan da API...")
                opportunities = self.scanner.scan_opportunities(
                    hours_ahead=72,
                    min_ev=0.10,   # EV mínimo de 10% (ATUALIZADO)
                    odd_min=1.80,  # Range ajustado conforme solicitado
                    odd_max=2.40   # Range ajustado conforme solicitado
                )
                
                logger.info(f"📊 Encontradas {len(opportunities) if opportunities else 0} oportunidades")
                
                if opportunities:
                    # Salva no banco
                    saved_count = self.db.save_opportunities(opportunities)
                    logger.info(f"💾 Salvas {saved_count} novas oportunidades")
                    
                    # Envia notificação de TODAS as oportunidades
                    self._notify_best_opportunities(opportunities)
                else:
                    logger.info("📭 Nenhuma oportunidade encontrada neste scan")
                
                # Aguarda 3 horas com logs intermediários
                logger.info("😴 Aguardando 3 horas até próximo scan...")
                self._sleep_with_heartbeat(1 * 3600, "⏰ Próximo scan em")  # 1 hora
                
            except Exception as e:
                logger.error(f"❌ Erro no loop de escaneamento: {e}")
                import traceback
                logger.error(f"Stack trace: {traceback.format_exc()}")
                self._sleep_with_interrupt(300)  # 5 minutos em caso de erro
    
    def _monitor_loop(self):
        """Loop para monitorar movimento de linha das oportunidades ativas"""
        while self.running:
            try:
                logger.info("📈 Monitorando movimento de linha...")
                
                # Busca oportunidades ativas
                active_opps = self.db.get_active_opportunities(min_hours_ahead=0.5)
                
                events_to_monitor = set()
                for opp in active_opps:
                    events_to_monitor.add(opp["event_id"])
                
                logger.info(f"🎯 Monitorando {len(events_to_monitor)} eventos")
                
                # Monitora cada evento
                monitored_count = 0
                for event_id in events_to_monitor:
                    try:
                        odds_data = self.scanner.get_event_odds(event_id)
                        if odds_data:
                            # Salva movimento de linha
                            self.db.save_line_movement(
                                event_id=event_id,
                                home_od=odds_data.home_od,
                                away_od=odds_data.away_od,
                                timestamp=odds_data.timestamp
                            )
                            monitored_count += 1
                        
                        # Pausa pequena entre requests
                        time.sleep(1)
                        
                    except Exception as e:
                        logger.warning(f"⚠️ Erro ao monitorar evento {event_id}: {e}")
                
                logger.info(f"✅ Monitoramento concluído: {monitored_count}/{len(events_to_monitor)} eventos atualizados")
                
                # Aguarda 30 minutos com logs intermediários
                self._sleep_with_heartbeat(30 * 60, "📊 Próximo monitoramento em")  # 30 minutos
                
            except Exception as e:
                logger.error(f"❌ Erro no loop de monitoramento: {e}")
                import traceback
                logger.error(f"Stack trace: {traceback.format_exc()}")
                self._sleep_with_interrupt(300)  # 5 minutos em caso de erro
    
    def _notify_best_opportunities(self, opportunities: List):
        """Envia notificação das melhores oportunidades via Telegram - cada jogo separadamente"""
        if not opportunities:
            return
        
        logger.info("� Processando TODAS as oportunidades encontradas (sem filtro de tempo)")
        
        # Filtra oportunidades que já foram enviadas
        new_opportunities = []
        for opp in opportunities:
            if not self.db.is_opportunity_already_sent(opp):
                new_opportunities.append(opp)
                
                # Log do tempo até o jogo para informação
                try:
                    from datetime import datetime
                    now = datetime.utcnow()
                    start_dt = datetime.fromisoformat(opp.start_utc.replace('Z', ''))
                    hours_until_game = (start_dt - now).total_seconds() / 3600
                    logger.info(f"✅ Oportunidade aceita: {opp.match} em {hours_until_game:.1f}h")
                except Exception as e:
                    logger.info(f"✅ Oportunidade aceita: {opp.match} (erro ao calcular tempo)")
            else:
                logger.info(f"Oportunidade já enviada: {opp.match} - {opp.side}")
        
        if not new_opportunities:
            logger.info("Todas as oportunidades já foram enviadas anteriormente")
            return
            
        try:
            # Obtém o contador inicial para este lote
            starting_counter = self._get_current_counter()
            
            # Envia cada oportunidade como mensagem separada com numeração contínua
            for i, opp in enumerate(new_opportunities):
                opportunity_number = starting_counter + i + 1
                # ⚠️ VALIDAÇÃO DE ODDS ANTES DE ENVIAR
                current_odds = self.scanner.get_event_odds(opp.event_id)
                if current_odds:
                    # Verifica se as odds mudaram significativamente (>10%)
                    odds_changed = False
                    current_odd = current_odds.home_od if opp.side == "HOME" else current_odds.away_od
                    
                    if abs(current_odd - opp.odd) / opp.odd > 0.10:  # 10% de diferença
                        odds_changed = True
                        logger.warning(f"⚠️ Odds mudaram significativamente para {opp.match}: {opp.odd} → {current_odd}")
                
                ev_percent = opp.ev * 100
                
                # Determina qual jogador apostar baseado no lado
                home_player, away_player = opp.match.split(' vs ')
                target_player = home_player if opp.side == "HOME" else away_player
                
                # Extrai data e hora do start_utc e converte para timezone brasileiro
                from datetime import datetime, timezone, timedelta
                start_dt = datetime.fromisoformat(opp.start_utc.replace('Z', '+00:00'))
                
                # Converte para horário brasileiro (UTC-3)
                br_timezone = timezone(timedelta(hours=-3))
                start_dt_br = start_dt.astimezone(br_timezone)
                
                date_str = start_dt_br.strftime('%d/%m')
                time_str = start_dt_br.strftime('%H:%M')
                
                # Cria mensagem individual com formato completo
                message = f"🎾 OPORTUNIDADE {opportunity_number}\n\n"
                message += f"🏆 {opp.league}\n"
                message += f"⚔️ {opp.match}\n"
                message += f"🎯 **{target_player}** @ {opp.odd}\n"
                message += f"📊 EV: **{ev_percent:.1f}%** (10-15% range)\n"
                message += f"📅 {date_str} às {time_str}"
                
                # ⚠️ ADICIONA AVISO SE ODDS MUDARAM
                if current_odds and abs(current_odd - opp.odd) / opp.odd > 0.10:
                    message += f"\n\n⚠️ **ATENÇÃO**: Odds atual @ {current_odd:.2f}"
                    message += f"\n🔄 Verificar casa de apostas antes de apostar"
                
                # Envia cada mensagem separadamente
                self._send_telegram_message(message)
                
                # Marca como enviada para evitar duplicatas
                self.db.mark_opportunity_as_sent(opp)
                
                # Pequena pausa entre mensagens para não spammar
                import time
                time.sleep(1)
                
            # Atualiza o contador após enviar todas as oportunidades
            self._update_counter_batch(len(new_opportunities))
                
            # Mensagem final de resumo
            
            logger.info(f"Enviadas {len(new_opportunities)} novas oportunidades de {len(opportunities)} encontradas")
            
        except Exception as e:
            logger.error(f"Erro ao enviar notificação: {e}")
    
    def _send_telegram_message(self, message: str):
        """Envia mensagem via Telegram"""
        try:
            import requests
            
            url = f"https://api.telegram.org/bot{self.config['telegram_token']}/sendMessage"
            
            # Usa o canal em vez do chat privado para oportunidades
            target_chat = self.config.get("channel_id") or self.config.get("chat_id")
            
            data = {
                "chat_id": target_chat,
                "text": message
            }
            
            response = requests.post(url, data=data, timeout=10)
            response.raise_for_status()
            
            logger.info(f"Notificação enviada via Telegram para {target_chat}")
            
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem Telegram: {e}")

    def send_startup_notification(self):
        """Envia notificação de início do sistema para o canal"""
        try:
            from datetime import datetime
            
            startup_message = (
                "🚀 TENNISQ PRÉ-LIVE INICIADO\n\n"
                f"⏰ Hora: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC\n"
                "🔍 Monitoramento ativo para oportunidades pré-live\n"
                "⏱️ Ciclo de escaneamento: 1 hora\n"
                "� Notificação: QUALQUER horário (sem filtro de tempo)\n"
                "🎾 Lógica AGRESSIVA: EV 3-25%, Odds 1.70-3.00\n"
                "🌐 Dados reais via B365API (sport_id=13)\n"
                "📊 Paginação ativa para superar limite de 50 jogos\n\n"
                "💡 Sistema operacional e pronto para detectar oportunidades!"
            )
            
            self._send_telegram_message(startup_message)
            logger.info("Notificação de início enviada para o canal Telegram")
            
        except Exception as e:
            logger.error(f"Erro ao enviar notificação de início: {e}")
    
    def _sleep_with_interrupt(self, seconds: int):
        """Dorme por X segundos, mas pode ser interrompido"""
        end_time = time.time() + seconds
        while time.time() < end_time and self.running:
            time.sleep(min(10, end_time - time.time()))
    
    def _sleep_with_heartbeat(self, seconds: int, message_prefix: str):
        """Dorme por X segundos com logs de heartbeat regulares"""
        start_time = time.time()
        end_time = start_time + seconds
        
        # Log a cada 30 minutos durante sleeps longos
        heartbeat_interval = min(1800, seconds // 4)  # 30 min ou 1/4 do tempo total
        last_heartbeat = start_time
        
        while time.time() < end_time and self.running:
            current_time = time.time()
            
            # Log de heartbeat
            if current_time - last_heartbeat >= heartbeat_interval:
                remaining = int(end_time - current_time)
                hours = remaining // 3600
                minutes = (remaining % 3600) // 60
                
                if hours > 0:
                    time_str = f"{hours}h {minutes}m"
                else:
                    time_str = f"{minutes}m"
                    
                logger.info(f"💓 {message_prefix} {time_str}")
                last_heartbeat = current_time
            
            # Sleep em chunks pequenos para permitir interrupção
            time.sleep(min(10, end_time - current_time))
    
    def get_service_status(self) -> Dict:
        """Retorna status do serviço"""
        return {
            "running": self.running,
            "scan_thread_alive": self.scan_thread.is_alive() if self.scan_thread else False,
            "monitor_thread_alive": self.monitor_thread.is_alive() if self.monitor_thread else False,
            "database_stats": self.db.get_statistics()
        }
    
    def force_scan(self) -> List:
        """Força um escaneamento imediato"""
        logger.info("Executando escaneamento forçado...")
        
        opportunities = self.scanner.scan_opportunities(
            hours_ahead=72,
            min_ev=0.01,
            odd_min=1.60,
            odd_max=2.50
        )
        
        if opportunities:
            self.db.save_opportunities(opportunities)
            
        return opportunities
    
    def cleanup_expired_opportunities(self):
        """Limpa oportunidades expiradas"""
        logger.info("Limpando oportunidades expiradas...")
        
        # Marca como expiradas as oportunidades de jogos que já começaram
        active_opps = self.db.get_active_opportunities(min_hours_ahead=-1)
        now = datetime.utcnow()
        
        for opp in active_opps:
            start_time = datetime.fromisoformat(opp["start_utc"].replace('Z', '+00:00'))
            if start_time <= now:
                self.db.mark_opportunity_expired(opp["event_id"])
        
        # Remove dados antigos
        self.db.cleanup_old_data(days_old=7)
        
        logger.info("Limpeza concluída")

class PreLiveManager:
    """Classe principal para gerenciar o sistema pré-live"""
    
    def __init__(self, config_path: str = "../config/config.json"):
        self.monitoring_service = LineMonitoringService(config_path)
        self.db = PreLiveDatabase()
    
    def start(self):
        """Inicia todo o sistema"""
        logger.info("🚀 PreLiveManager: Iniciando sistema TennisQ Pré-Live...")
        
        # Envia notificação de início para o canal
        logger.info("📱 PreLiveManager: Enviando notificação de startup...")
        self.monitoring_service.send_startup_notification()
        
        # Inicia o serviço de monitoramento
        logger.info("🔄 PreLiveManager: Iniciando serviço de monitoramento...")
        self.monitoring_service.start_service()
        
        logger.info("✅ PreLiveManager: Sistema totalmente iniciado!")
    
    def stop(self):
        """Para todo o sistema"""
        logger.info("⏹️ PreLiveManager: Parando sistema TennisQ Pré-Live...")
        self.monitoring_service.stop_service()
        logger.info("✅ PreLiveManager: Sistema parado!")
    
    def get_dashboard_data(self) -> Dict:
        """Retorna dados para o dashboard"""
        return {
            "service_status": self.monitoring_service.get_service_status(),
            "active_opportunities": self.db.get_active_opportunities()[:20],
            "statistics": self.db.get_statistics()
        }
    
    def manual_scan(self) -> List:
        """Executa escaneamento manual"""
        return self.monitoring_service.force_scan()

def main():
    """Função principal para executar o serviço"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    manager = PreLiveManager()
    
    try:
        manager.start()
        
        # Mantém o serviço rodando
        while True:
            time.sleep(60)
            
    except KeyboardInterrupt:
        logger.info("Interrompido pelo usuário")
    finally:
        manager.stop()

if __name__ == "__main__":
    main()
