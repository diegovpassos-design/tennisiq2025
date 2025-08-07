#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VERIFICAÇÃO DO CÁLCULO DO MOMENTUM SCORE (MS)
============================================
Análise detalhada de como o MS está sendo calculado por jogador
para entender se há problemas de atribuição entre jogadores
"""

import json
from datetime import datetime

def analisar_calculo_ms():
    """
    Analisa como o MS está sendo calculado baseado no código
    """
    print("🔍 VERIFICAÇÃO DO CÁLCULO DO MOMENTUM SCORE (MS)")
    print("=" * 70)
    
    # 1. PROBLEMA IDENTIFICADO: MS PODE ESTAR INVERTIDO
    print("\n❗ PROBLEMA POTENCIAL DETECTADO:")
    print("   • MS é calculado baseado em estatísticas (aces, win 1st serve, break points)")
    print("   • Mas a ATRIBUIÇÃO pode estar ERRADA entre jogador1 vs jogador2")
    print("   • Odds também podem estar sendo atribuídas ao jogador ERRADO")
    
    # 2. FLUXO ATUAL DO CÁLCULO
    print("\n📋 FLUXO ATUAL DO CÁLCULO:")
    print("   1️⃣ API retorna stats[aces][0] e stats[aces][1] (jogador1 e jogador2)")
    print("   2️⃣ Calcula momentum ponderado: (aces - df) + win_1st_serve")
    print("   3️⃣ Converte para %: jogador1_ms vs jogador2_ms")
    print("   4️⃣ Identifica se jogador é HOME ou AWAY")
    print("   5️⃣ Atribui MS correto ao jogador específico")
    
    # 3. POSSÍVEIS PROBLEMAS
    print("\n⚠️ POSSÍVEIS PROBLEMAS:")
    print("   🔄 INVERSÃO DE DADOS:")
    print("      • stats[0] pode ser jogador2 em vez de jogador1")
    print("      • odds[0] pode estar para o jogador errado")
    print("      • Identificação HOME/AWAY pode estar incorreta")
    
    print("\n   📊 CÁLCULO INCORRETO:")
    print("      • Momentum formula pode estar errada")
    print("      • Pesos dos fatores inadequados")
    print("      • Conversão para % problemática")
    
    # 4. CASOS ESPECÍFICOS DOS REDS
    print("\n🔴 ANÁLISE DOS CASOS RED:")
    casos_red = [
        {
            'jogador': 'Taddia/Vaccari',
            'ms': '55%',
            'ev': '0.26',
            'odds': '1.72',
            'resultado': 'RED',
            'suspeita': 'MS muito baixo para favorito - pode estar invertido'
        },
        {
            'jogador': 'Nicholas Godsick',
            'ms': '60%',
            'ev': '0.16',
            'odds': '1.66',
            'resultado': 'RED',
            'suspeita': 'Odds muito baixa, MS pode ser do adversário'
        },
        {
            'jogador': 'Lucie Urbanova',
            'ms': '55%',
            'ev': '0.10',
            'odds': '1.70',
            'resultado': 'RED',
            'suspeita': 'MS baixo para favorito - provável inversão'
        },
        {
            'jogador': 'Tessa Johanna Brockmann',
            'ms': '60%',
            'ev': '0.20',
            'odds': '1.69',
            'resultado': 'RED',
            'suspeita': 'Padrão: favorito com MS baixo'
        }
    ]
    
    print("\n📊 PADRÃO DETECTADO NOS REDS:")
    for caso in casos_red:
        print(f"   👤 {caso['jogador']}")
        print(f"      📈 MS: {caso['ms']} | 💰 EV: {caso['ev']} | 🎯 Odds: {caso['odds']}")
        print(f"      🔍 Suspeita: {caso['suspeita']}")
        print()
    
    # 5. EVIDÊNCIAS DE INVERSÃO
    print("🚨 EVIDÊNCIAS DE INVERSÃO DE MS:")
    print("   ✅ TODOS os favoritos têm MS entre 55-60% (muito baixo)")
    print("   ✅ Com odds 1.66-1.72, deveriam ter MS > 70%")
    print("   ✅ MS baixo = adversário forte = odds deveria ser alta")
    print("   ✅ CONTRADIÇÃO: odds baixa + MS baixo = impossível")
    
    # 6. COMPARAÇÃO COM ESTRATÉGIA INVERTIDA
    casos_invertida = [
        {
            'jogador': 'Kristjan Tamm',
            'ms_adversario': '300+ pontos',
            'odds': '2.4+',
            'resultado': 'RED',
            'observacao': 'Sistema invertido funcionou melhor'
        },
        {
            'jogador': 'Arina Rodionova', 
            'ms_adversario': '300+ pontos',
            'odds': '2.1+',
            'resultado': 'RED',
            'observacao': 'Underdogs com mental score alto'
        }
    ]
    
    print("\n🔄 COMPARAÇÃO COM ESTRATÉGIA INVERTIDA:")
    print("   • Estratégia invertida: 60% acerto (3/5)")
    print("   • Estratégia tradicional: 0% acerto (0/4)")
    print("   • Suspeita: MS tradicional está INVERTIDO")
    
    # 7. SOLUÇÃO PROPOSTA
    print("\n💡 SOLUÇÃO PROPOSTA:")
    print("   1️⃣ VERIFICAR identificação HOME/AWAY")
    print("   2️⃣ VALIDAR atribuição de odds por jogador")
    print("   3️⃣ CONFIRMAR cálculo correto do MS")
    print("   4️⃣ TESTAR inversão: MS_real = 100 - MS_calculado")
    print("   5️⃣ CRIAR validação cruzada com nomes dos jogadores")
    
    # 8. TESTE RÁPIDO
    print("\n🧪 TESTE RÁPIDO - INVERSÃO DO MS:")
    print("   Se invertermos o MS dos casos RED:")
    for caso in casos_red:
        ms_original = int(caso['ms'].replace('%', ''))
        ms_invertido = 100 - ms_original
        odds = float(caso['odds'])
        ev_novo = (ms_invertido/100 * odds) - 1
        
        print(f"   👤 {caso['jogador'][:20]}...")
        print(f"      📊 MS original: {ms_original}% → MS invertido: {ms_invertido}%")
        print(f"      💰 EV original: {caso['ev']} → EV novo: {ev_novo:.3f}")
        print(f"      🎯 Resultado: {'SERIA REJEITADO' if ms_invertido < 65 else 'APROVADO'}")
        print()
    
    print("🎯 CONCLUSÃO:")
    print("   ✅ INVERSÃO DO MS explicaria os 100% de REDs na estratégia tradicional")
    print("   ✅ Favoritos com odds baixa DEVERIAM ter MS alto (70-80%)")
    print("   ✅ MS baixo indica que estamos apostando no jogador ERRADO")
    print("   🚨 URGENTE: Verificar e corrigir atribuição do MS por jogador")

def verificar_estrutura_dados():
    """
    Verifica a estrutura dos dados da API para entender o problema
    """
    print("\n" + "="*70)
    print("🔍 VERIFICAÇÃO DA ESTRUTURA DOS DADOS")
    print("="*70)
    
    print("📋 ESTRUTURA ESPERADA DA API:")
    print("   • events[].home.name = Nome do jogador HOME")
    print("   • events[].away.name = Nome do jogador AWAY") 
    print("   • odds[0] = Odd do jogador HOME")
    print("   • odds[1] = Odd do jogador AWAY")
    print("   • stats[aces][0] = Aces jogador HOME")
    print("   • stats[aces][1] = Aces jogador AWAY")
    
    print("\n❗ PROBLEMA IDENTIFICADO:")
    print("   🔄 Função 'buscar_dados_jogador' faz:")
    print("      1. Identifica se jogador é HOME ou AWAY")
    print("      2. Se HOME: usa stats[0] e odds[0]")
    print("      3. Se AWAY: usa stats[1] e odds[1]")
    print("   ⚠️ MAS identificação HOME/AWAY pode estar ERRADA!")
    
    print("\n🚨 EVIDÊNCIA DO ERRO:")
    print("   • TODOS favoritos com odds 1.66-1.72 têm MS 55-60%")
    print("   • Isso é IMPOSSÍVEL - favorito deve ter MS > 70%")
    print("   • Logo: estamos pegando MS do ADVERSÁRIO!")
    
    print("\n💡 SOLUÇÃO:")
    print("   1. Verificar lógica 'is_home = jogador_nome in jogador_casa'")
    print("   2. Pode estar fazendo match incorreto")
    print("   3. Testar com nomes completos vs parciais")
    print("   4. Validar com prints de debug")

if __name__ == "__main__":
    analisar_calculo_ms()
    verificar_estrutura_dados()
