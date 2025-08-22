#!/usr/bin/env python3
"""
Monitor de Partidas TennisQ - Visualiza partidas sendo monitoradas
"""

import requests
import json
import time
from datetime import datetime
import os

RAILWAY_URL = "https://tennisiq-production.up.railway.app"

def format_time(iso_time):
    """Formata tempo ISO para leitura"""
    if not iso_time:
        return "N/A"
    try:
        if 'T' in iso_time:
            dt = datetime.fromisoformat(iso_time.replace('Z', '+00:00'))
            return dt.strftime("%d/%m %H:%M")
        return iso_time
    except:
        return iso_time

def get_matches():
    """Obtém partidas sendo monitoradas"""
    try:
        response = requests.get(f"{RAILWAY_URL}/api/matches", timeout=15)
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"❌ Erro ao obter partidas: {e}")
        return None

def force_scan():
    """Força um scan manual"""
    try:
        print("🔍 Executando scan manual...")
        response = requests.get(f"{RAILWAY_URL}/api/live-scan", timeout=30)
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"❌ Erro no scan: {e}")
        return None

def print_matches_dashboard():
    """Imprime dashboard das partidas"""
    os.system('cls' if os.name == 'nt' else 'clear')
    
    print("🎾" + "="*70 + "🎾")
    print("              TENNISQ - PARTIDAS MONITORADAS")
    print("🎾" + "="*70 + "🎾")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Buscar partidas
    matches_data = get_matches()
    
    if matches_data:
        print(f"📊 RESUMO:")
        print(f"   📈 Total de partidas: {matches_data.get('total_matches', 0)}")
        print(f"   🎯 Oportunidades ativas: {matches_data.get('active_opportunities', 0)}")
        print()
        
        matches = matches_data.get('matches', [])
        if matches:
            print("🏆 PARTIDAS RECENTES:")
            print("-" * 70)
            
            # Separar por probabilidade
            high_prob = [m for m in matches if m.get('probability', 0) > 0.6]
            medium_prob = [m for m in matches if 0.4 <= m.get('probability', 0) <= 0.6]
            low_prob = [m for m in matches if m.get('probability', 0) < 0.4]
            
            if high_prob:
                print("🔥 ALTA PROBABILIDADE (>60%):")
                for match in high_prob[:5]:
                    prob = match.get('probability', 0) * 100
                    print(f"   🎯 {match.get('home_team', 'N/A')} vs {match.get('away_team', 'N/A')}")
                    print(f"      📊 {prob:.1f}% | 💰 {match.get('current_odds', 'N/A')} | ⏰ {format_time(match.get('start_time'))}")
                    print()
            
            if medium_prob:
                print("⚡ PROBABILIDADE MÉDIA (40-60%):")
                for match in medium_prob[:3]:
                    prob = match.get('probability', 0) * 100
                    print(f"   ⚪ {match.get('home_team', 'N/A')} vs {match.get('away_team', 'N/A')}")
                    print(f"      📊 {prob:.1f}% | ⏰ {format_time(match.get('start_time'))}")
                print()
            
            if not high_prob and not medium_prob and low_prob:
                print("📋 PARTIDAS MONITORADAS:")
                for match in low_prob[:5]:
                    prob = match.get('probability', 0) * 100
                    print(f"   📌 {match.get('home_team', 'N/A')} vs {match.get('away_team', 'N/A')}")
                    print(f"      📊 {prob:.1f}% | ⏰ {format_time(match.get('start_time'))}")
                print()
                
        else:
            print("❌ Nenhuma partida encontrada no histórico")
            print("💡 Tentando scan manual...")
            scan_data = force_scan()
            
            if scan_data and scan_data.get('events'):
                print()
                print("🔍 RESULTADOS DO SCAN MANUAL:")
                print("-" * 70)
                
                events = scan_data.get('events', [])
                opportunities = [e for e in events if e.get('probability', 0) > 0.6]
                
                if opportunities:
                    print("🎯 OPORTUNIDADES ENCONTRADAS:")
                    for event in opportunities:
                        prob = event.get('probability', 0) * 100
                        print(f"   🔥 {event.get('home', 'N/A')} vs {event.get('away', 'N/A')}")
                        print(f"      📊 {prob:.1f}% | ⏰ {format_time(event.get('start_time'))}")
                        print()
                else:
                    print("📋 PARTIDAS ENCONTRADAS NO SCAN:")
                    for event in events[:5]:
                        prob = event.get('probability', 0) * 100
                        print(f"   📌 {event.get('home', 'N/A')} vs {event.get('away', 'N/A')}")
                        print(f"      📊 {prob:.1f}% | ⏰ {format_time(event.get('start_time'))}")
                    print()
            else:
                print("❌ Scan manual não retornou resultados")
    else:
        print("❌ Não foi possível conectar ao sistema")
    
    print("💡 COMANDOS:")
    print("   [Ctrl+C] - Sair")
    print("   [S] - Scan manual")
    print("   [Enter] - Atualizar")
    print()
    print("🔄 Atualizando automaticamente a cada 60 segundos...")
    print("="*72)

def monitor_matches():
    """Loop principal de monitoramento das partidas"""
    try:
        while True:
            print_matches_dashboard()
            
            # Aguardar entrada do usuário ou timeout
            import select
            import sys
            
            if os.name == 'nt':  # Windows
                time.sleep(60)
            else:  # Unix/Linux
                print("Pressione Enter para atualizar ou 's' para scan manual...")
                ready, _, _ = select.select([sys.stdin], [], [], 60)
                if ready:
                    user_input = sys.stdin.readline().strip().lower()
                    if user_input == 's':
                        force_scan()
                        time.sleep(3)
                        
    except KeyboardInterrupt:
        print("\n\n👋 Monitor de partidas finalizado!")
        print("🎾 TennisQ continua rodando no Railway!")

if __name__ == "__main__":
    print("🚀 Iniciando monitor de partidas TennisQ...")
    time.sleep(2)
    monitor_matches()
