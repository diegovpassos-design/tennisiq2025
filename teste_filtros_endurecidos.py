#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TESTE DAS ALTERAÇÕES NA ESTRATÉGIA TRADICIONAL
==============================================
Verificando como as alterações MS: 55% → 65% e Odds: ≥1.75 afetam os casos RED
"""

def testar_novos_filtros():
    """
    Testa como os novos filtros afetariam os casos RED anteriores
    """
    print("🔧 TESTE DOS NOVOS FILTROS DA ESTRATÉGIA TRADICIONAL")
    print("=" * 70)
    print("📊 ALTERAÇÕES APLICADAS:")
    print("   • MS mínimo: 55% → 65% (ENDURECIDO)")
    print("   • Odds mínimas: ≥1.75 (MANTIDO)")
    print("   • Correção do MS invertido: APLICADA")
    
    # Casos RED originais
    casos_red = [
        {
            'jogador': 'Taddia/Vaccari',
            'ms_original': 55,
            'ms_corrigido': 55,  # Após correção de inversão
            'odds': 1.72,
            'ev_original': 0.26,
            'ev_corrigido': -0.05,
            'tipo': 'dupla'
        },
        {
            'jogador': 'Nicholas Godsick',
            'ms_original': 60,
            'ms_corrigido': 60,  # Após correção de inversão
            'odds': 1.66,
            'ev_original': 0.16,
            'ev_corrigido': -0.00,
            'tipo': 'individual'
        },
        {
            'jogador': 'Lucie Urbanova',
            'ms_original': 55,
            'ms_corrigido': 55,  # Após correção de inversão
            'odds': 1.70,
            'ev_original': 0.10,
            'ev_corrigido': -0.06,
            'tipo': 'individual'
        },
        {
            'jogador': 'Tessa Johanna Brockmann',
            'ms_original': 60,
            'ms_corrigido': 60,  # Após correção de inversão
            'odds': 1.69,
            'ev_original': 0.20,
            'ev_corrigido': 0.01,
            'tipo': 'individual'
        }
    ]
    
    print("\\n📋 ANÁLISE COM FILTROS ANTIGOS (ANTES):")
    print("-" * 70)
    aprovados_antes = 0
    
    for caso in casos_red:
        ms = caso['ms_original']
        odds = caso['odds']
        ev = caso['ev_original']
        
        # Filtros antigos
        aprovado_ms = ms >= 55  # MS antigo
        aprovado_odds = 1.75 <= odds <= 2.80
        aprovado_ev = ev >= 0.15
        aprovado_geral = aprovado_ms and aprovado_odds and aprovado_ev
        
        if aprovado_geral:
            aprovados_antes += 1
        
        status_ms = "✅" if aprovado_ms else "❌"
        status_odds = "✅" if aprovado_odds else "❌"
        status_ev = "✅" if aprovado_ev else "❌"
        status_geral = "✅ APROVADO" if aprovado_geral else "❌ REJEITADO"
        
        print(f"👤 {caso['jogador'][:25]:<25} | MS: {ms:>2}% {status_ms} | Odds: {odds} {status_odds} | EV: {ev:>5.2f} {status_ev} | {status_geral}")
    
    print(f"\\n📊 Resultado ANTES: {aprovados_antes}/4 = {aprovados_antes/4*100:.0f}% aprovados → 100% RED")
    
    print("\\n📋 ANÁLISE COM FILTROS NOVOS (DEPOIS):")
    print("-" * 70)
    aprovados_depois = 0
    
    for caso in casos_red:
        ms = caso['ms_corrigido']  # Usar MS após correção de inversão
        odds = caso['odds']
        ev = caso['ev_corrigido']  # EV recalculado após correção
        
        # Filtros novos (ENDURECIDOS)
        aprovado_ms = ms >= 65  # MS ENDURECIDO: 55% → 65%
        aprovado_odds = 1.75 <= odds <= 2.80
        aprovado_ev = ev >= 0.15
        aprovado_geral = aprovado_ms and aprovado_odds and aprovado_ev
        
        if aprovado_geral:
            aprovados_depois += 1
        
        status_ms = "✅" if aprovado_ms else "❌"
        status_odds = "✅" if aprovado_odds else "❌"
        status_ev = "✅" if aprovado_ev else "❌"
        status_geral = "✅ APROVADO" if aprovado_geral else "❌ REJEITADO"
        
        motivos_rejeicao = []
        if not aprovado_ms:
            motivos_rejeicao.append(f"MS {ms}% < 65%")
        if not aprovado_odds:
            motivos_rejeicao.append(f"Odds {odds} < 1.75")
        if not aprovado_ev:
            motivos_rejeicao.append(f"EV {ev:.2f} < 0.15")
        
        print(f"👤 {caso['jogador'][:25]:<25} | MS: {ms:>2}% {status_ms} | Odds: {odds} {status_odds} | EV: {ev:>5.2f} {status_ev} | {status_geral}")
        if motivos_rejeicao:
            print(f"      🔍 Motivos: {', '.join(motivos_rejeicao)}")
    
    print(f"\\n📊 Resultado DEPOIS: {aprovados_depois}/4 = {aprovados_depois/4*100:.0f}% aprovados → 0% RED esperado")
    
    print("\\n🎯 RESUMO DAS MELHORIAS:")
    print("-" * 70)
    print("1️⃣ CORREÇÃO DO MS INVERTIDO:")
    print("   • MS agora reflete corretamente o jogador")
    print("   • EV recalculado com MS correto")
    print("   • Favoritos com odds baixa agora têm MS coerente")
    
    print("\\n2️⃣ ENDURECIMENTO DOS FILTROS:")
    print("   • MS mínimo: 55% → 65% (+10%)")
    print("   • Filtro mais seletivo para estratégia tradicional")
    print("   • Reduz aprovação de casos marginais")
    
    print("\\n3️⃣ IMPACT ESPECÍFICO NOS CASOS RED:")
    for caso in casos_red:
        motivos = []
        if caso['ms_corrigido'] < 65:
            motivos.append("MS < 65%")
        if caso['odds'] < 1.75:
            motivos.append("Odds < 1.75")
        if caso['ev_corrigido'] < 0.15:
            motivos.append("EV < 0.15")
        
        print(f"   👤 {caso['jogador']}: {'✅ Seria REJEITADO' if motivos else '⚠️ Ainda seria aprovado'}")
        if motivos:
            print(f"      🔍 Por: {', '.join(motivos)}")

def simular_casos_futuros():
    """
    Simula como casos futuros seriam filtrados
    """
    print("\\n" + "=" * 70)
    print("🔮 SIMULAÇÃO DE CASOS FUTUROS")
    print("=" * 70)
    
    casos_simulados = [
        {'desc': 'Favorito forte', 'ms': 75, 'odds': 1.60, 'ev': 0.20},
        {'desc': 'Favorito médio', 'ms': 68, 'odds': 1.75, 'ev': 0.19},
        {'desc': 'Favorito borderline', 'ms': 64, 'odds': 1.80, 'ev': 0.15},
        {'desc': 'Caso marginal', 'ms': 62, 'odds': 1.85, 'ev': 0.12},
        {'desc': 'Underdog', 'ms': 45, 'odds': 2.20, 'ev': 0.01},
    ]
    
    print("📊 COMO NOVOS CASOS SERIAM TRATADOS:")
    print("-" * 70)
    
    for caso in casos_simulados:
        ms = caso['ms']
        odds = caso['odds']
        ev = caso['ev']
        desc = caso['desc']
        
        # Aplicar novos filtros
        aprovado_ms = ms >= 65
        aprovado_odds = 1.75 <= odds <= 2.80
        aprovado_ev = ev >= 0.15
        aprovado_geral = aprovado_ms and aprovado_odds and aprovado_ev
        
        status = "✅ APROVADO" if aprovado_geral else "❌ REJEITADO"
        
        print(f"🎯 {desc:<15} | MS: {ms:>2}% | Odds: {odds} | EV: {ev:>5.2f} | {status}")
        
        if not aprovado_geral:
            motivos = []
            if not aprovado_ms:
                motivos.append(f"MS {ms}% < 65%")
            if not aprovado_odds:
                motivos.append(f"Odds {odds} fora 1.75-2.80")
            if not aprovado_ev:
                motivos.append(f"EV {ev:.2f} < 0.15")
            print(f"      🔍 Motivos: {', '.join(motivos)}")
    
    print("\\n🎯 EXPECTATIVA:")
    print("   ✅ Apenas casos com MS ≥ 65% serão aprovados")
    print("   ✅ Odds muito baixas (< 1.75) rejeitadas automaticamente")
    print("   ✅ EV mínimo mantido em 0.15 para qualidade")
    print("   ✅ Drástica redução de REDs esperada")

if __name__ == "__main__":
    testar_novos_filtros()
    simular_casos_futuros()
