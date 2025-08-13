import requests
import json
import time
from datetime import datetime
import sys
import os

# Adicionar o diretório dados ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'dados'))

def buscar_partidas_ao_vivo():
    """Busca todas as partidas de tênis ao vivo."""
    url = "https://api.b365api.com/v3/events/inplay"
    params = {
        'sport_id': 13,  # Tennis
        'token': '226997-BVn3XP4cGLAUfL'
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data['success']:
            return data['results']
        else:
            print(f"❌ API Erro: {data}")
            return []
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro na requisição: {e}")
        return []
    except ValueError as e:
        print(f"❌ Erro no JSON: {e}")
        return []

def analisar_fase_jogo(ss_data):
    """
    Analisa a fase do jogo baseado no placar (ss) e retorna classificação de timing.
    
    Retorna:
    - fase: string identificando a fase
    - entrada_segura: boolean se é seguro entrar
    - prioridade: int (1=baixa, 5=excelente)
    """
    
    if not ss_data or ss_data == 'N/A':
        return "sem_dados", False, 0
    
    try:
        # Analisar o placar atual
        if ',' in ss_data:
            sets = ss_data.split(',')
        else:
            sets = [ss_data]
        
        sets = [s.strip() for s in sets]
        num_sets = len(sets)
        
        # Analisar último set (atual)
        ultimo_set = sets[-1]
        if '-' in ultimo_set:
            games_a, games_b = map(int, ultimo_set.split('-'))
        else:
            return "formato_invalido", False, 0
        
        # Determinar qual set estamos
        sets_completos = num_sets - 1
        
        # Verificar se é tie-break (6-6 ou 7-6)
        if (games_a == 6 and games_b == 6) or (games_a == 7 and games_b == 6) or (games_a == 6 and games_b == 7):
            return "tiebreak", False, 0
        
        # Verificar match point
        if ((games_a >= 6 or games_b >= 6) and abs(games_a - games_b) >= 1):
            # Se alguém tem 6+ e diferença de 1+, pode ser match point
            if sets_completos >= 1:  # 2º set ou mais
                return "possivel_matchpoint", False, 0
        
        # Análise por set
        if sets_completos == 0:  # 1º set
            total_games = games_a + games_b
            
            if total_games <= 4:  # 0x0 até 2x2
                return "1set_early", False, 1
            elif total_games <= 10:  # 3x3 até 5x5
                return "1set_mid", True, 2
            else:  # 6x6+
                return "1set_late", False, 1
                
        elif sets_completos == 1:  # 2º set
            total_games = games_a + games_b
            
            if total_games <= 4:  # 0x0 até 2x2
                return "2set_early", True, 3
            elif total_games <= 10:  # 3x3 até 5x5
                return "2set_mid", True, 4
            else:  # 6x6+
                return "2set_late", True, 3
                
        elif sets_completos == 2:  # 3º set
            total_games = games_a + games_b
            
            if total_games <= 10:  # Qualquer ponto equilibrado
                return "3set_mid", True, 5
            else:
                return "3set_late", True, 4
        
        else:  # Sets extras (improvável no tênis)
            return "set_extra", True, 3
            
    except Exception as e:
        return "erro_analise", False, 0

def filtrar_partidas_por_timing():
    """
    TIMING LIBERADO 24H - Retorna todas as partidas sem filtro de timing.
    """
    
    print("🟢 FILTRO DE TIMING DESABILITADO - 24H LIBERADO")
    print("=" * 60)
    
    # Buscar eventos ao vivo
    eventos_ao_vivo = buscar_partidas_ao_vivo()
    
    if not eventos_ao_vivo:
        print("❌ Nenhuma partida ao vivo encontrada no momento.")
        return []
    
    partidas_filtradas = []
    
    print(f"🔴 TOTAL DE PARTIDAS ENCONTRADAS: {len(eventos_ao_vivo)}")
    print(f"📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("")
    print("🟢 APROVANDO TODAS AS PARTIDAS - SEM RESTRIÇÃO DE TIMING...")
    print("=" * 80)
    
    for i, evento in enumerate(eventos_ao_vivo, 1):
        # Extrair informações básicas
        evento_id = evento.get('id', 'N/A')
        liga = evento.get('league', {}).get('name', 'Liga não informada')
        
        # Jogadores
        jogador_casa = evento.get('home', {}).get('name', 'Jogador 1')
        jogador_visitante = evento.get('away', {}).get('name', 'Jogador 2')
        
        # Placar básico do evento principal
        ss_basico = evento.get('ss', '')
        
        # APROVAÇÃO AUTOMÁTICA - SEM ANÁLISE DE TIMING
        fase, entrada_segura, prioridade = analisar_fase_jogo(ss_basico)
        
        # Criar objeto da partida
        partida_info = {
            'id': evento_id,
            'liga': liga,
            'jogador_casa': jogador_casa,
            'jogador_visitante': jogador_visitante,
            'placar': ss_basico,
            'fase': fase,
            'entrada_segura': True,  # SEMPRE SEGURA
            'prioridade': 5,  # SEMPRE MÁXIMA PRIORIDADE
            'evento_completo': evento
        }
        
        # SEMPRE APROVADO - 24H LIBERADO
        emoji = "🟢"  # Verde - Sempre aprovado
        status = "APROVADO 24H"
        
        print(f"{emoji} PARTIDA {i} - {status}")
        print(f"   ID: {evento_id}")
        print(f"   🏟️  Liga: {liga}")
        print(f"   👤 {jogador_casa} vs {jogador_visitante}")
        print(f"   🎯 Games: {ss_basico}")
        print(f"   ⏱️  Fase: {fase}")
        print(f"   📊 Prioridade: 5/5 (LIBERADO)")
        
        # SEMPRE INCLUIR - SEM FILTRO
        partidas_filtradas.append(partida_info)
        print(f"   ✅ INCLUÍDA AUTOMATICAMENTE")
        
        print("-" * 60)
    
    # Resumo
    print("\n" + "=" * 80)
    print("📊 RESUMO DO FILTRO DE TIMING - 24H LIBERADO")
    print("=" * 80)
    print(f"✅ Total de partidas analisadas: {len(eventos_ao_vivo)}")
    print(f"🟢 Partidas aprovadas automaticamente: {len(partidas_filtradas)}")
    print(f"❌ Partidas rejeitadas: 0 (TODAS APROVADAS)")
    
    # Classificar por ID (já que não há mais prioridade real)
    partidas_filtradas.sort(key=lambda x: x['id'])
    
    if partidas_filtradas:
        print("\n� TODAS AS PARTIDAS LIBERADAS PARA ANÁLISE:")
        print("=" * 50)
        
        for i, partida in enumerate(partidas_filtradas[:10], 1):  # Top 10
            emoji_prio = "🟢"  # Sempre verde
            print(f"{emoji_prio} {i}. {partida['jogador_casa']} vs {partida['jogador_visitante']}")
            print(f"      Placar: {partida['placar']} | Fase: {partida['fase']} | Status: LIBERADO 24H")
    
    print(f"\n🕐 Última atualização: {datetime.now().strftime('%H:%M:%S')}")
    print("🟢 SISTEMA LIBERADO 24 HORAS - SEM RESTRIÇÕES DE TIMING")
    
    return partidas_filtradas

def explicar_criterios():
    """Explica os critérios de timing usados no filtro."""
    
    print("\n📚 CRITÉRIOS DE TIMING PARA ENTRADA SEGURA")
    print("=" * 60)
    print("🟢 EXCELENTE (Prioridade 5):")
    print("   • 3º set - qualquer ponto equilibrado")
    print("   • Fase decisiva, dominância técnica se destaca")
    print("")
    print("🔵 ÓTIMO (Prioridade 4):")
    print("   • 2º set - meio (3x3 a 5x5)")
    print("   • Odds estabilizadas, jogadores testados")
    print("")
    print("🟡 BOM (Prioridade 3) - AGORA REJEITADO:")
    print("   • 2º set - início (0x0 até 2x2)")
    print("   • ❌ Filtro muito rigoroso, preferimos mais dados")
    print("")
    print("🟠 POSSÍVEL (Prioridade 2) - REJEITADO:")
    print("   • 1º set - meio (3x3 até 5x5)")
    print("   • ❌ Filtro muito rigoroso, preferimos mais dados")
    print("")
    print("🔴 EVITAR (Prioridade 0-1):")
    print("   • 1º set início (0x0 até 2x2)")
    print("   • Tie-breaks (6x6)")
    print("   • Match points")
    print("   • Padrão tático ainda não claro")

if __name__ == "__main__":
    filtrar_partidas_por_timing()