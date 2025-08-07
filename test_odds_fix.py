#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste para verificar correção das odds
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

def test_odds_extraction():
    """Testa a extração correta de odds"""
    
    # Simular dados do seu exemplo
    odds_data = {
        'jogador1_odd': 1.363,  # Giselle (Casa)
        'jogador2_odd': 3.000,  # Monique (Visitante)
        'jogador1_nome': 'Giselle Isabella Guillen',
        'jogador2_nome': 'Monique Barry'
    }
    
    # Importar o bot
    from backend.core.bot import TennisIQBot
    bot = TennisIQBot()
    
    print("🧪 TESTE DE EXTRAÇÃO DE ODDS")
    print("=" * 50)
    print(f"Dados simulados:")
    print(f"  J1: {odds_data['jogador1_nome']} - Odd: {odds_data['jogador1_odd']}")
    print(f"  J2: {odds_data['jogador2_nome']} - Odd: {odds_data['jogador2_odd']}")
    print()
    
    # Teste 1: Buscar odd da Giselle
    print("🔍 Teste 1: Buscar odd da Giselle")
    odd_giselle = bot.extrair_odd_jogador(odds_data, "Giselle Isabella Guillen")
    print(f"Resultado: {odd_giselle}")
    print(f"Esperado: 1.363 - {'✅ CORRETO' if odd_giselle == 1.363 else '❌ ERRO'}")
    print()
    
    # Teste 2: Buscar odd da Monique
    print("🔍 Teste 2: Buscar odd da Monique")
    odd_monique = bot.extrair_odd_oponente(odds_data, "Monique Barry")
    print(f"Resultado: {odd_monique}")
    print(f"Esperado: 3.000 - {'✅ CORRETO' if odd_monique == 3.000 else '❌ ERRO'}")
    print()
    
    # Teste 3: Testar com nomes parciais
    print("🔍 Teste 3: Buscar com nome parcial 'Giselle'")
    odd_giselle_parcial = bot.extrair_odd_jogador(odds_data, "Giselle")
    print(f"Resultado: {odd_giselle_parcial}")
    print(f"Esperado: 1.363 - {'✅ CORRETO' if odd_giselle_parcial == 1.363 else '❌ ERRO'}")
    print()
    
    # Teste 4: Testar com nomes parciais
    print("🔍 Teste 4: Buscar com nome parcial 'Monique'")
    odd_monique_parcial = bot.extrair_odd_oponente(odds_data, "Monique")
    print(f"Resultado: {odd_monique_parcial}")
    print(f"Esperado: 3.000 - {'✅ CORRETO' if odd_monique_parcial == 3.000 else '❌ ERRO'}")

if __name__ == "__main__":
    test_odds_extraction()
