#!/usr/bin/env python3
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
        
        print("\n🔧 VARIÁVEIS RAILWAY:")
        for var, value in self.railway_vars.items():
            print(f"  • {var}: {value}")
        
        # Verificar se está rodando no Railway
        is_railway = self.railway_vars['RAILWAY_SERVICE_NAME'] != 'not_set'
        print(f"\n🚂 Rodando no Railway: {'✅ SIM' if is_railway else '❌ NÃO'}")
        
        if is_railway:
            self.verificar_replicas()
            self.verificar_recursos()
    
    def verificar_replicas(self):
        """Verifica número de replicas"""
        print("\n📊 VERIFICAÇÃO DE REPLICAS:")
        
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
        print("\n💾 VERIFICAÇÃO DE RECURSOS:")
        
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
        print("\n🛠️ COMANDOS PARA DEBUG MANUAL:")
        print("  No Railway CLI:")
        print("    railway ps                    # Ver processos ativos")
        print("    railway status               # Status do serviço")
        print("    railway logs -f              # Logs em tempo real")
        print("    railway variables            # Ver variáveis")
        print("\n  No Dashboard Railway:")
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
