#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exibição de Partidas de Tênis ao Vivo
====================================

Este módulo exibe no terminal as partidas de tênis ao vivo extraídas da API.
Mostra: número de partidas, data, hora de início e jogadores.
"""

import json
import requests
import time
from datetime import datetime


def buscar_stats_detalhadas(event_id, api_key, base_url):
    """Busca estatísticas detalhadas usando /v3/event/view."""
    url = f"{base_url}/v3/event/view"
    params = {
        'event_id': event_id,
        'token': api_key
    }
    
    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        if data.get('success') == 1 and 'results' in data:
            results = data['results']
            if results and len(results) > 0:
                event_data = results[0]
                
                # Extrair estatísticas
                stats = event_data.get('stats', {})
                
                # Calcular momentum score baseado em estatísticas reais
                jogador1_ms = 50
                jogador2_ms = 50
                
                if stats:
                    momentum_factors = []
                    
                    # Aces (peso: 10)
                    if 'aces' in stats and len(stats['aces']) >= 2:
                        try:
                            aces1 = int(stats['aces'][0])
                            aces2 = int(stats['aces'][1])
                            if aces1 + aces2 > 0:
                                momentum_factors.append((aces1, aces2, 10))
                        except:
                            pass
                    
                    # Win 1st serve % (peso: 15)
                    if 'win_1st_serve' in stats and len(stats['win_1st_serve']) >= 2:
                        try:
                            serve1 = int(stats['win_1st_serve'][0])
                            serve2 = int(stats['win_1st_serve'][1])
                            momentum_factors.append((serve1, serve2, 15))
                        except:
                            pass
                    
                    # Break point conversions % (peso: 20)
                    if 'break_point_conversions' in stats and len(stats['break_point_conversions']) >= 2:
                        try:
                            bp1 = int(stats['break_point_conversions'][0])
                            bp2 = int(stats['break_point_conversions'][1])
                            momentum_factors.append((bp1, bp2, 20))
                        except:
                            pass
                    
                    # Calcular momentum ponderado
                    if momentum_factors:
                        total_weighted_score1 = 0
                        total_weighted_score2 = 0
                        total_weight = 0
                        
                        for stat1, stat2, weight in momentum_factors:
                            total_weighted_score1 += stat1 * weight
                            total_weighted_score2 += stat2 * weight
                            total_weight += weight
                        
                        if total_weight > 0:
                            total_score = total_weighted_score1 + total_weighted_score2
                            if total_score > 0:
                                jogador1_ms = round((total_weighted_score1 / total_score) * 100)
                                jogador2_ms = 100 - jogador1_ms
                
                # Extrair double faults
                df1 = 0
                df2 = 0
                if 'double_faults' in stats and len(stats['double_faults']) >= 2:
                    try:
                        df1 = int(stats['double_faults'][0])
                        df2 = int(stats['double_faults'][1])
                    except:
                        pass
                
                # Extrair win 1st serve %
                w1s1 = 0
                w1s2 = 0
                if 'win_1st_serve' in stats and len(stats['win_1st_serve']) >= 2:
                    try:
                        w1s1 = int(stats['win_1st_serve'][0])
                        w1s2 = int(stats['win_1st_serve'][1])
                    except:
                        pass
                
                return {
                    'jogador1_ms': str(jogador1_ms),
                    'jogador2_ms': str(jogador2_ms),
                    'jogador1_df': str(df1),
                    'jogador2_df': str(df2),
                    'jogador1_w1s': str(w1s1),
                    'jogador2_w1s': str(w1s2),
                    'stats_detalhadas': stats
                }
        
        return {
            'jogador1_ms': '50',
            'jogador2_ms': '50',
            'jogador1_df': '0',
            'jogador2_df': '0',
            'jogador1_w1s': '0',
            'jogador2_w1s': '0',
            'stats_detalhadas': {}
        }
        
    except Exception as e:
        return {
            'jogador1_ms': '50',
            'jogador2_ms': '50',
            'jogador1_df': '0',
            'jogador2_df': '0',
            'jogador1_w1s': '0',
            'jogador2_w1s': '0',
            'stats_detalhadas': {}
        }


def calcular_momentum_score(evento):
    """Calcula o momentum score baseado no estado atual da partida."""
    try:
        # Obter score atual
        score_str = evento.get('ss', '')
        if not score_str:
            return {'jogador1_ms': '50', 'jogador2_ms': '50'}
        
        # Parsing do score - exemplo: "6-3,0-0" ou "6-7,4-4" ou "1-5"
        sets_info = score_str.split(' ') if ' ' in score_str else [score_str]
        
        jogador1_score = 0
        jogador2_score = 0
        
        # Analisar cada set/game
        for set_info in sets_info:
            if '-' in set_info:
                if ',' in set_info:
                    # Formato: "6-7,4-4" (set finalizado, game atual)
                    set_part, game_part = set_info.split(',')
                    
                    # Analisar set finalizado (peso alto)
                    if '-' in set_part:
                        try:
                            s1, s2 = map(int, set_part.split('-'))
                            jogador1_score += s1 * 10
                            jogador2_score += s2 * 10
                        except:
                            pass
                    
                    # Analisar game atual (peso médio)
                    if '-' in game_part:
                        try:
                            g1, g2 = map(int, game_part.split('-'))
                            jogador1_score += g1 * 5
                            jogador2_score += g2 * 5
                        except:
                            # Pontos dentro do game
                            g1, g2 = game_part.split('-')
                            points_map = {'0': 0, '15': 1, '30': 2, '40': 3, 'A': 4, 'AD': 4}
                            p1 = points_map.get(g1, 0)
                            p2 = points_map.get(g2, 0)
                            jogador1_score += p1
                            jogador2_score += p2
                
                else:
                    # Formato simples: "1-5" 
                    try:
                        s1, s2 = map(int, set_info.split('-'))
                        jogador1_score += s1 * 5
                        jogador2_score += s2 * 5
                    except:
                        pass
        
        # Calcular momentum de forma mais equilibrada
        total_score = jogador1_score + jogador2_score
        if total_score > 0:
            # Proporção base
            prop1 = jogador1_score / total_score
            prop2 = jogador2_score / total_score
            
            # Aplicar suavização para evitar extremos 100-0
            # Misturar com 50-50 para dar mais equilíbrio
            balance_factor = 0.3  # 30% de equilíbrio
            ms1 = round((prop1 * (1 - balance_factor) + 0.5 * balance_factor) * 100)
            ms2 = round((prop2 * (1 - balance_factor) + 0.5 * balance_factor) * 100)
            
            # Garantir que soma 100
            if ms1 + ms2 != 100:
                ms2 = 100 - ms1
                
            # Limitar extremos
            ms1 = max(10, min(90, ms1))
            ms2 = max(10, min(90, ms2))
            
            # Reajustar para somar 100
            total = ms1 + ms2
            ms1 = round((ms1 / total) * 100)
            ms2 = 100 - ms1
            
        else:
            ms1 = ms2 = 50
        
        return {'jogador1_ms': str(ms1), 'jogador2_ms': str(ms2)}
        
    except Exception as e:
        return {'jogador1_ms': '50', 'jogador2_ms': '50'}


def buscar_odds_evento(event_id, api_key, base_url):
    """Busca as odds de um evento específico."""
    url = f"{base_url}/v3/event/odds"  # Usar v3 que funciona melhor
    params = {
        'event_id': event_id,
        'token': api_key
    }
    
    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        if data.get('success') == 1 and 'results' in data:
            results = data['results']
            
            # Verificar se há odds disponíveis no formato v3
            if 'odds' in results and results['odds']:
                odds_data = results['odds']
                
                # Procurar pelo mercado 13_1 (Match Winner)
                if '13_1' in odds_data and odds_data['13_1']:
                    # Pegar a odd mais recente (primeira da lista)
                    latest_odds = odds_data['13_1'][0]
                    
                    if 'home_od' in latest_odds and 'away_od' in latest_odds:
                        return {
                            'jogador1_odd': latest_odds.get('home_od', 'N/A'),
                            'jogador2_odd': latest_odds.get('away_od', 'N/A')
                        }
        
        return {'jogador1_odd': 'N/A', 'jogador2_odd': 'N/A'}
        
    except:
        return {'jogador1_odd': 'N/A', 'jogador2_odd': 'N/A'}


def buscar_partidas_ao_vivo():
    """Busca partidas ao vivo diretamente da API."""
    
    # Carregar configurações
    try:
        with open('../../config/config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
    except:
        print("❌ Erro ao carregar configurações do arquivo config/config.json")
        return []
    
    # Configurações da API
    api_key = config.get('api_key')
    base_url = config.get('api_base_url', 'https://api.b365api.com')
    
    if not api_key:
        print("❌ API key não encontrada no arquivo de configuração")
        return []
    
    # Fazer requisição para eventos ao vivo
    url = f"{base_url}/v3/events/inplay"
    params = {
        'sport_id': 13,  # Tênis
        'token': api_key
    }
    
    try:
        print("🔄 Consultando API...")
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('success') and 'results' in data:
            return data['results']
        else:
            print(f"❌ Erro da API: {data.get('error', 'Resposta inválida')}")
            return []
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"❌ Erro ao decodificar resposta: {e}")
        return []


def exibir_partidas_ao_vivo():
    """Exibe as partidas de tênis ao vivo no terminal."""
    
    print("🎾 BUSCANDO PARTIDAS AO VIVO...")
    print("=" * 50)
    
    # Buscar eventos ao vivo
    eventos_ao_vivo = buscar_partidas_ao_vivo()
    
    if not eventos_ao_vivo:
        print("❌ Nenhuma partida ao vivo encontrada no momento.")
        return
    
    # Carregar configurações para buscar odds
    try:
        with open('../../config/config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        api_key = config.get('api_key')
        base_url = config.get('api_base_url', 'https://api.b365api.com')
    except:
        api_key = None
        base_url = None
    
    # Exibir informações
    print(f"🔴 PARTIDAS AO VIVO ENCONTRADAS: {len(eventos_ao_vivo)}")
    print(f"📅 Data da consulta: {datetime.now().strftime('%d/%m/%Y')}")
    print(f"🕐 Hora da consulta: {datetime.now().strftime('%H:%M:%S')}")
    print("")
    print("=" * 80)
    
    for i, evento in enumerate(eventos_ao_vivo, 1):
        # Extrair informações básicas
        evento_id = evento.get('id', 'N/A')
        liga = evento.get('league', {}).get('name', 'Liga não informada')
        
        # Jogadores
        jogador_casa = evento.get('home', {}).get('name', 'Jogador 1')
        jogador_visitante = evento.get('away', {}).get('name', 'Jogador 2')
        
        # Hora de início (se disponível)
        timestamp = evento.get('time', 0)
        try:
            if timestamp and int(timestamp) > 0:
                hora_inicio = datetime.fromtimestamp(int(timestamp)).strftime('%H:%M')
            else:
                hora_inicio = 'N/A'
        except (ValueError, TypeError):
            hora_inicio = 'N/A'
        
        # Buscar odds e estatísticas se possível
        odds_info = {'jogador1_odd': 'N/A', 'jogador2_odd': 'N/A'}
        momentum_info = {'jogador1_ms': '50', 'jogador2_ms': '50', 'jogador1_df': '0', 'jogador2_df': '0', 'jogador1_w1s': '0', 'jogador2_w1s': '0'}
        
        if api_key and base_url and evento_id != 'N/A':
            print(f"🔄 Buscando dados da partida {i}...")
            
            # Buscar odds
            odds_info = buscar_odds_evento(evento_id, api_key, base_url)
            time.sleep(0.3)
            
            # Buscar estatísticas detalhadas para momentum
            stats_info = buscar_stats_detalhadas(evento_id, api_key, base_url)
            momentum_info['jogador1_ms'] = stats_info['jogador1_ms']
            momentum_info['jogador2_ms'] = stats_info['jogador2_ms']
            momentum_info['jogador1_df'] = stats_info['jogador1_df']
            momentum_info['jogador2_df'] = stats_info['jogador2_df']
            momentum_info['jogador1_w1s'] = stats_info['jogador1_w1s']
            momentum_info['jogador2_w1s'] = stats_info['jogador2_w1s']
            time.sleep(0.3)
        
        # Exibir informações da partida
        print(f"🏆 PARTIDA {i}")
        print(f"   ID: {evento_id}")
        print(f"   🏟️  Liga/Torneio: {liga}")
        print(f"   👤 Jogador 1: {jogador_casa} - Odd: {odds_info['jogador1_odd']} - MS: {momentum_info['jogador1_ms']} - DF: {momentum_info['jogador1_df']} - W1S: {momentum_info['jogador1_w1s']}%")
        print(f"   👤 Jogador 2: {jogador_visitante} - Odd: {odds_info['jogador2_odd']} - MS: {momentum_info['jogador2_ms']} - DF: {momentum_info['jogador2_df']} - W1S: {momentum_info['jogador2_w1s']}%")
        print(f"   🕐 Hora de início: {hora_inicio}")
        print("-" * 50)
    
    print(f"\n✅ Total de {len(eventos_ao_vivo)} partidas ao vivo exibidas!")


def obter_status_partida(time_status):
    """Converte o status numérico em texto legível."""
    status_map = {
        0: "Aguardando início",
        1: "1º Set em andamento",
        2: "2º Set em andamento", 
        3: "3º Set em andamento",
        4: "4º Set em andamento",
        5: "5º Set em andamento",
        6: "Entre sets",
        99: "Partida finalizada"
    }
    return status_map.get(time_status, f"Status desconhecido ({time_status})")


if __name__ == "__main__":
    exibir_partidas_ao_vivo()
