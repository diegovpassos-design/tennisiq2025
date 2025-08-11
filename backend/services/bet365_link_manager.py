"""
Gerenciador de Links da Bet365
==============================
Sistema robusto para capturar e atualizar automaticamente o parâmetro _h da Bet365
"""

import requests
import re
import json
import time
from datetime import datetime
from urllib.parse import urlparse, parse_qs
import os

class Bet365LinkManager:
    def __init__(self, config_path=None):
        self.config_path = config_path or 'config/bet365_config.json'
        self.base_url = "https://www.bet365.bet.br"
        self.current_h_param = None
        self.last_update = None
        self.update_interval = 3600  # 1 hora em segundos
        self.max_retries = 3
        self.timeout = 30
        
        # Headers para simular navegador real
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        self.load_config()
    
    def load_config(self):
        """Carrega configuração salva do parâmetro _h"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.current_h_param = config.get('h_param')
                    self.last_update = config.get('last_update')
                    print(f"📂 Configuração carregada: _h = {self.current_h_param[:20]}..." if self.current_h_param else "📂 Nenhuma configuração encontrada")
            else:
                print("📂 Arquivo de configuração não encontrado, será criado")
        except Exception as e:
            print(f"⚠️ Erro ao carregar configuração: {e}")
    
    def save_config(self):
        """Salva configuração do parâmetro _h"""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            config = {
                'h_param': self.current_h_param,
                'last_update': self.last_update,
                'update_history': getattr(self, 'update_history', [])
            }
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
                print(f"💾 Configuração salva: _h atualizado")
        except Exception as e:
            print(f"❌ Erro ao salvar configuração: {e}")
    
    def test_link(self, test_url=None):
        """Testa se um link da Bet365 está funcionando"""
        if not test_url and not self.current_h_param:
            return False
            
        test_url = test_url or f"{self.base_url}/?_h={self.current_h_param}&btsffd=1#/IP/B13"
        
        try:
            response = requests.get(test_url, headers=self.headers, timeout=self.timeout, allow_redirects=True)
            
            # Verificar se não foi redirecionado para página de erro ou login
            if response.status_code == 200:
                content = response.text.lower()
                # Indicadores de que o link está funcionando
                success_indicators = ['tennis', 'sport', 'bet365', 'odds']
                # Indicadores de erro
                error_indicators = ['error', 'expired', 'invalid', 'not found', 'forbidden']
                
                has_success = any(indicator in content for indicator in success_indicators)
                has_error = any(indicator in content for indicator in error_indicators)
                
                if has_success and not has_error:
                    print(f"✅ Link testado com sucesso: {response.status_code}")
                    return True
                else:
                    print(f"⚠️ Link pode estar com problema - conteúdo suspeito")
                    return False
            else:
                print(f"❌ Link falhou: Status {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao testar link: {e}")
            return False
    
    def extract_h_param_from_page(self):
        """Extrai o parâmetro _h atual da página principal da Bet365"""
        try:
            print("🔍 Buscando parâmetro _h atual na Bet365...")
            
            # Lista de parâmetros _h conhecidos para testar (fallback)
            known_params = [
                "LKUUnzn5idsD_NCCi9iyvQ%3D%3D",
                "goYOEwj4-5qJk-IvCt-TtA%3D%3D",
                "XyZ123abc456def789%3D%3D",  # Placeholder para novos
            ]
            
            # Primeiro, tentar extrair da página
            pages_to_try = [
                f"{self.base_url}",
                f"{self.base_url}/sport/tennis",
                f"{self.base_url}/#/IP/B13"
            ]
            
            for page_url in pages_to_try:
                try:
                    response = requests.get(page_url, headers=self.headers, timeout=self.timeout)
                    
                    if response.status_code == 200:
                        content = response.text
                        
                        # Buscar parâmetro _h em diferentes formatos
                        patterns = [
                            r'_h=([^&"\']+)',
                            r'"_h":"([^"]+)"',
                            r"'_h':'([^']+)'",
                            r'&_h=([^&"\']+)',
                            r'\?_h=([^&"\']+)'
                        ]
                        
                        for pattern in patterns:
                            matches = re.findall(pattern, content)
                            for match in matches:
                                # Validar se parece com um hash válido
                                if len(match) > 10 and ('=' in match or len(match) > 20):
                                    # Testar se este parâmetro funciona
                                    test_url = f"{self.base_url}/?_h={match}&btsffd=1#/IP/B13"
                                    if self.test_link(test_url):
                                        print(f"🎯 Parâmetro _h funcional encontrado: {match[:20]}...")
                                        return match
                        
                        print(f"🔍 Tentando próxima página...")
                    
                except Exception as e:
                    print(f"⚠️ Erro ao acessar {page_url}: {e}")
                    continue
            
            # Se não conseguiu extrair, testar parâmetros conhecidos
            print("🔄 Testando parâmetros conhecidos...")
            for param in known_params:
                test_url = f"{self.base_url}/?_h={param}&btsffd=1#/IP/B13"
                print(f"🧪 Testando: {param[:20]}...")
                if self.test_link(test_url):
                    print(f"✅ Parâmetro conhecido funciona: {param[:20]}...")
                    return param
            
            print("❌ Não foi possível encontrar parâmetro _h funcional")
            return None
            
        except Exception as e:
            print(f"❌ Erro na extração do parâmetro _h: {e}")
            return None
    
    def update_h_param(self, force=False):
        """Atualiza o parâmetro _h se necessário"""
        now = datetime.now()
        
        # Verificar se precisa atualizar
        if not force and self.last_update:
            try:
                last_update_dt = datetime.fromisoformat(self.last_update)
                time_diff = (now - last_update_dt).total_seconds()
                
                if time_diff < self.update_interval:
                    print(f"⏰ Parâmetro _h ainda válido (última atualização: {time_diff/3600:.1f}h atrás)")
                    return self.current_h_param
            except:
                pass
        
        # Testar link atual primeiro
        if self.current_h_param and not force:
            if self.test_link():
                print("✅ Link atual ainda funciona")
                self.last_update = now.isoformat()
                self.save_config()
                return self.current_h_param
        
        print("🔄 Atualizando parâmetro _h...")
        
        # Tentar extrair novo parâmetro
        for attempt in range(self.max_retries):
            new_h_param = self.extract_h_param_from_page()
            
            if new_h_param and new_h_param != self.current_h_param:
                # Testar novo parâmetro
                test_url = f"{self.base_url}/?_h={new_h_param}&btsffd=1#/IP/B13"
                if self.test_link(test_url):
                    print(f"✅ Novo parâmetro _h validado: {new_h_param[:20]}...")
                    
                    # Salvar histórico
                    if not hasattr(self, 'update_history'):
                        self.update_history = []
                    
                    self.update_history.append({
                        'timestamp': now.isoformat(),
                        'old_param': self.current_h_param,
                        'new_param': new_h_param,
                        'reason': 'auto_update' if not force else 'forced_update'
                    })
                    
                    # Manter apenas últimas 10 entradas do histórico
                    self.update_history = self.update_history[-10:]
                    
                    self.current_h_param = new_h_param
                    self.last_update = now.isoformat()
                    self.save_config()
                    
                    return new_h_param
                else:
                    print(f"❌ Novo parâmetro não funcionou na tentativa {attempt + 1}")
            
            time.sleep(2)  # Aguardar antes da próxima tentativa
        
        print("❌ Falha ao atualizar parâmetro _h automaticamente")
        return self.current_h_param
    
    def set_h_param_manual(self, h_param):
        """Define parâmetro _h manualmente"""
        print(f"🔧 Definindo parâmetro _h manualmente: {h_param[:20]}...")
        
        # Testar parâmetro fornecido
        test_url = f"{self.base_url}/?_h={h_param}&btsffd=1#/IP/B13"
        if self.test_link(test_url):
            if not hasattr(self, 'update_history'):
                self.update_history = []
            
            self.update_history.append({
                'timestamp': datetime.now().isoformat(),
                'old_param': self.current_h_param,
                'new_param': h_param,
                'reason': 'manual_update'
            })
            
            self.current_h_param = h_param
            self.last_update = datetime.now().isoformat()
            self.save_config()
            print("✅ Parâmetro _h definido manualmente com sucesso")
            return True
        else:
            print("❌ Parâmetro _h fornecido não está funcionando")
            return False
    
    def generate_link(self, event_id=None):
        """Gera link da Bet365 com parâmetro _h atualizado"""
        # Garantir que temos parâmetro válido
        if not self.current_h_param:
            print("⚠️ Parâmetro _h não encontrado, tentando capturar...")
            self.update_h_param(force=True)
        
        # Verificar se link ainda funciona (teste rápido a cada hora)
        if self.current_h_param:
            now = datetime.now()
            if self.last_update:
                try:
                    last_update_dt = datetime.fromisoformat(self.last_update)
                    time_diff = (now - last_update_dt).total_seconds()
                    
                    # Testar link a cada hora
                    if time_diff > 3600:
                        print("🔄 Verificando validade do link...")
                        if not self.test_link():
                            print("❌ Link expirado, atualizando...")
                            self.update_h_param(force=True)
                except:
                    pass
        
        if not self.current_h_param:
            print("❌ Não foi possível obter parâmetro _h válido")
            return f"{self.base_url}/#/IP/B13"  # Link genérico
        
        # Gerar link específico ou genérico
        if event_id:
            return f"{self.base_url}/?_h={self.current_h_param}&btsffd=1#/IP/EV{event_id}C13"
        else:
            return f"{self.base_url}/?_h={self.current_h_param}&btsffd=1#/IP/B13"
    
    def get_status(self):
        """Retorna status atual do gerenciador"""
        status = {
            'h_param_available': bool(self.current_h_param),
            'last_update': self.last_update,
            'link_working': False
        }
        
        if self.current_h_param:
            status['link_working'] = self.test_link()
            status['h_param_preview'] = f"{self.current_h_param[:20]}..." if len(self.current_h_param) > 20 else self.current_h_param
        
        return status

# Instância global para uso em outros módulos
bet365_manager = Bet365LinkManager()

if __name__ == "__main__":
    # Teste do sistema
    manager = Bet365LinkManager()
    
    print("🧪 Testando Bet365 Link Manager...")
    print("=" * 50)
    
    # Verificar status
    status = manager.get_status()
    print(f"Status atual: {status}")
    
    # Tentar atualizar
    h_param = manager.update_h_param(force=True)
    print(f"Parâmetro obtido: {h_param}")
    
    # Gerar links de teste
    link_generico = manager.generate_link()
    print(f"Link genérico: {link_generico}")
    
    link_especifico = manager.generate_link("12345678")
    print(f"Link específico: {link_especifico}")
