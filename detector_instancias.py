#!/usr/bin/env python3
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
    
    print(f"\n🎯 RESULTADO:")
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
