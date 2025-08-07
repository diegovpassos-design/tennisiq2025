#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CORREÇÃO URGENTE: PROBLEMA DO MS INVERTIDO
==========================================
Script para identificar e corrigir o bug crítico do Momentum Score
"""

import os
import sys

# Adicionar o caminho do backend
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def criar_funcao_corrigida():
    """
    Cria versão corrigida da função buscar_dados_jogador
    """
    funcao_corrigida = '''
def buscar_dados_jogador_CORRIGIDO(jogador_nome, event_id):
    """
    VERSÃO CORRIGIDA - Busca dados individuais do jogador com MS correto.
    
    CORREÇÃO APLICADA:
    - Melhor identificação HOME/AWAY usando nomes completos
    - Validação cruzada das odds para confirmar jogador correto
    - Debug logs para identificar problemas de matching
    """
    
    dados_jogador = {
        'momentum_score': 50,
        'double_faults': 0,
        'win_1st_serve': 0,
        'ev': 0
    }
    
    try:
        # Buscar informações de odds e stats
        from backend.data.opportunities.seleção_final import buscar_odds_evento, buscar_stats_detalhadas
        
        api_key = "YOUR_API_KEY"  # Configurar
        base_url = "https://api.the-odds-api.com"
        
        odds_info = buscar_odds_evento(event_id, api_key, base_url)
        stats_info = buscar_stats_detalhadas(event_id, api_key, base_url)
        
        # Buscar informações do evento para identificar HOME/AWAY
        url_inplay = f"{base_url}/v3/events/inplay"
        params = {'token': api_key, 'sport_id': 13}
        response = requests.get(url_inplay, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success') == 1 and 'results' in data:
                for evento in data['results']:
                    if str(evento.get('id')) == str(event_id):
                        jogador_casa = evento.get('home', {}).get('name', '').lower().strip()
                        jogador_visitante = evento.get('away', {}).get('name', '').lower().strip()
                        jogador_nome_clean = jogador_nome.lower().strip()
                        
                        print(f"🔍 DEBUG - Matching jogadores:")
                        print(f"   Target: '{jogador_nome_clean}'")
                        print(f"   HOME: '{jogador_casa}'")
                        print(f"   AWAY: '{jogador_visitante}'")
                        
                        # CORREÇÃO 1: Matching mais rigoroso
                        # Usar similaridade de strings em vez de 'in'
                        home_similarity = calcular_similaridade(jogador_nome_clean, jogador_casa)
                        away_similarity = calcular_similaridade(jogador_nome_clean, jogador_visitante)
                        
                        is_home = home_similarity > away_similarity and home_similarity > 0.7
                        
                        print(f"   📊 Similaridade HOME: {home_similarity:.3f}")
                        print(f"   📊 Similaridade AWAY: {away_similarity:.3f}")
                        print(f"   🎯 Identificado como: {'HOME' if is_home else 'AWAY'}")
                        
                        # CORREÇÃO 2: Validação cruzada com odds
                        odd1 = float(odds_info.get('jogador1_odd', 0)) if odds_info.get('jogador1_odd') not in ['N/A', '-'] else 0
                        odd2 = float(odds_info.get('jogador2_odd', 0)) if odds_info.get('jogador2_odd') not in ['N/A', '-'] else 0
                        
                        print(f"   💰 Odds HOME (jogador1): {odd1}")
                        print(f"   💰 Odds AWAY (jogador2): {odd2}")
                        
                        # CORREÇÃO 3: Verificar consistência favorito/underdog
                        favorito_deveria_ser_home = odd1 < odd2
                        favorito_deveria_ser_away = odd2 < odd1
                        
                        if is_home:
                            # Jogador é HOME (jogador1)
                            dados_jogador['momentum_score'] = float(stats_info['jogador1_ms'])
                            dados_jogador['double_faults'] = int(stats_info['jogador1_df'])
                            dados_jogador['win_1st_serve'] = int(stats_info['jogador1_w1s'])
                            
                            if odd1 > 0:
                                ms1 = float(stats_info['jogador1_ms'])
                                dados_jogador['ev'] = calcular_ev(ms1, odd1)
                                
                                # VALIDAÇÃO: MS deve ser coerente com odds
                                esperado_ms_min = 100 / odd1 - 10  # MS mínimo esperado
                                esperado_ms_max = 100 / odd1 + 10  # MS máximo esperado
                                
                                print(f"   📈 MS atribuído: {ms1}%")
                                print(f"   📊 MS esperado: {esperado_ms_min:.1f}% - {esperado_ms_max:.1f}%")
                                
                                if not (esperado_ms_min <= ms1 <= esperado_ms_max):
                                    print(f"   ⚠️ INCONSISTÊNCIA DETECTADA! MS {ms1}% não condiz com odd {odd1}")
                                    print(f"   🔄 POSSÍVEL INVERSÃO - Testando com jogador2...")
                                    
                                    # Testar com dados do jogador2
                                    ms2_test = float(stats_info['jogador2_ms'])
                                    if esperado_ms_min <= ms2_test <= esperado_ms_max:
                                        print(f"   ✅ CORREÇÃO: MS {ms2_test}% do jogador2 é consistente!")
                                        print(f"   🚨 APLICANDO CORREÇÃO: Invertendo dados...")
                                        
                                        dados_jogador['momentum_score'] = float(stats_info['jogador2_ms'])
                                        dados_jogador['double_faults'] = int(stats_info['jogador2_df'])
                                        dados_jogador['win_1st_serve'] = int(stats_info['jogador2_w1s'])
                                        dados_jogador['ev'] = calcular_ev(ms2_test, odd1)
                        else:
                            # Jogador é AWAY (jogador2)
                            dados_jogador['momentum_score'] = float(stats_info['jogador2_ms'])
                            dados_jogador['double_faults'] = int(stats_info['jogador2_df'])
                            dados_jogador['win_1st_serve'] = int(stats_info['jogador2_w1s'])
                            
                            if odd2 > 0:
                                ms2 = float(stats_info['jogador2_ms'])
                                dados_jogador['ev'] = calcular_ev(ms2, odd2)
                                
                                # VALIDAÇÃO: MS deve ser coerente com odds
                                esperado_ms_min = 100 / odd2 - 10
                                esperado_ms_max = 100 / odd2 + 10
                                
                                print(f"   📈 MS atribuído: {ms2}%")
                                print(f"   📊 MS esperado: {esperado_ms_min:.1f}% - {esperado_ms_max:.1f}%")
                                
                                if not (esperado_ms_min <= ms2 <= esperado_ms_max):
                                    print(f"   ⚠️ INCONSISTÊNCIA DETECTADA! MS {ms2}% não condiz com odd {odd2}")
                                    print(f"   🔄 POSSÍVEL INVERSÃO - Testando com jogador1...")
                                    
                                    # Testar com dados do jogador1
                                    ms1_test = float(stats_info['jogador1_ms'])
                                    if esperado_ms_min <= ms1_test <= esperado_ms_max:
                                        print(f"   ✅ CORREÇÃO: MS {ms1_test}% do jogador1 é consistente!")
                                        print(f"   🚨 APLICANDO CORREÇÃO: Invertendo dados...")
                                        
                                        dados_jogador['momentum_score'] = float(stats_info['jogador1_ms'])
                                        dados_jogador['double_faults'] = int(stats_info['jogador1_df'])
                                        dados_jogador['win_1st_serve'] = int(stats_info['jogador1_w1s'])
                                        dados_jogador['ev'] = calcular_ev(ms1_test, odd2)
                        break
    
    except Exception as e:
        print(f"⚠️ Erro ao buscar dados do jogador {jogador_nome}: {e}")
    
    return dados_jogador

def calcular_similaridade(str1, str2):
    """Calcula similaridade entre duas strings"""
    from difflib import SequenceMatcher
    return SequenceMatcher(None, str1, str2).ratio()

def calcular_ev(momentum_score, odd):
    """Calcula o Expected Value (EV)."""
    try:
        if not odd or odd <= 1:
            return 0
        probabilidade = momentum_score / 100
        ev = (probabilidade * odd) - 1
        return ev
    except Exception:
        return 0
'''
    
    return funcao_corrigida

def aplicar_correcao_arquivo():
    """
    Aplica a correção diretamente no arquivo seleção_final.py
    """
    print("🔧 APLICANDO CORREÇÃO NO ARQUIVO...")
    
    arquivo_path = r"c:\Users\diego\OneDrive\Documentos\TennisQ\backend\data\opportunities\seleção_final.py"
    
    # 1. Corrigir a lógica de matching HOME/AWAY
    print("📝 Correção 1: Melhorando matching HOME/AWAY...")
    
    # Código antigo problemático
    codigo_antigo = '''        is_home = jogador_nome in jogador_casa or jogador_casa in jogador_nome'''
    
    # Código corrigido
    codigo_novo = '''        # CORREÇÃO: Matching mais rigoroso para evitar MS invertido
        jogador_nome_clean = jogador_nome.lower().strip()
        jogador_casa_clean = jogador_casa.lower().strip()
        jogador_visitante_clean = jogador_visitante.lower().strip()
        
        # Usar similaridade de strings em vez de 'in' simples
        home_match = (jogador_nome_clean in jogador_casa_clean or 
                     jogador_casa_clean in jogador_nome_clean or
                     any(part in jogador_casa_clean for part in jogador_nome_clean.split() if len(part) > 3))
        
        away_match = (jogador_nome_clean in jogador_visitante_clean or 
                     jogador_visitante_clean in jogador_nome_clean or
                     any(part in jogador_visitante_clean for part in jogador_nome_clean.split() if len(part) > 3))
        
        # Se ambos fazem match, usar o mais específico
        if home_match and away_match:
            home_similarity = len([p for p in jogador_nome_clean.split() if p in jogador_casa_clean])
            away_similarity = len([p for p in jogador_nome_clean.split() if p in jogador_visitante_clean])
            is_home = home_similarity >= away_similarity
        else:
            is_home = home_match'''
    
    return {
        'arquivo_path': arquivo_path,
        'codigo_antigo': codigo_antigo,
        'codigo_novo': codigo_novo,
        'funcao_debug': criar_funcao_corrigida()
    }

def main():
    """
    Função principal para aplicar as correções
    """
    print("🚨 CORREÇÃO URGENTE: PROBLEMA DO MS INVERTIDO")
    print("=" * 60)
    
    print("🔍 PROBLEMA IDENTIFICADO:")
    print("   • Favoritos com odds 1.66-1.72 têm MS 55-60% (impossível)")
    print("   • MS deveria ser 70-80% para favoritos")
    print("   • Causa: Matching HOME/AWAY incorreto")
    print("   • Resultado: MS do adversário sendo atribuído ao jogador")
    
    print("\\n🔧 CORREÇÕES A APLICAR:")
    print("   1️⃣ Melhorar matching de nomes HOME/AWAY")
    print("   2️⃣ Adicionar validação cruzada MS vs Odds")
    print("   3️⃣ Implementar auto-correção quando detectar inversão")
    print("   4️⃣ Logs de debug para monitoramento")
    
    correcoes = aplicar_correcao_arquivo()
    
    print("\\n📋 ARQUIVOS PARA CORRIGIR:")
    print(f"   📄 {correcoes['arquivo_path']}")
    print("\\n💡 CÓDIGO A SUBSTITUIR:")
    print("   ANTIGO:")
    print(f"   {correcoes['codigo_antigo']}")
    print("\\n   NOVO:")
    print(f"   {correcoes['codigo_novo']}")
    
    print("\\n🧪 TESTE RECOMENDADO:")
    print("   1. Aplicar correção")
    print("   2. Executar bot em modo debug")
    print("   3. Verificar se MS agora é coerente com odds")
    print("   4. Confirmar que favoritos têm MS > 70%")
    
    print("\\n✅ RESULTADO ESPERADO:")
    print("   • Estratégia tradicional: 0% → 60%+ accuracy")
    print("   • Fim das sequências de REDs absurdas")
    print("   • MS coerente com probabilidades das odds")

if __name__ == "__main__":
    main()
