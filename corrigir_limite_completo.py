#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 CORREÇÃO COMPLETA: RATE LIMITING + INSTÂNCIAS
============================================================
Implementa todas as correções necessárias para resolver 
o problema dos 53 req/ciclo e rate limiting
"""

import json
import os
import time
from pathlib import Path

def atualizar_rate_limiter():
    """Atualiza rate_limiter.py com limites corretos"""
    print("🔧 Atualizando rate_limiter.py...")
    
    rate_limiter_path = "backend/utils/rate_limiter.py"
    
    with open(rate_limiter_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Atualizar max_requests_per_minute de 30 para 80
    content = content.replace(
        'max_requests_per_minute=30',
        'max_requests_per_minute=80'
    )
    
    # Adicionar rate limiting por segundo
    if 'max_requests_per_second' not in content:
        # Inserir após max_requests_per_minute
        content = content.replace(
            'max_requests_per_minute=80,',
            'max_requests_per_minute=80,\n        max_requests_per_second=5,'
        )
    
    with open(rate_limiter_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Rate limiter atualizado!")

def criar_detector_instancias():
    """Cria script para detectar múltiplas instâncias"""
    print("🔍 Criando detector de instâncias...")
    
    detector_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 DETECTOR DE MÚLTIPLAS INSTÂNCIAS
============================================================
Detecta se há múltiplas instâncias do bot rodando
"""

import os
import time
import json
import psutil
from datetime import datetime

class DetectorInstancias:
    def __init__(self):
        self.instance_file = "storage/database/instance_check.json"
        self.my_pid = os.getpid()
        
    def detectar_instancias(self):
        """Detecta se há múltiplas instâncias rodando"""
        print(f"🔍 === DETECTOR DE INSTÂNCIAS (PID: {self.my_pid}) ===")
        
        # Verificar processos Python rodando bot
        bot_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['name'] == 'python.exe' or proc.info['name'] == 'python':
                    cmdline = ' '.join(proc.info['cmdline'] or [])
                    if 'run_bot.py' in cmdline or 'bot.py' in cmdline:
                        bot_processes.append({
                            'pid': proc.info['pid'],
                            'cmdline': cmdline,
                            'create_time': proc.create_time()
                        })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        print(f"📊 Processos bot encontrados: {len(bot_processes)}")
        for proc in bot_processes:
            create_time = datetime.fromtimestamp(proc['create_time'])
            print(f"  • PID {proc['pid']}: {create_time} - {proc['cmdline'][:80]}...")
        
        # Registrar esta instância
        self.registrar_instancia()
        
        # Verificar arquivo de instâncias
        self.verificar_arquivo_instancias()
        
        return len(bot_processes)
    
    def registrar_instancia(self):
        """Registra esta instância no arquivo de controle"""
        os.makedirs(os.path.dirname(self.instance_file), exist_ok=True)
        
        instance_data = {
            'pid': self.my_pid,
            'timestamp': datetime.now().isoformat(),
            'railway_replica': os.environ.get('RAILWAY_REPLICA_ID', 'unknown'),
            'railway_service': os.environ.get('RAILWAY_SERVICE_NAME', 'unknown')
        }
        
        # Ler instâncias existentes
        instances = []
        if os.path.exists(self.instance_file):
            try:
                with open(self.instance_file, 'r') as f:
                    instances = json.load(f)
            except:
                instances = []
        
        # Adicionar esta instância
        instances.append(instance_data)
        
        # Manter apenas últimas 10 instâncias
        instances = instances[-10:]
        
        with open(self.instance_file, 'w') as f:
            json.dump(instances, f, indent=2)
        
        print(f"📝 Instância registrada: PID {self.my_pid}")
    
    def verificar_arquivo_instancias(self):
        """Verifica instâncias registradas no arquivo"""
        if not os.path.exists(self.instance_file):
            return
        
        with open(self.instance_file, 'r') as f:
            instances = json.load(f)
        
        print(f"📋 Instâncias registradas: {len(instances)}")
        for inst in instances[-5:]:  # Últimas 5
            print(f"  • PID {inst['pid']}: {inst['timestamp']} (Replica: {inst['railway_replica']})")

