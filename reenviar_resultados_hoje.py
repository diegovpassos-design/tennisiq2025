#!/usr/bin/env python3
"""
Reenviar resultados de hoje com mensagens atualizadas
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.core.bot import TennisIQBot
import json
from datetime import datetime

def main():
    print("📧 REENVIANDO RESULTADOS DE HOJE COM MENSAGENS ATUALIZADAS")
    print("=" * 70)
    
    # Criar instância do bot
    bot = TennisIQBot()
    
    if not bot.verificador_resultados:
        print("❌ Verificador de resultados não foi inicializado!")
        return
    
    # Buscar apostas de hoje (5 de agosto de 2025) que têm resultado
    apostas_hoje = []
    hoje = "2025-08-05"
    
    for aposta in bot.verificador_resultados.historico_apostas:
        data_aposta = aposta.get('data_aposta', '')
        if hoje in data_aposta and aposta.get('resultado_verificacao'):
            apostas_hoje.append(aposta)
    
    print(f"📊 Encontradas {len(apostas_hoje)} apostas de hoje com resultado:")
    print("-" * 50)
    
    resultados_hoje = {
        'GREEN': [],
        'RED': [],
        'VOID': []
    }
    
    # Processar cada aposta de hoje
    for i, aposta in enumerate(apostas_hoje, 1):
        resultado = aposta.get('resultado_verificacao', {})
        status = resultado.get('status', 'N/A')
        jogador = aposta.get('jogador_apostado', 'N/A')
        oponente = aposta.get('oponente', 'N/A')
        hora_aposta = aposta.get('data_aposta', '')[:16].replace('T', ' ')
        
        print(f"{i}. {jogador} vs {oponente}")
        print(f"   📅 Hora: {hora_aposta}")
        print(f"   📊 Status: {status}")
        
        resultados_hoje[status].append(aposta)
        
        # Reenviar com as mensagens atualizadas
        try:
            print(f"   📤 Reenviando resultado...")
            bot.enviar_resultado_aposta(aposta, resultado)
            print(f"   ✅ Reenviado com sucesso!")
        except Exception as e:
            print(f"   ❌ Erro ao reenviar: {e}")
        
        print("-" * 50)
    
    # Resumo final
    print("\n📈 RESUMO DOS RESULTADOS DE HOJE:")
    print("=" * 50)
    print(f"🟢 GREEN: {len(resultados_hoje['GREEN'])} apostas")
    for aposta in resultados_hoje['GREEN']:
        print(f"   ✅ {aposta['jogador_apostado']} vs {aposta['oponente']}")
    
    print(f"\n🔴 RED: {len(resultados_hoje['RED'])} apostas")
    for aposta in resultados_hoje['RED']:
        print(f"   ❌ {aposta['jogador_apostado']} vs {aposta['oponente']}")
    
    print(f"\n⚪ VOID: {len(resultados_hoje['VOID'])} apostas")
    for aposta in resultados_hoje['VOID']:
        print(f"   ⚠️ {aposta['jogador_apostado']} vs {aposta['oponente']}")
    
    total = len(apostas_hoje)
    greens = len(resultados_hoje['GREEN'])
    if total > 0:
        taxa_acerto = (greens / total) * 100
        print(f"\n🎯 TAXA DE ACERTO: {taxa_acerto:.1f}% ({greens} GREEN em {total} apostas)")
    
    print(f"\n✅ Todos os {len(apostas_hoje)} resultados foram reenviados com as mensagens atualizadas!")

if __name__ == "__main__":
    main()
