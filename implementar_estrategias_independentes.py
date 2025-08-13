#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 IMPLEMENTAÇÃO: ESTRATÉGIAS INDEPENDENTES
============================================================
Modifica o seleção_final.py para que cada estratégia opere independentemente
"""

import os
import sys

def aplicar_correcao_estrategias_independentes():
    """Aplica correção para estratégias independentes"""
    
    print("🔧 === CORREÇÃO: ESTRATÉGIAS INDEPENDENTES ===")
    print("🎯 Modificando seleção_final.py para separar estratégias")
    
    # Definir critérios independentes para cada estratégia
    criterios_independentes = '''
# 🎯 CRITÉRIOS INDEPENDENTES POR ESTRATÉGIA
# ============================================================

# 🚀 ESTRATÉGIA ALAVANCAGEM - Para EVs muito altos (independente)
CRITERIOS_ALAVANCAGEM = {
    'EV_MINIMO': 0.5,             # EVs altos (0.5+)
    'EV_MAXIMO': 50.0,            # Sem limite superior
    'MOMENTUM_SCORE_MINIMO': 40,  # MS ≥ 40% (RELAXADO)
    'WIN_1ST_SERVE_MINIMO': 50,   # W1S ≥ 50% (RELAXADO)
    'DOUBLE_FAULTS_MAXIMO': 8,    # DF ≤ 8 (RELAXADO)
    'PRIORIDADE_MINIMA': 2,       # Prioridade ≥ 2 (RELAXADO)
    'NOME': 'ALAVANCAGEM'
}

# 🧠 ESTRATÉGIA VANTAGEM MENTAL - Para situações psicológicas (independente)
CRITERIOS_VANTAGEM_MENTAL = {
    'EV_MINIMO': 0.15,            # EV moderado
    'EV_MAXIMO': 2.0,             # Limite moderado
    'MOMENTUM_SCORE_MINIMO': 60,  # MS ≥ 60% (importante para mental)
    'WIN_1ST_SERVE_MINIMO': 60,   # W1S ≥ 60% (importante para mental)
    'DOUBLE_FAULTS_MAXIMO': 4,    # DF ≤ 4 (rigoroso para mental)
    'PRIORIDADE_MINIMA': 3,       # Prioridade ≥ 3
    'NOME': 'VANTAGEM_MENTAL'
}

# 🔄 ESTRATÉGIA INVERTIDA - Para fadiga e 3º sets (independente)
CRITERIOS_INVERTIDOS = {
    'EV_MINIMO': 0.1,             # EV baixo (situações especiais)
    'EV_MAXIMO': 3.0,             # Permite EVs altos
    'MOMENTUM_SCORE_MINIMO': 45,  # MS ≥ 45% (MUITO RELAXADO)
    'WIN_1ST_SERVE_MINIMO': 45,   # W1S ≥ 45% (MUITO RELAXADO)
    'DOUBLE_FAULTS_MAXIMO': 6,    # DF ≤ 6 (relaxado)
    'PRIORIDADE_MINIMA': 2,       # Prioridade ≥ 2
    'NOME': 'INVERTIDA'
}

def avaliar_estrategia_independente(dados_jogador, partida, criterios):
    """Avalia UMA estratégia específica independentemente das outras"""
    
    filtros_aprovados = []
    filtros_rejeitados = []
    estrategia_nome = criterios['NOME']
    
    # Filtro EV
    if criterios['EV_MINIMO'] <= dados_jogador['ev'] <= criterios['EV_MAXIMO']:
        filtros_aprovados.append(f"EV: {dados_jogador['ev']:.3f} ✅")
    else:
        filtros_rejeitados.append(f"EV: {dados_jogador['ev']:.3f} ❌")
    
    # Filtro Momentum Score
    if dados_jogador['momentum_score'] >= criterios['MOMENTUM_SCORE_MINIMO']:
        filtros_aprovados.append(f"MS: {dados_jogador['momentum_score']:.1f}% ✅")
    else:
        filtros_rejeitados.append(f"MS: {dados_jogador['momentum_score']:.1f}% ❌")
    
    # Filtro Double Faults
    try:
        df_value = int(dados_jogador['double_faults']) if dados_jogador['double_faults'] else 0
        if 0 <= df_value <= criterios['DOUBLE_FAULTS_MAXIMO']:
            filtros_aprovados.append(f"DF: {df_value} ✅")
        else:
            filtros_rejeitados.append(f"DF: {df_value} ❌")
    except (ValueError, TypeError):
        filtros_rejeitados.append(f"DF: inválido ❌")
    
    # Filtro Win 1st Serve
    try:
        w1s_value = float(dados_jogador['win_1st_serve']) if dados_jogador['win_1st_serve'] else 0
        if w1s_value >= criterios['WIN_1ST_SERVE_MINIMO']:
            filtros_aprovados.append(f"W1S: {w1s_value}% ✅")
        else:
            filtros_rejeitados.append(f"W1S: {w1s_value}% ❌")
    except (ValueError, TypeError):
        filtros_rejeitados.append(f"W1S: inválido ❌")
    
    # Estratégia aprovada se TODOS os filtros passaram
    aprovada = len(filtros_rejeitados) == 0
    
    if aprovada:
        print(f"   ✅ {estrategia_nome}: {dados_jogador.get('nome', 'N/A')} APROVADO!")
        print(f"      {', '.join(filtros_aprovados)}")
    else:
        print(f"   ❌ {estrategia_nome}: {dados_jogador.get('nome', 'N/A')} rejeitado")
        print(f"      {', '.join(filtros_rejeitados[:2])}...")
    
    return aprovada, estrategia_nome, filtros_aprovados
'''
    
    print("✅ Critérios independentes definidos:")
    print("   🚀 ALAVANCAGEM: EV ≥ 0.5, MS ≥ 40%, W1S ≥ 50% (RELAXADO)")
    print("   🧠 VANTAGEM MENTAL: EV ≥ 0.15, MS ≥ 60%, W1S ≥ 60% (RIGOROSO)")  
    print("   🔄 INVERTIDA: EV ≥ 0.1, MS ≥ 45%, W1S ≥ 45% (MUITO RELAXADO)")
    
    return criterios_independentes

def criar_funcao_processamento_independente():
    """Cria função que processa cada estratégia independentemente"""
    
    funcao_processamento = '''
def processar_estrategias_independentes(partidas_timing):
    """Processa CADA estratégia independentemente (uma não interfere na outra)"""
    
    oportunidades_por_estrategia = {
        'ALAVANCAGEM': [],
        'VANTAGEM_MENTAL': [],
        'INVERTIDA': []
    }
    
    todas_estrategias = [CRITERIOS_ALAVANCAGEM, CRITERIOS_VANTAGEM_MENTAL, CRITERIOS_INVERTIDOS]
    
    print("\\n🎯 === PROCESSAMENTO INDEPENDENTE DE ESTRATÉGIAS ===")
    
    for partida in partidas_timing:
        print(f"\\n🔍 {partida['jogador1']} vs {partida['jogador2']}")
        
        # Para cada jogador na partida
        jogadores_dados = obter_dados_jogadores(partida)  # Função existente
        
        for dados_jogador in jogadores_dados:
            # Testar CADA estratégia independentemente
            for criterios in todas_estrategias:
                aprovada, estrategia_nome, filtros_aprovados = avaliar_estrategia_independente(
                    dados_jogador, partida, criterios
                )
                
                if aprovada:
                    oportunidade = {
                        'partida_id': partida['event_id'],
                        'liga': partida['liga'],
                        'jogador': dados_jogador['nome'],
                        'oponente': dados_jogador['oponente'],
                        'placar': partida['placar'],
                        'fase_timing': partida['fase'],
                        'prioridade_timing': partida['prioridade'],
                        'tipo': dados_jogador['tipo'],
                        'ev': dados_jogador['ev'],
                        'momentum': dados_jogador['momentum_score'],
                        'double_faults': dados_jogador['double_faults'],
                        'win_1st_serve': dados_jogador['win_1st_serve'],
                        'estrategia': estrategia_nome,
                        'filtros_aprovados': filtros_aprovados
                    }
                    
                    oportunidades_por_estrategia[estrategia_nome].append(oportunidade)
    
    # Consolidar todas as oportunidades
    todas_oportunidades = []
    for estrategia, oportunidades in oportunidades_por_estrategia.items():
        todas_oportunidades.extend(oportunidades)
        if oportunidades:
            print(f"\\n✅ {estrategia}: {len(oportunidades)} oportunidades encontradas")
    
    print(f"\\n🎯 TOTAL: {len(todas_oportunidades)} oportunidades independentes")
    
    return todas_oportunidades
'''
    
    return funcao_processamento

def main():
    """Função principal"""
    print("🔧 === IMPLEMENTAÇÃO: ESTRATÉGIAS INDEPENDENTES ===")
    print("📅 Criando sistema para corrigir seleção_final.py")
    
    # 1. Criar critérios independentes
    criterios = aplicar_correcao_estrategias_independentes()
    
    # 2. Criar função de processamento independente  
    funcao = criar_funcao_processamento_independente()
    
    print("\\n✅ === SISTEMA INDEPENDENTE CRIADO! ===")
    print("\\n🎯 COMO FUNCIONA:")
    print("   1. Cada estratégia tem seus próprios critérios")
    print("   2. Uma estratégia rejeitada NÃO afeta as outras")
    print("   3. ALAVANCAGEM pode funcionar mesmo com MS baixo")
    print("   4. Várias estratégias podem aprovar a mesma partida")
    
    print("\\n📋 PRÓXIMOS PASSOS:")
    print("   1. Integrar este código no seleção_final.py")
    print("   2. Substituir função atual por processamento independente")
    print("   3. Testar para verificar se alavancagem funciona")
    
    print("\\n🚀 RESULTADO ESPERADO:")
    print("   • Sinais de alavancagem voltando a funcionar")
    print("   • Partidas com EV alto (>0.5) sendo aprovadas")
    print("   • Critérios relaxados para MS/W1S na alavancagem")
    
    return True

if __name__ == "__main__":
    main()
