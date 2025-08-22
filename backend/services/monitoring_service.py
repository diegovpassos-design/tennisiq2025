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
    def __init__(self, config_path: str = "../config/config.json"):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.scanner = PreLiveScanner(
            api_token=self.config["api_key"],
            api_base=self.config["api_base_url"]
        )
        
        self.db = PreLiveDatabase()
        self.running = False
        self.scan_thread = None
        self.monitor_thread = None
        
    def start_service(self):
        """Inicia o serviço de monitoramento"""
        if self.running:
            logger.warning("Serviço já está rodando")
            return
            
        self.running = True
        
        # Thread para escanear novas oportunidades
        self.scan_thread = threading.Thread(target=self._scan_loop, daemon=True)
        self.scan_thread.start()
        
        # Thread para monitorar movimento de linha
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        logger.info("Serviço de monitoramento iniciado")
    
    def stop_service(self):
        """Para o serviço de monitoramento"""
        self.running = False
        logger.info("Serviço de monitoramento parado")
    
    def _scan_loop(self):
        """Loop principal para escanear novas oportunidades"""
        while self.running:
            try:
                logger.info("Iniciando escaneamento de novas oportunidades...")
                
                # Limpeza de oportunidades enviadas expiradas
                self.db.cleanup_expired_sent_opportunities()
                
                # Escaneia oportunidades
                opportunities = self.scanner.scan_opportunities(
                    hours_ahead=72,
                    min_ev=0.005,  # EV mínimo de 0.5% (mais sensível)
                    odd_min=1.80,  # Range ajustado conforme solicitado
                    odd_max=2.40   # Range ajustado conforme solicitado
                )
                
                if opportunities:
                    # Salva no banco
                    saved_count = self.db.save_opportunities(opportunities)
                    logger.info(f"Salvas {saved_count} novas oportunidades")
                    
                    # Envia notificação de TODAS as oportunidades
                    self._notify_best_opportunities(opportunities)
                
                # Aguarda 3 horas antes do próximo scan completo
                self._sleep_with_interrupt(3 * 3600)  # 3 horas
                
            except Exception as e:
                logger.error(f"Erro no loop de escaneamento: {e}")
                self._sleep_with_interrupt(300)  # 5 minutos em caso de erro
    
    def _monitor_loop(self):
        """Loop para monitorar movimento de linha das oportunidades ativas"""
        while self.running:
            try:
                logger.info("Monitorando movimento de linha...")
                
                # Busca oportunidades ativas
                active_opps = self.db.get_active_opportunities(min_hours_ahead=0.5)
                
                events_to_monitor = set()
                for opp in active_opps:
                    events_to_monitor.add(opp["event_id"])
                
                # Monitora cada evento
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
                        
                        # Pausa pequena entre requests
                        time.sleep(1)
                        
                    except Exception as e:
                        logger.warning(f"Erro ao monitorar evento {event_id}: {e}")
                
                logger.info(f"Monitoramento concluído para {len(events_to_monitor)} eventos")
                
                # Aguarda 30 minutos antes do próximo monitoramento
                self._sleep_with_interrupt(30 * 60)  # 30 minutos
                
            except Exception as e:
                logger.error(f"Erro no loop de monitoramento: {e}")
                self._sleep_with_interrupt(300)  # 5 minutos em caso de erro
    
    def _notify_best_opportunities(self, opportunities: List):
        """Envia notificação das melhores oportunidades via Telegram - cada jogo separadamente"""
        if not opportunities:
            return
        
        # Filtra oportunidades que já foram enviadas
        new_opportunities = []
        for opp in opportunities:
            if not self.db.is_opportunity_already_sent(opp):
                new_opportunities.append(opp)
            else:
                logger.info(f"Oportunidade já enviada: {opp.match} - {opp.side}")
        
        if not new_opportunities:
            logger.info("Todas as oportunidades já foram enviadas anteriormente")
            return
            
        try:
            # Envia cada oportunidade como mensagem separada
            for i, opp in enumerate(new_opportunities, 1):
                ev_percent = opp.ev * 100
                
                # Determina qual jogador apostar baseado no lado
                home_player, away_player = opp.match.split(' vs ')
                target_player = home_player if opp.side == "HOME" else away_player
                
                # Extrai data e hora do start_utc
                from datetime import datetime
                start_dt = datetime.fromisoformat(opp.start_utc.replace('Z', '+00:00'))
                date_str = start_dt.strftime('%d/%m')
                time_str = start_dt.strftime('%H:%M')
                
                # Cria mensagem individual com formato completo
                message = f"🎾 OPORTUNIDADE {i}\n\n"
                message += f"🏆 {opp.league}\n"
                message += f"⚔️ {opp.match}\n"
                message += f"🎯 **{target_player}** @ {opp.odd}\n"
                message += f"📊 EV: **{ev_percent:.1f}%**\n"
                message += f"📅 {date_str} às {time_str}"
                
                # Envia cada mensagem separadamente
                self._send_telegram_message(message)
                
                # Marca como enviada para evitar duplicatas
                self.db.mark_opportunity_as_sent(opp)
                
                # Pequena pausa entre mensagens para não spammar
                import time
                time.sleep(1)
                
            # Mensagem final de resumo
            summary_message = f"💡 **{len(new_opportunities)} oportunidades** enviadas!"
            self._send_telegram_message(summary_message)
            
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
                "⏱️ Ciclo de escaneamento: 3 horas\n"
                "🎾 Análise de TODOS os jogos de tênis\n"
                "🌐 Dados reais via B365API (sport_id=13)\n\n"
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
        logger.info("Iniciando sistema TennisQ Pré-Live...")
        
        # Envia notificação de início para o canal
        self.monitoring_service.send_startup_notification()
        
        # Inicia o serviço de monitoramento
        self.monitoring_service.start_service()
    
    def stop(self):
        """Para todo o sistema"""
        logger.info("Parando sistema TennisQ Pré-Live...")
        self.monitoring_service.stop_service()
    
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
