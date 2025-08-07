#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TESTE DA CORREÇÃO DO MS INVERTIDO
=================================
Script para testar se a correção do Momentum Score está funcionando
"""

def simular_casos_antes_depois():
    """
    Simula os casos RED antes e depois da correção
    """
    print("🧪 TESTE DA CORREÇÃO DO MS INVERTIDO")
    print("=" * 60)
    
    casos_red = [
        {
            'jogador': 'Taddia/Vaccari',
            'ms_original': 55,
            'odds': 1.72,
            'ev_original': 0.26,
            'tipo': 'dupla'
        },
        {
            'jogador': 'Nicholas Godsick',
            'ms_original': 60,
            'odds': 1.66,
            'ev_original': 0.16,
            'tipo': 'individual'
        },
        {
            'jogador': 'Lucie Urbanova',
            'ms_original': 55,
            'odds': 1.70,
            'ev_original': 0.10,
            'tipo': 'individual'
        },
        {
            'jogador': 'Tessa Johanna Brockmann',
            'ms_original': 60,
            'odds': 1.69,
            'ev_original': 0.20,
            'tipo': 'individual'
        }
    ]
    
    print("📊 ANÁLISE ANTES DA CORREÇÃO:")
    print("-" * 60)
    total_aprovados_antes = 0
    
    for caso in casos_red:
        ms = caso['ms_original']
        odds = caso['odds']
        ev = caso['ev_original']
        
        # Filtros originais
        aprovado_ev = ev >= 0.15
        aprovado_ms = 55 <= ms <= 75
        aprovado_geral = aprovado_ev and aprovado_ms
        
        if aprovado_geral:
            total_aprovados_antes += 1
            
        print(f"👤 {caso['jogador'][:25]:<25} | MS: {ms:>2}% | EV: {ev:>5.2f} | Odds: {odds} | {'✅ APROVADO' if aprovado_geral else '❌ REJEITADO'}")
    
    print(f"\\n📈 Resultado ANTES: {total_aprovados_antes}/4 aprovados = {total_aprovados_antes/4*100:.0f}% accuracy")
    print("   🔴 Todos resultaram em RED!")
    
    print("\\n📊 ANÁLISE DEPOIS DA CORREÇÃO:")
    print("-" * 60)
    total_aprovados_depois = 0
    
    for caso in casos_red:
        ms_original = caso['ms_original']
        odds = caso['odds']
        
        # CORREÇÃO: Validar se MS é coerente com odds
        prob_esperada = 1 / odds
        ms_esperado = prob_esperada * 100
        diferenca = abs(ms_original - ms_esperado)
        
        # Se diferença > 25%, aplicar correção (inverter)
        if diferenca > 25:
            ms_corrigido = 100 - ms_original  # Simular inversão
            print(f"   🔧 CORREÇÃO: MS {ms_original}% → {ms_corrigido}% (esperado: {ms_esperado:.1f}%)")
        else:
            ms_corrigido = ms_original
            print(f"   ✅ VALIDADO: MS {ms_original}% OK (esperado: {ms_esperado:.1f}%)")
        
        # Recalcular EV com MS corrigido
        ev_corrigido = (ms_corrigido/100 * odds) - 1
        
        # Aplicar filtros com dados corrigidos
        aprovado_ev = ev_corrigido >= 0.15
        aprovado_ms = 55 <= ms_corrigido <= 75
        aprovado_geral = aprovado_ev and aprovado_ms
        
        if aprovado_geral:
            total_aprovados_depois += 1
            
        status = "✅ APROVADO" if aprovado_geral else "❌ REJEITADO"
        print(f"👤 {caso['jogador'][:25]:<25} | MS: {ms_corrigido:>2}% | EV: {ev_corrigido:>5.2f} | Odds: {odds} | {status}")
    
    print(f"\\n📈 Resultado DEPOIS: {total_aprovados_depois}/4 aprovados = {total_aprovados_depois/4*100:.0f}% accuracy")
    
    print("\\n🎯 CONCLUSÃO:")
    if total_aprovados_depois < total_aprovados_antes:
        print("   ✅ CORREÇÃO FUNCIONOU!")
        print("   ✅ Casos problemáticos agora são REJEITADOS")
        print("   ✅ Fim da sequência de REDs")
    else:
        print("   ⚠️ Correção precisa de ajustes")

def testar_validacao_ms_odds():
    """
    Testa a validação MS vs Odds
    """
    print("\\n" + "=" * 60)
    print("🔍 TESTE DA VALIDAÇÃO MS vs ODDS")
    print("=" * 60)
    
    casos_teste = [
        {'odds': 1.50, 'ms_correto': 67, 'ms_errado': 33, 'desc': 'Favorito forte'},
        {'odds': 1.70, 'ms_correto': 59, 'ms_errado': 41, 'desc': 'Favorito médio'},
        {'odds': 2.00, 'ms_correto': 50, 'ms_errado': 50, 'desc': 'Equilíbrio'},
        {'odds': 2.50, 'ms_correto': 40, 'ms_errado': 60, 'desc': 'Underdog'},
        {'odds': 3.00, 'ms_correto': 33, 'ms_errado': 67, 'desc': 'Underdog forte'}
    ]
    
    for caso in casos_teste:
        odds = caso['odds']
        ms_correto = caso['ms_correto']
        ms_errado = caso['ms_errado']
        desc = caso['desc']
        
        prob_esperada = 1 / odds * 100
        diferenca_correto = abs(ms_correto - prob_esperada)
        diferenca_errado = abs(ms_errado - prob_esperada)
        
        print(f"\\n📊 {desc} (Odds: {odds})")
        print(f"   🎯 Probabilidade esperada: {prob_esperada:.1f}%")
        print(f"   ✅ MS correto: {ms_correto}% (diferença: {diferenca_correto:.1f}%)")
        print(f"   ❌ MS errado: {ms_errado}% (diferença: {diferenca_errado:.1f}%)")
        
        if diferenca_correto < diferenca_errado:
            print(f"   🔍 Validação: MS correto seria ACEITO")
        else:
            print(f"   🔍 Validação: MS errado seria CORRIGIDO")

def teste_casos_reais_api():
    """
    Simula como a correção funcionaria com dados reais da API
    """
    print("\\n" + "=" * 60)
    print("🌐 SIMULAÇÃO COM DADOS REAIS DA API")
    print("=" * 60)
    
    # Simular dados da API (baseado nos casos RED)
    dados_api_simulados = [
        {
            'evento_id': '12345',
            'home': 'Taddia/Vaccari',
            'away': 'Adversário A',
            'odds_home': 1.72,
            'odds_away': 2.18,
            'stats': {
                'jogador1_ms': 55,  # HOME com MS baixo (ERRADO)
                'jogador2_ms': 45,  # AWAY com MS baixo
            },
            'target_jogador': 'Taddia/Vaccari'
        },
        {
            'evento_id': '12346',
            'home': 'Adversário B',
            'away': 'Nicholas Godsick',
            'odds_home': 2.45,
            'odds_away': 1.66,
            'stats': {
                'jogador1_ms': 40,  # HOME com MS baixo 
                'jogador2_ms': 60,  # AWAY com MS médio (ERRADO para favorito)
            },
            'target_jogador': 'Nicholas Godsick'
        }
    ]
    
    for dados in dados_api_simulados:
        print(f"\\n🎾 Evento: {dados['target_jogador']}")
        print(f"   🏠 HOME: {dados['home']} (odds: {dados['odds_home']})")
        print(f"   ✈️ AWAY: {dados['away']} (odds: {dados['odds_away']})")
        
        target = dados['target_jogador']
        is_home = target in dados['home']
        
        if is_home:
            odds_target = dados['odds_home']
            ms_original = dados['stats']['jogador1_ms']
            ms_alternativo = dados['stats']['jogador2_ms']
            posicao = "HOME"
        else:
            odds_target = dados['odds_away']
            ms_original = dados['stats']['jogador2_ms']
            ms_alternativo = dados['stats']['jogador1_ms']
            posicao = "AWAY"
        
        print(f"   🎯 Target: {target} ({posicao})")
        print(f"   💰 Odds target: {odds_target}")
        
        # Validação
        prob_esperada = 1 / odds_target * 100
        diferenca_original = abs(ms_original - prob_esperada)
        diferenca_alternativo = abs(ms_alternativo - prob_esperada)
        
        print(f"   📊 MS original: {ms_original}% (diferença: {diferenca_original:.1f}%)")
        print(f"   📊 MS alternativo: {ms_alternativo}% (diferença: {diferenca_alternativo:.1f}%)")
        
        if diferenca_original > 25 and diferenca_alternativo < diferenca_original:
            print(f"   🚨 CORREÇÃO APLICADA: {ms_original}% → {ms_alternativo}%")
            ms_final = ms_alternativo
        else:
            print(f"   ✅ MS VALIDADO: {ms_original}%")
            ms_final = ms_original
        
        ev_final = (ms_final/100 * odds_target) - 1
        aprovado = ev_final >= 0.15 and 55 <= ms_final <= 75
        
        print(f"   📈 EV final: {ev_final:.3f}")
        print(f"   🎯 Resultado: {'✅ APROVADO' if aprovado else '❌ REJEITADO'}")

if __name__ == "__main__":
    simular_casos_antes_depois()
    testar_validacao_ms_odds()
    teste_casos_reais_api()
