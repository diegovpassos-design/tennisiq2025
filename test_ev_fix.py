#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste para verificar correção do cálculo de EV
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

def test_ev_calculation():
    """Testa o cálculo correto de EV"""
    
    # Importar função de cálculo
    from backend.data.opportunities.seleção_final import calcular_ev
    
    print("🧪 TESTE DE CÁLCULO DE EV")
    print("=" * 50)
    
    # Dados simulados do seu exemplo
    momentum_giselle = 51.0  # Momentum Score da Giselle
    momentum_monique = 49.0  # Momentum Score da Monique
    
    odd_giselle = 1.363  # Odd da Giselle (favorita)
    odd_monique = 3.000  # Odd da Monique (adversária)
    
    print(f"Dados simulados:")
    print(f"  Giselle: Momentum {momentum_giselle}% - Odd {odd_giselle}")
    print(f"  Monique: Momentum {momentum_monique}% - Odd {odd_monique}")
    print()
    
    # Teste 1: EV da Giselle com sua própria odd
    print("🔍 Teste 1: EV da Giselle com sua odd (1.363)")
    ev_giselle_correto = calcular_ev(momentum_giselle, odd_giselle)
    print(f"Resultado: {ev_giselle_correto:.3f}")
    print()
    
    # Teste 2: EV da Giselle com odd errada (da Monique)
    print("🔍 Teste 2: EV da Giselle com odd ERRADA (3.000)")
    ev_giselle_errado = calcular_ev(momentum_giselle, odd_monique)
    print(f"Resultado: {ev_giselle_errado:.3f}")
    print(f"❌ Este seria o EV INCORRETO se usasse odd errada")
    print()
    
    # Teste 3: EV da Monique com sua própria odd
    print("🔍 Teste 3: EV da Monique com sua odd (3.000)")
    ev_monique_correto = calcular_ev(momentum_monique, odd_monique)
    print(f"Resultado: {ev_monique_correto:.3f}")
    print()
    
    # Teste 4: EV da Monique com odd errada (da Giselle)
    print("🔍 Teste 4: EV da Monique com odd ERRADA (1.363)")
    ev_monique_errado = calcular_ev(momentum_monique, odd_giselle)
    print(f"Resultado: {ev_monique_errado:.3f}")
    print(f"❌ Este seria o EV INCORRETO se usasse odd errada")
    print()
    
    print("📊 RESUMO:")
    print(f"  EV máximo CORRETO: {max(ev_giselle_correto, ev_monique_correto):.3f}")
    print(f"  EV máximo INCORRETO (odds trocadas): {max(ev_giselle_errado, ev_monique_errado):.3f}")
    
    diferenca = abs(max(ev_giselle_correto, ev_monique_correto) - max(ev_giselle_errado, ev_monique_errado))
    print(f"  Diferença: {diferenca:.3f}")
    
    if diferenca > 0.1:
        print(f"  ⚠️ DIFERENÇA SIGNIFICATIVA! A correção é importante.")
    else:
        print(f"  ✅ Diferença pequena, mas correção ainda é necessária.")

if __name__ == "__main__":
    test_ev_calculation()
