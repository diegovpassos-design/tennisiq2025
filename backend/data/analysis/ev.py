#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Calculadora de EV (Expected Value) para Apostas de Tênis
========================================================

Este módulo calcula o EV (Valor Esperado) de cada jogador baseado nas odds
e no momentum score obtidos das partidas ao vivo.

Fórmula: EV = (Probabilidade estimada × Odd) - 1
Onde: probabilidade_estimada = momentum_score / 100

Interpretação:
- EV > 0: aposta tem valor esperado positivo → pode ser lucrativa
- EV < 0: aposta é desfavorável → evitar

Autor: Sistema TennisQ
Data: 2025-08-03
"""

import json
import requests
import time
from datetime import datetime
from typing import Dict, List, Tuple, Optional


def calcular_ev(odd: float, momentum_score: float) -> float:
    """
    Calcula o EV (Expected Value) com base na odd e no momentum_score.
    
    Args:
        odd (float): Odd da aposta (ex: 2.50)
        momentum_score (float): Valor entre 0 e 100 (ex: 68)

    Returns:
        float: EV calculado
    """
    probabilidade_estimada = momentum_score / 100
    ev = (probabilidade_estimada * odd) - 1
    return round(ev, 4)


def interpretar_ev(ev: float) -> str:
    """
    Interpreta o valor do EV e retorna uma recomendação.
    
    Args:
        ev (float): Valor do EV calculado
        
    Returns:
        str: Interpretação do EV
    """
    if ev > 0.2:
        return "🟢 EXCELENTE"
    elif ev > 0.1:
        return "🔵 BOM"
    elif ev > 0:
        return "🟡 MARGINAL"
    elif ev > -0.1:
        return "🟠 RUIM"
    else:
        return "🔴 PÉSSIMO"


def buscar_odds_evento(event_id, api_key, base_url):
    """Busca as odds de um evento específico."""
    url = f"{base_url}/v3/event/odds"
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
            
            if 'odds' in results and results['odds']:
                odds_data = results['odds']
                
                if '13_1' in odds_data and odds_data['13_1']:
                    latest_odds = odds_data['13_1'][0]
                    
                    if 'home_od' in latest_odds and 'away_od' in latest_odds:
                        return {
                            'jogador1_odd': latest_odds.get('home_od', 'N/A'),
                            'jogador2_odd': latest_odds.get('away_od', 'N/A')
                        }
        
        return {'jogador1_odd': 'N/A', 'jogador2_odd': 'N/A'}
        
    except:
        return {'jogador1_odd': 'N/A', 'jogador2_odd': 'N/A'}


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
                
                return {
                    'jogador1_ms': jogador1_ms,
                    'jogador2_ms': jogador2_ms,
                    'stats_detalhadas': stats
                }
        
        return {
            'jogador1_ms': 50,
            'jogador2_ms': 50,
            'stats_detalhadas': {}
        }
        
    except Exception as e:
        return {
            'jogador1_ms': 50,
            'jogador2_ms': 50,
            'stats_detalhadas': {}
        }


def buscar_partidas_ao_vivo():
    """Busca partidas ao vivo diretamente da API."""
    
    try:
        with open('../../config/config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
    except:
        print("❌ Erro ao carregar configurações")
        return []
    
    api_key = config.get('api_key')
    base_url = config.get('api_base_url', 'https://api.b365api.com')
    
    if not api_key:
        print("❌ API key não encontrada")
        return []
    
    url = f"{base_url}/v3/events/inplay"
    params = {
        'token': api_key,
        'sport_id': 13
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success') == 1 and 'results' in data:
                return data['results']
        return []
    except:
        return []


def calcular_ev_todas_partidas():
    """Calcula o EV para todas as partidas ao vivo."""
    
    print("🎾 CALCULADORA DE EV (EXPECTED VALUE) - TÊNIS")
    print("=" * 60)
    
    # Buscar eventos ao vivo
    eventos_ao_vivo = buscar_partidas_ao_vivo()
    
    if not eventos_ao_vivo:
        print("❌ Nenhuma partida ao vivo encontrada")
        return
    
    # Carregar configurações
    try:
        with open('../../config/config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        api_key = config.get('api_key')
        base_url = config.get('api_base_url', 'https://api.b365api.com')
    except:
        print("❌ Erro ao carregar config")
        return
    
    print(f"🔴 Total de partidas encontradas: {len(eventos_ao_vivo)}")
    print(f"📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("")
    print("💡 Legenda:")
    print("   🟢 EXCELENTE (EV > 0.2)  🔵 BOM (EV > 0.1)  🟡 MARGINAL (EV > 0)")
    print("   🟠 RUIM (EV > -0.1)      🔴 PÉSSIMO (EV ≤ -0.1)")
    print("")
    print("=" * 80)
    
    apostas_com_valor = []
    
    # Processar cada partida
    for i, evento in enumerate(eventos_ao_vivo, 1):
        evento_id = evento.get('id', 'N/A')
        liga = evento.get('league', {}).get('name', 'Liga não informada')
        jogador_casa = evento.get('home', {}).get('name', 'Jogador 1')
        jogador_visitante = evento.get('away', {}).get('name', 'Jogador 2')
        
        # Hora de início
        timestamp = evento.get('time', 0)
        try:
            if timestamp and int(timestamp) > 0:
                hora_inicio = datetime.fromtimestamp(int(timestamp)).strftime('%H:%M')
            else:
                hora_inicio = 'N/A'
        except:
            hora_inicio = 'N/A'
        
        print(f"🏆 PARTIDA {i}")
        print(f"   ID: {evento_id}")
        print(f"   🏟️  Liga: {liga}")
        print(f"   👤 {jogador_casa} vs {jogador_visitante}")
        print(f"   🕐 Hora: {hora_inicio}")
        
        # Buscar dados se possível
        if api_key and base_url and evento_id != 'N/A':
            print(f"   🔄 Calculando EV...")
            
            # Buscar odds
            odds_info = buscar_odds_evento(evento_id, api_key, base_url)
            time.sleep(0.3)
            
            # Buscar momentum
            stats_info = buscar_stats_detalhadas(evento_id, api_key, base_url)
            time.sleep(0.3)
            
            # Calcular EV para cada jogador
            try:
                # Jogador 1
                if odds_info['jogador1_odd'] != 'N/A' and odds_info['jogador1_odd'] != '-':
                    odd1 = float(odds_info['jogador1_odd'])
                    ms1 = stats_info['jogador1_ms']
                    ev1 = calcular_ev(odd1, ms1)
                    interpretacao1 = interpretar_ev(ev1)
                    
                    print(f"   💰 {jogador_casa}: Odd {odd1} | MS {ms1} | EV {ev1:+.4f} {interpretacao1}")
                    
                    if ev1 > 0:
                        apostas_com_valor.append({
                            'partida': f"{jogador_casa} vs {jogador_visitante}",
                            'jogador': jogador_casa,
                            'odd': odd1,
                            'ms': ms1,
                            'ev': ev1,
                            'interpretacao': interpretacao1
                        })
                else:
                    ms1 = stats_info['jogador1_ms']
                    print(f"   💰 {jogador_casa}: Sem odd | MS {ms1}")
                
                # Jogador 2
                if odds_info['jogador2_odd'] != 'N/A' and odds_info['jogador2_odd'] != '-':
                    odd2 = float(odds_info['jogador2_odd'])
                    ms2 = stats_info['jogador2_ms']
                    ev2 = calcular_ev(odd2, ms2)
                    interpretacao2 = interpretar_ev(ev2)
                    
                    print(f"   💰 {jogador_visitante}: Odd {odd2} | MS {ms2} | EV {ev2:+.4f} {interpretacao2}")
                    
                    if ev2 > 0:
                        apostas_com_valor.append({
                            'partida': f"{jogador_casa} vs {jogador_visitante}",
                            'jogador': jogador_visitante,
                            'odd': odd2,
                            'ms': ms2,
                            'ev': ev2,
                            'interpretacao': interpretacao2
                        })
                else:
                    ms2 = stats_info['jogador2_ms']
                    print(f"   💰 {jogador_visitante}: Sem odd | MS {ms2}")
                    
            except Exception as e:
                print(f"   ❌ Erro no cálculo: {e}")
        
        print("-" * 60)
        
        # Rate limiting
        if i % 5 == 0:
            time.sleep(1)
    
    # Resumo das melhores apostas
    print("\n" + "=" * 80)
    print("🎯 RESUMO DAS MELHORES OPORTUNIDADES (EV > 0)")
    print("=" * 80)
    
    if apostas_com_valor:
        # Ordenar por EV decrescente
        apostas_com_valor.sort(key=lambda x: x['ev'], reverse=True)
        
        for i, aposta in enumerate(apostas_com_valor[:10], 1):  # Top 10
            print(f"{i:2d}. {aposta['interpretacao']} {aposta['jogador']}")
            print(f"    📊 Partida: {aposta['partida']}")
            print(f"    💰 Odd: {aposta['odd']} | MS: {aposta['ms']} | EV: {aposta['ev']:+.4f}")
            print()
        
        print(f"✅ Total de oportunidades encontradas: {len(apostas_com_valor)}")
    else:
        print("❌ Nenhuma aposta com EV positivo encontrada no momento")
    
    print(f"\n📊 Análise concluída: {len(eventos_ao_vivo)} partidas processadas")


if __name__ == "__main__":
    calcular_ev_todas_partidas()