def main():
    """Função principal"""
    detector = DetectorInstancias()
    num_processes = detector.detectar_instancias()
    
    print(f"\\n🎯 RESULTADO:")
    if num_processes > 1:
        print(f"🚨 PROBLEMA: {num_processes} instâncias detectadas!")
        print("💡 SOLUÇÕES:")
        print("   1. Verificar Railway dashboard - quantas replicas?")
        print("   2. Usar 'railway ps' para ver processos ativos")
        print("   3. Ajustar rate limiting para múltiplas instâncias")
    else:
        print(f"✅ OK: Apenas 1 instância detectada")
    
    return num_processes

if __name__ == "__main__":
    main()
'''
    
    with open("detector_instancias.py", 'w', encoding='utf-8') as f:
        f.write(detector_content)
    
    print("✅ Detector criado!")

def criar_rate_limiter_avancado():
    """Cria rate limiter com controle de rajadas"""
    print("🚀 Criando rate limiter avançado...")
    
    limiter_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 RATE LIMITER AVANÇADO
============================================================
Rate limiter com controle de rajadas e múltiplas instâncias
"""

import time
import asyncio
from collections import deque
from datetime import datetime, timedelta

class RateLimiterAvancado:
    def __init__(self, 
                 max_requests_per_hour=3600,
                 max_requests_per_minute=80, 
                 max_requests_per_second=5,
                 burst_delay=0.2):
        """
        Rate limiter com controle de rajadas
        
        Args:
            max_requests_per_hour: Limite por hora
            max_requests_per_minute: Limite por minuto 
            max_requests_per_second: Limite por segundo
            burst_delay: Delay entre requisições em rajadas (segundos)
        """
        self.max_requests_per_hour = max_requests_per_hour
        self.max_requests_per_minute = max_requests_per_minute
        self.max_requests_per_second = max_requests_per_second
        self.burst_delay = burst_delay
        
        # Tracking de requests
        self.requests_hour = deque()
        self.requests_minute = deque()
        self.requests_second = deque()
        
        self.last_request_time = 0
        
    def can_make_request(self):
        """Verifica se pode fazer uma requisição"""
        now = time.time()
        
        # Limpar requests antigos
        self._clean_old_requests(now)
        
        # Verificar limites
        if len(self.requests_hour) >= self.max_requests_per_hour:
            return False, f"Limite por hora excedido: {len(self.requests_hour)}/{self.max_requests_per_hour}"
            
        if len(self.requests_minute) >= self.max_requests_per_minute:
            return False, f"Limite por minuto excedido: {len(self.requests_minute)}/{self.max_requests_per_minute}"
            
        if len(self.requests_second) >= self.max_requests_per_second:
            return False, f"Limite por segundo excedido: {len(self.requests_second)}/{self.max_requests_per_second}"
        
        # Verificar delay entre requests
        time_since_last = now - self.last_request_time
        if time_since_last < self.burst_delay:
            return False, f"Delay necessário: {self.burst_delay - time_since_last:.2f}s"
        
        return True, "OK"
    
    def make_request(self):
        """Registra uma requisição feita"""
        now = time.time()
        
        self.requests_hour.append(now)
        self.requests_minute.append(now)
        self.requests_second.append(now)
        self.last_request_time = now
        
        # Log de monitoramento
        self._log_request_stats()
    
    def wait_if_needed(self):
        """Espera se necessário antes de fazer request"""
        can_request, reason = self.can_make_request()
        
        if not can_request:
            if "Delay necessário" in reason:
                delay = float(reason.split(": ")[1].replace("s", ""))
                print(f"⏳ Aguardando {delay:.2f}s para evitar rate limit...")
                time.sleep(delay)
            else:
                print(f"🚨 Rate limit ativo: {reason}")
                return False
        
        return True
    
    async def async_wait_if_needed(self):
        """Versão async de wait_if_needed"""
        can_request, reason = self.can_make_request()
        
        if not can_request:
            if "Delay necessário" in reason:
                delay = float(reason.split(": ")[1].replace("s", ""))
                print(f"⏳ Aguardando {delay:.2f}s para evitar rate limit...")
                await asyncio.sleep(delay)
            else:
                print(f"🚨 Rate limit ativo: {reason}")
                return False
        
        return True
    
    def _clean_old_requests(self, now):
        """Remove requests antigos dos contadores"""
        # Hora (3600s)
        while self.requests_hour and now - self.requests_hour[0] > 3600:
            self.requests_hour.popleft()
            
        # Minuto (60s)
        while self.requests_minute and now - self.requests_minute[0] > 60:
            self.requests_minute.popleft()
            
        # Segundo (1s)
        while self.requests_second and now - self.requests_second[0] > 1:
            self.requests_second.popleft()
    
    def _log_request_stats(self):
        """Log das estatísticas de requests"""
        print(f"📊 Rate Stats: {len(self.requests_hour)}/3600h | "
              f"{len(self.requests_minute)}/80min | "
              f"{len(self.requests_second)}/5s")
    
    def get_stats(self):
        """Retorna estatísticas atuais"""
        now = time.time()
        self._clean_old_requests(now)
        
        return {
            'requests_hour': len(self.requests_hour),
            'requests_minute': len(self.requests_minute),
            'requests_second': len(self.requests_second),
            'limits': {
                'hour': self.max_requests_per_hour,
                'minute': self.max_requests_per_minute,
                'second': self.max_requests_per_second
            }
        }

# Instância global
rate_limiter = RateLimiterAvancado()
'''
    
    with open("backend/utils/rate_limiter_avancado.py", 'w', encoding='utf-8') as f:
        f.write(limiter_content)
    
    print("✅ Rate limiter avançado criado!")

