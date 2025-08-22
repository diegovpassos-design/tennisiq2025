import sys
import os
sys.path.append('backend')

import json
import logging
from flask import Flask, request
import threading
import time

logger = logging.getLogger(__name__)

class TelegramBotHandler:
    """Handler para processar callbacks do bot Telegram"""
    
    def __init__(self, config):
        self.config = config
        self.app = Flask(__name__)
        self.setup_routes()
    
    def setup_routes(self):
        """Configura as rotas do webhook"""
        
        @self.app.route('/webhook', methods=['POST'])
        def webhook():
            """Processa updates do Telegram"""
            try:
                update = request.get_json()
                
                if 'callback_query' in update:
                    self.handle_callback_query(update['callback_query'])
                
                return 'OK', 200
                
            except Exception as e:
                logger.error(f"Erro no webhook: {e}")
                return 'Error', 500
    
    def handle_callback_query(self, callback_query):
        """Processa clique nos botões inline"""
        try:
            callback_data = callback_query['data']
            chat_id = callback_query['message']['chat']['id']
            message_id = callback_query['message']['message_id']
            user = callback_query['from']
            
            logger.info(f"Callback recebido: {callback_data} do usuário {user.get('username', 'Unknown')}")
            
            if callback_data.startswith('copy_'):
                # Extrai informações do callback
                parts = callback_data.split('_', 2)
                if len(parts) >= 3:
                    opp_number = parts[1]
                    player_name = parts[2]
                    
                    # Responde ao callback com o nome do jogador
                    self.answer_callback_query(
                        callback_query['id'],
                        f"✅ {player_name}\n\nNome copiado! Cole na casa de apostas.",
                        show_alert=True
                    )
                    
                    # Envia feedback na conversa
                    self.send_quick_feedback(chat_id, f"✅ **{player_name}** copiado!")
            
        except Exception as e:
            logger.error(f"Erro ao processar callback: {e}")
    
    def send_quick_feedback(self, chat_id, text):
        """Envia feedback rápido que desaparece"""
        try:
            import requests
            
            url = f"https://api.telegram.org/bot{self.config['telegram_token']}/sendMessage"
            
            data = {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "Markdown"
            }
            
            response = requests.post(url, data=data, timeout=5)
            response.raise_for_status()
            
        except Exception as e:
            logger.error(f"Erro ao enviar feedback rápido: {e}")
    
    def answer_callback_query(self, callback_query_id, text, show_alert=False):
        """Responde ao callback query"""
        try:
            import requests
            
            url = f"https://api.telegram.org/bot{self.config['telegram_token']}/answerCallbackQuery"
            
            data = {
                "callback_query_id": callback_query_id,
                "text": text,
                "show_alert": show_alert
            }
            
            response = requests.post(url, data=data, timeout=5)
            response.raise_for_status()
            
        except Exception as e:
            logger.error(f"Erro ao responder callback: {e}")
    
    def add_click_feedback(self, chat_id, message_id, opp_number, player_name, user_name):
        """Adiciona feedback visual de que o botão foi clicado"""
        try:
            import requests
            
            # Cria mensagem de feedback
            feedback_text = f"✅ **{user_name}** copiou: **{player_name}** (Oportunidade #{opp_number})"
            
            url = f"https://api.telegram.org/bot{self.config['telegram_token']}/sendMessage"
            
            data = {
                "chat_id": chat_id,
                "text": feedback_text,
                "parse_mode": "Markdown",
                "reply_to_message_id": message_id
            }
            
            response = requests.post(url, data=data, timeout=5)
            response.raise_for_status()
            
        except Exception as e:
            logger.error(f"Erro ao enviar feedback: {e}")
    
    def setup_webhook(self, webhook_url):
        """Configura o webhook do Telegram"""
        try:
            import requests
            
            url = f"https://api.telegram.org/bot{self.config['telegram_token']}/setWebhook"
            
            data = {
                "url": webhook_url,
                "allowed_updates": ["callback_query"]
            }
            
            response = requests.post(url, data=data, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            if result.get('ok'):
                logger.info(f"Webhook configurado: {webhook_url}")
                return True
            else:
                logger.error(f"Erro ao configurar webhook: {result}")
                return False
            
        except Exception as e:
            logger.error(f"Erro ao configurar webhook: {e}")
            return False
    
    def run_server(self, host='0.0.0.0', port=8080):
        """Inicia o servidor Flask"""
        logger.info(f"Iniciando servidor webhook em {host}:{port}")
        self.app.run(host=host, port=port, debug=False)

# Função para integrar com o sistema existente
def start_telegram_bot_handler():
    """Inicia o handler do bot Telegram"""
    try:
        with open('backend/config/config.json', 'r') as f:
            config = json.load(f)
        
        bot_handler = TelegramBotHandler(config)
        
        # Em produção, configurar webhook com URL real
        # webhook_url = "https://seu-app.railway.app/webhook"
        # bot_handler.setup_webhook(webhook_url)
        
        # Para desenvolvimento local, usar polling ou ngrok
        logger.info("Handler do Telegram Bot criado")
        return bot_handler
        
    except Exception as e:
        logger.error(f"Erro ao iniciar bot handler: {e}")
        return None

if __name__ == "__main__":
    # Teste do sistema
    logging.basicConfig(level=logging.INFO)
    
    handler = start_telegram_bot_handler()
    if handler:
        print("Bot handler criado com sucesso!")
        print("Para testar localmente, use ngrok ou configure webhook em produção")
    else:
        print("Erro ao criar bot handler")
