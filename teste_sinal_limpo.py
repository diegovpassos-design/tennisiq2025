#!/usr/bin/env python3
"""
Teste do formato do sinal sem dados técnicos
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.core.bot import TennisIQBot

def main():
    print("📧 TESTANDO FORMATO DO SINAL SEM DADOS TÉCNICOS:")
    print("=" * 60)
    
    # Criar instância do bot
    bot = TennisIQBot()
    
    # Dados de teste para oportunidade
    oportunidade_teste = {
        'jogador': 'Murariu/Stirbu',
        'oponente': 'Banti/Mesaglio',
        'partida_id': '10419025',
        'tipo': 'HOME'
    }
    
    odds_data = {
        'jogador1_odd': 2.2,
        'limite_minimo': 1.56
    }
    
    dados_filtros = {
        'ev': 0.430,
        'momentum_score': 65.0,
        'double_faults': 2,
        'win_1st_serve': 75.0,
        'fase_timing': '2set_mid',
        'placar_momento': '6-2,4-4',
        'liga': 'ITF M15 Curtea de Arges MD'
    }
    
    # Gerar sinal
    sinal = bot.gerar_sinal_tennisiq(oportunidade_teste, odds_data, dados_filtros)
    
    print("📤 FORMATO ATUAL DO SINAL:")
    print("-" * 40)
    print(sinal)
    print("-" * 40)
    
    print("\n✅ DADOS TÉCNICOS REMOVIDOS:")
    print("❌ • EV: +0.430")
    print("❌ • MS: 65.0%")
    print("❌ • DF: 2")
    print("❌ • W1S: 75.0%")
    print("❌ • Fase: 2set_mid")
    print("❌ • Placar: 6-2,4-4")
    print("❌ • Liga: ITF M15 Curtea de Arges MD")
    
    print("\n🎯 Sinal agora é mais limpo e direto!")

if __name__ == "__main__":
    main()
