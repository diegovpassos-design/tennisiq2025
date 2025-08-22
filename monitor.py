#!/usr/bin/env python3
"""
Monitor TennisQ - Acompanha o sistema em tempo real
"""

import requests
import time
import json
from datetime import datetime
import os

RAILWAY_URL = "https://tennisiq-production.up.railway.app"

def get_system_stats():
    """Obtém estatísticas do sistema"""
    try:
        response = requests.get(f"{RAILWAY_URL}/api/stats", timeout=10)
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"❌ Erro ao obter stats: {e}")
        return None

def get_system_status():
    """Obtém status completo do sistema"""
    try:
        response = requests.get(f"{RAILWAY_URL}/status", timeout=10)
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"❌ Erro ao obter status: {e}")
        return None

def format_time(iso_time):
    """Formata tempo ISO para leitura"""
    if not iso_time:
        return "N/A"
    try:
        dt = datetime.fromisoformat(iso_time.replace('Z', '+00:00'))
        return dt.strftime("%H:%M:%S")
    except:
        return iso_time[:19] if len(iso_time) > 19 else iso_time

def print_dashboard():
    """Imprime dashboard do sistema"""
    os.system('cls' if os.name == 'nt' else 'clear')
    
    print("🎾" + "="*60 + "🎾")
    print("         TENNISQ V2.0 - MONITOR EM TEMPO REAL")
    print("🎾" + "="*60 + "🎾")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Obter dados
    stats = get_system_stats()
    status = get_system_status()
    
    if stats:
        print("📊 ESTATÍSTICAS:")
        print(f"   🚀 Sistema Ativo: {'✅' if stats.get('monitoring_active') else '❌'}")
        print(f"   ⏰ Iniciado em: {format_time(stats.get('started_at'))}")
        print(f"   🔍 Último Scan: {format_time(stats.get('last_scan'))}")
        print(f"   🎯 Oportunidades: {stats.get('opportunities_found', 0)}")
        print(f"   📱 Notificações: {stats.get('notifications_sent', 0)}")
        print()
    
    if status:
        print("⚙️ STATUS DO SISTEMA:")
        print(f"   🌐 Serviço: {status.get('service', 'N/A')}")
        print(f"   📱 Porta: {status.get('port', 'N/A')}")
        print(f"   🔧 TennisQ: {'✅' if status.get('tennisq_available') else '❌'}")
        print()
        
        env_vars = status.get('environment_vars', {})
        print("🔑 VARIÁVEIS DE AMBIENTE:")
        for var, status_icon in env_vars.items():
            print(f"   {status_icon} {var}")
        print()
    
    print("💡 COMANDOS DISPONÍVEIS:")
    print("   [Ctrl+C] - Sair do monitor")
    print("   [Enter] - Atualizar manualmente")
    print()
    print("🔄 Atualizando a cada 30 segundos...")
    print("="*62)

def monitor_loop():
    """Loop principal de monitoramento"""
    try:
        while True:
            print_dashboard()
            time.sleep(30)
    except KeyboardInterrupt:
        print("\n\n👋 Monitor finalizado!")
        print("🎾 TennisQ continua rodando no Railway!")

if __name__ == "__main__":
    print("🚀 Iniciando monitor TennisQ...")
    time.sleep(2)
    monitor_loop()