def criar_verificador_railway():
    """Cria script para verificar configuração Railway"""
    print("🚂 Criando verificador Railway...")
    
    railway_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚂 VERIFICADOR RAILWAY
============================================================
Verifica configuração e instâncias no Railway
"""

import os
import json
import subprocess
from datetime import datetime

class VerificadorRailway:
    def __init__(self):
        self.railway_vars = self._get_railway_vars()
    
    def _get_railway_vars(self):
        """Coleta variáveis do Railway"""
        vars_of_interest = [
            'RAILWAY_REPLICA_ID',
            'RAILWAY_SERVICE_NAME', 
            'RAILWAY_SERVICE_ID',
            'RAILWAY_ENVIRONMENT_NAME',
            'RAILWAY_PROJECT_NAME',
            'RAILWAY_DEPLOYMENT_ID',
            'PORT'
        ]
        
        railway_vars = {}
        for var in vars_of_interest:
            railway_vars[var] = os.environ.get(var, 'not_set')
        
        return railway_vars
    
    def verificar_configuracao(self):
        """Verifica configuração atual do Railway"""
        print("🚂 === VERIFICADOR RAILWAY ===")
        print(f"📅 Verificação: {datetime.now()}")
        
        print("\\n🔧 VARIÁVEIS RAILWAY:")
        for var, value in self.railway_vars.items():
            print(f"  • {var}: {value}")
        
        # Verificar se está rodando no Railway
        is_railway = self.railway_vars['RAILWAY_SERVICE_NAME'] != 'not_set'
        print(f"\\n🚂 Rodando no Railway: {'✅ SIM' if is_railway else '❌ NÃO'}")
        
        if is_railway:
            self.verificar_replicas()
            self.verificar_recursos()
    
    def verificar_replicas(self):
        """Verifica número de replicas"""
        print("\\n📊 VERIFICAÇÃO DE REPLICAS:")
        
        replica_id = self.railway_vars['RAILWAY_REPLICA_ID']
        if replica_id != 'not_set':
            print(f"  • ID desta replica: {replica_id}")
            
            # Tentar detectar outras replicas pelo arquivo de controle
            self._verificar_arquivo_replicas()
        else:
            print("  • Replica ID não definido")
    
    def _verificar_arquivo_replicas(self):
        """Verifica arquivo de controle de replicas"""
        replica_file = "storage/database/replica_check.json"
        
        # Registrar esta replica
        replica_data = {
            'replica_id': self.railway_vars['RAILWAY_REPLICA_ID'],
            'service_name': self.railway_vars['RAILWAY_SERVICE_NAME'],
            'timestamp': datetime.now().isoformat(),
            'pid': os.getpid()
        }
        
        # Ler replicas existentes
        replicas = []
        if os.path.exists(replica_file):
            try:
                with open(replica_file, 'r') as f:
                    replicas = json.load(f)
            except:
                replicas = []
        
        # Adicionar esta replica
        replicas.append(replica_data)
        
        # Manter apenas últimas 10
        replicas = replicas[-10:]
        
        os.makedirs(os.path.dirname(replica_file), exist_ok=True)
        with open(replica_file, 'w') as f:
            json.dump(replicas, f, indent=2)
        
        print(f"  • Replicas registradas: {len(replicas)}")
        for replica in replicas[-3:]:  # Últimas 3
            print(f"    - {replica['replica_id']}: {replica['timestamp']}")
    
    def verificar_recursos(self):
        """Verifica uso de recursos"""
        print("\\n💾 VERIFICAÇÃO DE RECURSOS:")
        
        try:
            import psutil
            
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            print(f"  • CPU: {cpu_percent}%")
            
            # Memória
            memory = psutil.virtual_memory()
            memory_mb = memory.used / 1024 / 1024
            print(f"  • Memória: {memory_mb:.1f}MB ({memory.percent}%)")
            
            # Processos Python
            python_processes = 0
            for proc in psutil.process_iter(['name']):
                try:
                    if 'python' in proc.info['name'].lower():
                        python_processes += 1
                except:
                    continue
            
            print(f"  • Processos Python: {python_processes}")
            
        except ImportError:
            print("  • psutil não disponível para verificar recursos")
    
    def gerar_comandos_debug(self):
        """Gera comandos para debug manual"""
        print("\\n🛠️ COMANDOS PARA DEBUG MANUAL:")
        print("  No Railway CLI:")
        print("    railway ps                    # Ver processos ativos")
        print("    railway status               # Status do serviço")
        print("    railway logs -f              # Logs em tempo real")
        print("    railway variables            # Ver variáveis")
        print("\\n  No Dashboard Railway:")
        print("    Settings > Replicas         # Verificar quantidade")
        print("    Metrics > Memory/CPU        # Uso de recursos")
        print("    Deployments                 # Histórico deployments")

def main():
    """Função principal"""
    verificador = VerificadorRailway()
    verificador.verificar_configuracao()
    verificador.gerar_comandos_debug()

if __name__ == "__main__":
    main()
'''
    
    with open("verificar_railway.py", 'w', encoding='utf-8') as f:
        f.write(railway_content)
    
    print("✅ Verificador Railway criado!")

def main():
    """Função principal de correção"""
    print("🔧 === CORREÇÃO COMPLETA DO RATE LIMITING ===")
    print(f"📅 Iniciando correção: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 1. Atualizar rate limiter
        atualizar_rate_limiter()
        
        # 2. Criar detector de instâncias
        criar_detector_instancias()
        
        # 3. Criar rate limiter avançado
        criar_rate_limiter_avancado()
        
        # 4. Criar verificador Railway
        criar_verificador_railway()
        
        print("\n✅ === CORREÇÃO COMPLETA! ===")
        print("\n🎯 PRÓXIMOS PASSOS:")
        print("1. python detector_instancias.py      # Verificar instâncias")
        print("2. python verificar_railway.py         # Verificar Railway")
        print("3. Deploy com limites corrigidos")
        print("4. Monitorar logs para confirmar 26 req/ciclo")
        
        print("\n📋 ARQUIVOS CRIADOS/ATUALIZADOS:")
        print("  • backend/utils/rate_limiter.py     (limites corrigidos)")
        print("  • detector_instancias.py            (detectar múltiplas instâncias)")
        print("  • backend/utils/rate_limiter_avancado.py  (rate limiter com burst control)")
        print("  • verificar_railway.py              (verificar configuração Railway)")
        
    except Exception as e:
        print(f"❌ Erro na correção: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    main()
