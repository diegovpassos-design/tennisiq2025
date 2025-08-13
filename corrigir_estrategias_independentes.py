#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 CORREÇÃO: ESTRATÉGIAS INDEPENDENTES
============================================================
Separa as estratégias para que cada uma opere com seu    
    return oportunidades_por_estrategia
    """
    
    return estrategias_config

def main():
    """Função principal"""rios critérios, sem misturar filtros
"""

def criar_sistema_estrategias_independentes():
    """Cria sistema onde cada estratégia opera independentemente"""
    
    estrategias_config = """
# 🎯 SISTEMA DE ESTRATÉGIAS INDEPENDENTES
# ============================================================
# Cada estratégia tem seus próprios critérios e não interfere nas outras

# 🚀 ESTRATÉGIA ALAVANCAGEM - Para EVs muito altos
CRITERIOS_ALAVANCAGEM = {
    'EV_MINIMO': 0.5,             # EVs altos (0.5+)
    'EV_MAXIMO': 50.0,            # Sem limite superior
    'MOMENTUM_SCORE_MINIMO': 40,  # MS ≥ 40% (relaxado)
    'WIN_1ST_SERVE_MINIMO': 50,   # W1S ≥ 50% (relaxado)
    'DOUBLE_FAULTS_MAXIMO': 8,    # DF ≤ 8 (relaxado)
    'PRIORIDADE_MINIMA': 2,       # Prioridade ≥ 2 (relaxado)
    'FASE_PERMITIDA': ['2set_mid', '2set_late', '3set_early', '3set_mid', '3set_late'],
    'NOME': 'ALAVANCAGEM'
}

# 🧠 ESTRATÉGIA VANTAGEM MENTAL - Para situações psicológicas
CRITERIOS_VANTAGEM_MENTAL = {
    'EV_MINIMO': 0.15,            # EV moderado
    'EV_MAXIMO': 2.0,             # Limite moderado
    'MOMENTUM_SCORE_MINIMO': 60,  # MS ≥ 60% (importante para mental)
    'WIN_1ST_SERVE_MINIMO': 60,   # W1S ≥ 60% (importante para mental)
    'DOUBLE_FAULTS_MAXIMO': 4,    # DF ≤ 4 (rigoroso para mental)
    'PRIORIDADE_MINIMA': 3,       # Prioridade ≥ 3
    'FASE_PERMITIDA': ['2set_early', '2set_mid', '3set_early', '3set_mid'],
    'NOME': 'VANTAGEM_MENTAL'
}

# 🔄 ESTRATÉGIA INVERTIDA - Para fadiga e 3º sets
CRITERIOS_INVERTIDOS = {
    'EV_MINIMO': 0.1,             # EV baixo (situações especiais)
    'EV_MAXIMO': 3.0,             # Permite EVs altos
    'MOMENTUM_SCORE_MINIMO': 45,  # MS ≥ 45% (muito relaxado)
    'WIN_1ST_SERVE_MINIMO': 45,   # W1S ≥ 45% (muito relaxado)
    'DOUBLE_FAULTS_MAXIMO': 6,    # DF ≤ 6 (relaxado)
    'PRIORIDADE_MINIMA': 2,       # Prioridade ≥ 2
    'FASE_PERMITIDA': ['3set_mid', '3set_late', '2set_late'],
    'NOME': 'INVERTIDA'
}

# 📊 ESTRATÉGIA CONSERVADORA - Para situações estáveis
CRITERIOS_CONSERVADORES = {
    'EV_MINIMO': 0.2,             # EV moderado-alto
    'EV_MAXIMO': 1.0,             # Limite conservador
    'MOMENTUM_SCORE_MINIMO': 70,  # MS ≥ 70% (rigoroso)
    'WIN_1ST_SERVE_MINIMO': 70,   # W1S ≥ 70% (rigoroso)
    'DOUBLE_FAULTS_MAXIMO': 3,    # DF ≤ 3 (muito rigoroso)
    'PRIORIDADE_MINIMA': 4,       # Prioridade ≥ 4 (alta)
    'FASE_PERMITIDA': ['1set_late', '2set_early', '2set_mid'],
    'NOME': 'CONSERVADORA'
}

def avaliar_oportunidade_por_estrategia(dados_jogador, partida, criterios, estrategia_nome):
    \"\"\"Avalia uma oportunidade específica para uma estratégia específica\"\"\"
    
    filtros_aprovados = []
    filtros_rejeitados = []
    
    # Filtro EV
    if criterios['EV_MINIMO'] <= dados_jogador['ev'] <= criterios['EV_MAXIMO']:
        filtros_aprovados.append(f"EV: {dados_jogador['ev']:.3f} ✅ ({estrategia_nome})")
    else:
        filtros_rejeitados.append(f"EV: {dados_jogador['ev']:.3f} ❌ ({estrategia_nome}: {criterios['EV_MINIMO']}-{criterios['EV_MAXIMO']})")
    
    # Filtro Momentum Score
    if dados_jogador['momentum_score'] >= criterios['MOMENTUM_SCORE_MINIMO']:
        filtros_aprovados.append(f"MS: {dados_jogador['momentum_score']:.1f}% ✅ ({estrategia_nome})")
    else:
        filtros_rejeitados.append(f"MS: {dados_jogador['momentum_score']:.1f}% ❌ ({estrategia_nome}: min {criterios['MOMENTUM_SCORE_MINIMO']}%)")
    
    # Filtro Double Faults
    try:
        df_value = int(dados_jogador['double_faults']) if dados_jogador['double_faults'] else 0
        if 0 <= df_value <= criterios['DOUBLE_FAULTS_MAXIMO']:
            filtros_aprovados.append(f"DF: {df_value} ✅ ({estrategia_nome})")
        else:
            filtros_rejeitados.append(f"DF: {df_value} ❌ ({estrategia_nome}: max {criterios['DOUBLE_FAULTS_MAXIMO']})")
    except (ValueError, TypeError):
        filtros_rejeitados.append(f"DF: dados inválidos ❌ ({estrategia_nome})")
    
    # Filtro Win 1st Serve
    try:
        w1s_value = float(dados_jogador['win_1st_serve']) if dados_jogador['win_1st_serve'] else 0
        if w1s_value >= criterios['WIN_1ST_SERVE_MINIMO']:
            filtros_aprovados.append(f"W1S: {w1s_value}% ✅ ({estrategia_nome})")
        else:
            filtros_rejeitados.append(f"W1S: {w1s_value}% ❌ ({estrategia_nome}: min {criterios['WIN_1ST_SERVE_MINIMO']}%)")
    except (ValueError, TypeError):
        filtros_rejeitados.append(f"W1S: dados inválidos ❌ ({estrategia_nome})")
    
    # Filtro Fase da Partida
    fase_partida = partida.get('fase', '')
    if fase_partida in criterios['FASE_PERMITIDA']:
        filtros_aprovados.append(f"Fase: {fase_partida} ✅ ({estrategia_nome})")
    else:
        filtros_rejeitados.append(f"Fase: {fase_partida} ❌ ({estrategia_nome}: permitido {criterios['FASE_PERMITIDA']})")
    
    # Filtro Prioridade
    prioridade = partida.get('prioridade', 0)
    if prioridade >= criterios['PRIORIDADE_MINIMA']:
        filtros_aprovados.append(f"Prioridade: {prioridade}/5 ✅ ({estrategia_nome})")
    else:
        filtros_rejeitados.append(f"Prioridade: {prioridade}/5 ❌ ({estrategia_nome}: min {criterios['PRIORIDADE_MINIMA']})")
    
    # Estratégia aprovada se TODOS os filtros passaram
    aprovada = len(filtros_rejeitados) == 0
    
    return {
        'aprovada': aprovada,
        'estrategia': estrategia_nome,
        'filtros_aprovados': filtros_aprovados,
        'filtros_rejeitados': filtros_rejeitados,
        'criterios_usados': criterios
    }

def processar_oportunidades_independentes(partidas_timing):
    \"\"\"Processa oportunidades testando CADA estratégia independentemente\"\"\"
    
    todas_estrategias = [
        CRITERIOS_ALAVANCAGEM,
        CRITERIOS_VANTAGEM_MENTAL, 
        CRITERIOS_INVERTIDOS,
        CRITERIOS_CONSERVADORES
    ]
    
    oportunidades_por_estrategia = {
        'ALAVANCAGEM': [],
        'VANTAGEM_MENTAL': [],
        'INVERTIDA': [],
        'CONSERVADORA': []
    }
    
    print("\\n🎯 === PROCESSAMENTO INDEPENDENTE DE ESTRATÉGIAS ===")
    print("=" * 80)
    
    for partida in partidas_timing:
        event_id = partida['event_id']
        print(f"\\n🔍 Analisando partida {event_id}: {partida['jogador1']} vs {partida['jogador2']}")
        
        # Simular dados dos jogadores (em produção, viria da análise real)
        jogadores_dados = [
            {
                'nome': partida['jogador1'],
                'oponente': partida['jogador2'],
                'tipo': 'casa',
                'ev': 0.8,  # Exemplo: EV alto para testar alavancagem
                'momentum_score': 55,  # Exemplo: MS moderado
                'double_faults': 3,    # Exemplo: DF baixo
                'win_1st_serve': 65    # Exemplo: W1S bom
            },
            {
                'nome': partida['jogador2'],
                'oponente': partida['jogador1'],
                'tipo': 'visitante',
                'ev': 0.25,  # Exemplo: EV moderado para testar outras estratégias
                'momentum_score': 72,  # Exemplo: MS alto
                'double_faults': 2,    # Exemplo: DF muito baixo
                'win_1st_serve': 78    # Exemplo: W1S muito bom
            }
        ]
        
        # Testar CADA jogador em CADA estratégia
        for jogador_dados in jogadores_dados:
            for criterios in todas_estrategias:
                estrategia_nome = criterios['NOME']
                
                # Avaliar esta combinação jogador+estratégia
                resultado = avaliar_oportunidade_por_estrategia(
                    jogador_dados, partida, criterios, estrategia_nome
                )
                
                if resultado['aprovada']:
                    oportunidade = {
                        'partida_id': event_id,
                        'liga': partida['liga'],
                        'jogador': jogador_dados['nome'],
                        'oponente': jogador_dados['oponente'],
                        'placar': partida['placar'],
                        'fase_timing': partida['fase'],
                        'prioridade_timing': partida['prioridade'],
                        'tipo': jogador_dados['tipo'],
                        'ev': jogador_dados['ev'],
                        'momentum': jogador_dados['momentum_score'],
                        'double_faults': jogador_dados['double_faults'],
                        'win_1st_serve': jogador_dados['win_1st_serve'],
                        'estrategia': estrategia_nome,
                        'filtros_aprovados': resultado['filtros_aprovados']
                    }
                    
                    oportunidades_por_estrategia[estrategia_nome].append(oportunidade)
                    
                    print(f"   ✅ {estrategia_nome}: {jogador_dados['nome']} APROVADO!")
                    print(f"      Filtros: {', '.join(resultado['filtros_aprovados'])}")
                else:
                    print(f"   ❌ {estrategia_nome}: {jogador_dados['nome']} rejeitado")
                    print(f"      Motivos: {', '.join(resultado['filtros_rejeitados'][:2])}...")  # Mostrar só primeiros 2
    
    return oportunidades_por_estrategia
    \"\"\"
    
    return estrategias_config

def main():
    """Função principal"""
    print("🔧 === CORREÇÃO: ESTRATÉGIAS INDEPENDENTES ===")
    print("📅 Criando sistema onde cada estratégia opera independentemente")
    
    config = criar_sistema_estrategias_independentes()
    
    print("\\n✅ Sistema criado com 4 estratégias independentes:")
    print("   🚀 ALAVANCAGEM - EVs altos (0.5+), critérios relaxados")
    print("   🧠 VANTAGEM MENTAL - EVs moderados, critérios psicológicos")  
    print("   🔄 INVERTIDA - 3º sets, critérios muito relaxados")
    print("   📊 CONSERVADORA - EVs moderados, critérios rigorosos")
    
    print("\\n🎯 VANTAGENS:")
    print("   • Cada estratégia tem seus próprios filtros")
    print("   • Uma estratégia rejeitada NÃO afeta as outras")
    print("   • Permite encontrar oportunidades em diferentes cenários")
    print("   • Alavancagem pode funcionar mesmo com MS baixo")
    
    print("\\n📋 PRÓXIMO PASSO:")
    print("   Implementar esta lógica no seleção_final.py")
    
    return config

if __name__ == "__main__":
    main()
