#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ANÁLISE DA SEQUÊNCIA DE REDS
============================
Análise das apostas que resultaram em sequência de reds
"""

import json
import sys
import os
from datetime import datetime

# Adicionar paths
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'core'))

def analisar_sequencia_red():
    """
    Analisa a sequência de REDs que você mencionou
    """
    
    apostas_red = [
        {"jogador": "Kristjan Tamm", "estrategia": "INVERTIDA", "resultado": "RED"},
        {"jogador": "Taddia/Vaccari", "estrategia": "TRADICIONAL", "resultado": "RED"},
        {"jogador": "Nicholas Godsick", "estrategia": "TRADICIONAL", "resultado": "RED"},
        {"jogador": "Arina Rodionova", "estrategia": "INVERTIDA", "resultado": "RED"},
        {"jogador": "Lucie Urbanova", "estrategia": "TRADICIONAL", "resultado": "RED"},
        {"jogador": "Tessa Johanna Brockmann", "estrategia": "TRADICIONAL", "resultado": "RED"}
    ]
    
    apostas_green = [
        {"jogador": "Hikaru Sato", "estrategia": "INVERTIDA", "resultado": "GREEN"},
        {"jogador": "Giselle Isabella Guille", "estrategia": "INVERTIDA", "resultado": "GREEN"},
        {"jogador": "Victoria Chramcova", "estrategia": "INVERTIDA", "resultado": "GREEN"}
    ]
    
    print("🚨 ANÁLISE DA SEQUÊNCIA DE REDS")
    print("="*60)
    
    # Análise por estratégia
    reds_invertida = [a for a in apostas_red if a["estrategia"] == "INVERTIDA"]
    reds_tradicional = [a for a in apostas_red if a["estrategia"] == "TRADICIONAL"]
    greens_invertida = [a for a in apostas_green if a["estrategia"] == "INVERTIDA"]
    
    print("\n📊 ESTATÍSTICAS POR ESTRATÉGIA:")
    print(f"🔄 INVERTIDA: {len(greens_invertida)} GREENs vs {len(reds_invertida)} REDs")
    print(f"📈 TRADICIONAL: 0 GREENs vs {len(reds_tradicional)} REDs")
    
    # Cálculo de accuracy
    total_invertida = len(greens_invertida) + len(reds_invertida)
    accuracy_invertida = (len(greens_invertida) / total_invertida * 100) if total_invertida > 0 else 0
    
    total_tradicional = len(reds_tradicional)
    accuracy_tradicional = 0  # Todos foram RED
    
    print(f"\n🎯 ACCURACY:")
    print(f"🔄 INVERTIDA: {accuracy_invertida:.1f}% ({len(greens_invertida)}/{total_invertida})")
    print(f"📈 TRADICIONAL: {accuracy_tradicional:.1f}% (0/{total_tradicional})")
    
    print("\n🔍 PROBLEMAS IDENTIFICADOS:")
    print("="*40)
    
    if accuracy_tradicional == 0:
        print("🚨 PROBLEMA CRÍTICO 1: ESTRATÉGIA TRADICIONAL 0% ACCURACY")
        print("   • Todos os sinais tradicionais falharam")
        print("   • Indica problema nos filtros tradicionais")
        print("   • Pode estar aprovando favoritos ruins")
        print()
    
    if accuracy_invertida < 60:
        print("⚠️  PROBLEMA 2: ESTRATÉGIA INVERTIDA ABAIXO DO ESPERADO")
        print(f"   • {accuracy_invertida:.1f}% vs meta de 65%+")
        print("   • Pode estar invertendo em momentos inadequados")
        print()
    
    print("🔬 POSSÍVEIS CAUSAS:")
    print("="*30)
    print("1. 📊 ODDS MATCHING: Inversão de odds jogador-favorito")
    print("2. 🧠 MENTAL SCORE: Thresholds inadequados para inversão")
    print("3. 🎯 EV CALCULATION: Cálculos usando odds erradas")
    print("4. ⏰ TIMING: Sinais enviados em momentos inadequados")
    print("5. 🎲 FILTROS DE ODDS: Range 1.75-2.80 muito restritivo")
    print()
    
    print("🛠️  INVESTIGAÇÕES NECESSÁRIAS:")
    print("="*35)
    print("1. Verificar se odds estão sendo atribuídas corretamente")
    print("2. Analisar thresholds do detector de vantagem mental")
    print("3. Validar cálculos de EV com odds corretas")
    print("4. Revisar filtros de momentum score e timing")
    print("5. Verificar se duplicatas estão sendo enviadas")
    
    return {
        "accuracy_invertida": accuracy_invertida,
        "accuracy_tradicional": accuracy_tradicional,
        "total_apostas": len(apostas_red) + len(apostas_green),
        "problemas_criticos": accuracy_tradicional == 0
    }

def analisar_dados_historicos():
    """
    Analisa dados do histórico de apostas para identificar padrões
    """
    try:
        historico_path = r"c:\Users\diego\OneDrive\Documentos\TennisQ\backend\data\results\historico_apostas.json"
        
        if not os.path.exists(historico_path):
            print("❌ Arquivo de histórico não encontrado")
            return
        
        with open(historico_path, 'r', encoding='utf-8') as f:
            apostas = json.load(f)
        
        print("\n📈 ANÁLISE DO HISTÓRICO COMPLETO:")
        print("="*40)
        
        # Contar por status
        status_count = {}
        total_apostas = len(apostas)
        
        for aposta in apostas:
            status = aposta.get('status', 'PENDENTE')
            status_count[status] = status_count.get(status, 0) + 1
        
        print(f"📊 Total de apostas: {total_apostas}")
        for status, count in status_count.items():
            percent = (count / total_apostas * 100) if total_apostas > 0 else 0
            print(f"   {status}: {count} ({percent:.1f}%)")
        
        # Análise recente
        apostas_recentes = [a for a in apostas if a.get('data_aposta', '').startswith('2025-08-07')]
        print(f"\n📅 Apostas de hoje (07/08): {len(apostas_recentes)}")
        
        for aposta in apostas_recentes:
            jogador = aposta.get('jogador_apostado', '')
            status = aposta.get('status', 'PENDENTE')
            odd = aposta.get('odd', 0)
            liga = aposta.get('liga', '')
            print(f"   🎯 {jogador} | {status} | Odd: {odd} | {liga}")
    
    except Exception as e:
        print(f"❌ Erro ao analisar histórico: {e}")

def verificar_terminal_output():
    """
    Verifica se há informações no terminal atual
    """
    print("\n🖥️  VERIFICAÇÃO DO TERMINAL:")
    print("="*30)
    print("⚠️  Para análise completa, verifique:")
    print("1. Logs do terminal do bot")
    print("2. Odds sendo coletadas em tempo real")
    print("3. Filtros sendo aplicados")
    print("4. Estratégias (INVERTIDA vs TRADICIONAL)")

if __name__ == "__main__":
    print("🎾 TENNISIQ - ANÁLISE DE SEQUÊNCIA DE REDS")
    print("="*60)
    
    # Análise da sequência específica
    resultado = analisar_sequencia_red()
    
    # Análise do histórico
    analisar_dados_historicos()
    
    # Verificação do terminal
    verificar_terminal_output()
    
    print("\n" + "="*60)
    print("✅ ANÁLISE CONCLUÍDA")
    
    if resultado["problemas_criticos"]:
        print("🚨 AÇÃO URGENTE NECESSÁRIA: Estratégia tradicional com 0% accuracy!")
    
    print("📋 Próximos passos: Verificar código de odds matching e filtros")
