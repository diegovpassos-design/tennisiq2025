#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXTRATOR DE ESTATÍSTICAS DOS JOGADORES
====================================
Função para extrair estatísticas completas dos jogadores de uma partida
"""

import requests
import json
import os

# Configurar caminhos para nova estrutura
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

def carregar_config():
    """Carrega configurações da API"""
    try:
        config_path = os.path.join(PROJECT_ROOT, 'backend', 'config', 'config.json')
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            return config['api_key'], config['api_base_url']
    except Exception as e:
        print(f"[ERROR] Erro ao carregar configurações: {e}")
        return None, None

def extrair_stats_completas(event_id, api_key=None, base_url=None):
    """
    Extrai estatísticas completas dos dois jogadores de uma partida
    
    Returns:
        dict: {
            'stats_jogador1': {...},
            'stats_jogador2': {...}
        }
    """
    # Se não fornecidas, carregar da config
    if not api_key or not base_url:
        api_key, base_url = carregar_config()
        
    if not api_key or not base_url:
        print("[ERROR] Configurações da API não encontradas")
        return {
            'stats_jogador1': {},
            'stats_jogador2': {}
        }
    
    url = f"{base_url}/v3/event/view"
    params = {
        'event_id': event_id,
        'token': api_key
    }
    
    stats_vazias = {
        'aces': 0,
        'double_faults': 0,
        'first_serve_percentage': 0,
        'win_first_serve': 0,
        'win_second_serve': 0,
        'break_points_saved': 0,
        'total_points_won': 0,
        'winners': 0,
        'unforced_errors': 0,
        'break_points_converted': 0,
        'service_games_won': 0,
        'return_games_won': 0
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get('success') == 1 and 'results' in data:
            results = data['results']
            if results and len(results) > 0:
                event_data = results[0]
                stats = event_data.get('stats', {})
                
                if not stats:
                    print("[INFO] Nenhuma estatística encontrada para este evento")
                    return {
                        'stats_jogador1': stats_vazias.copy(),
                        'stats_jogador2': stats_vazias.copy()
                    }
                
                # Inicializar stats dos jogadores
                stats_j1 = stats_vazias.copy()
                stats_j2 = stats_vazias.copy()
                
                # Extrair cada estatística disponível
                estatisticas_map = {
                    'aces': 'aces',
                    'double_faults': 'double_faults',
                    'first_serve_percentage': 'first_serve_percentage',
                    'win_1st_serve': 'win_first_serve',
                    'win_2nd_serve': 'win_second_serve',
                    'break_point_saved': 'break_points_saved',
                    'total_points_won': 'total_points_won',
                    'winners': 'winners',
                    'unforced_errors': 'unforced_errors',
                    'break_point_conversions': 'break_points_converted',
                    'service_games_won': 'service_games_won',
                    'return_games_won': 'return_games_won'
                }
                
                for api_key_stat, our_key in estatisticas_map.items():
                    if api_key_stat in stats and len(stats[api_key_stat]) >= 2:
                        try:
                            valor1 = stats[api_key_stat][0]
                            valor2 = stats[api_key_stat][1]
                            
                            # Converter para int se possível, senão manter string
                            if isinstance(valor1, str) and valor1.replace('%', '').replace('.', '').isdigit():
                                valor1 = int(float(valor1.replace('%', '')))
                            elif isinstance(valor1, str):
                                valor1 = 0
                            
                            if isinstance(valor2, str) and valor2.replace('%', '').replace('.', '').isdigit():
                                valor2 = int(float(valor2.replace('%', '')))
                            elif isinstance(valor2, str):
                                valor2 = 0
                                
                            stats_j1[our_key] = int(valor1) if str(valor1).isdigit() else 0
                            stats_j2[our_key] = int(valor2) if str(valor2).isdigit() else 0
                            
                        except (ValueError, IndexError, TypeError):
                            stats_j1[our_key] = 0
                            stats_j2[our_key] = 0
                
                return {
                    'stats_jogador1': stats_j1,
                    'stats_jogador2': stats_j2
                }
        
        return {
            'stats_jogador1': stats_vazias.copy(),
            'stats_jogador2': stats_vazias.copy()
        }
        
    except Exception as e:
        print(f"[ERROR] Erro ao extrair stats: {e}")
        return {
            'stats_jogador1': stats_vazias.copy(),
            'stats_jogador2': stats_vazias.copy()
        }

def teste_extrator():
    """Função de teste para verificar se o extrator está funcionando"""
    # Carregar configurações reais
    api_key, base_url = carregar_config()
    
    if not api_key or not base_url:
        print("[ERROR] Configurações não encontradas para teste")
        return
        
    # Event ID de teste - substitua por um real
    EVENT_ID = "123456"
    
    print(f"[INFO] Testando com API: {base_url}")
    print(f"[INFO] Event ID: {EVENT_ID}")
    
    stats = extrair_stats_completas(EVENT_ID)
    print("Resultado do teste:")
    print(json.dumps(stats, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    teste_extrator()
