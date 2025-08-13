"""
FILTRO DE TIMING RIGOROSO PARA TENNIS IQ

Sistema que filtra partidas baseado em timing e prioridade de entrada.
Só aprova partidas com prioridade ≥3 (2º set ou mais avançado).

PRIORIDADES:
- 5: 3º set (qualquer ponto) - EXCELENTE
- 4: 2º set meio/final (3-3+) - ÓTIMO  
- 3: 2º set início (0-0 até 2-2) - BOM (MÍNIMO ACEITO)
- 2: 1º set meio (3-3+) - POSSÍVEL (REJEITADO)
- 1: 1º set início (0-0 até 2-2) - CEDO (REJEITADO)
- 0: Tie-break/Match point - EVITAR (REJEITADO)
"""

import json
import requests
from datetime import datetime
import re

def buscar_partidas_ao_vivo():
    """Busca todas as partidas de tênis ao vivo."""
    try:
        url = "https://d.flashscore.com/x/feed/d_hh_1_8_pt_2_ebgkmz6e"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Referer': 'https://www.flashscore.pt/'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"❌ Erro HTTP: {response.status_code}")
            return []
            
        data = response.text
        
        # Buscar eventos em JSON
        eventos = []
        linhas = data.split('\n')
        
        for linha in linhas:
            if '"id":"' in linha and '"league":' in linha and '"home":' in linha:
                try:
                    evento_json = json.loads(linha)
                    if evento_json.get('sport_id') == 2:  # Tênis
                        eventos.append(evento_json)
                except:
                    continue
                    
        return eventos
        
    except Exception as e:
        print(f"❌ Erro ao buscar partidas: {e}")
        return []

def analisar_fase_jogo(placar_str):
    """
    Analisa a fase do jogo e retorna:
    - fase: Descrição textual da fase
    - entrada_segura: Se é seguro entrar neste momento
    - prioridade: Nível de prioridade (0-5)
    """
    
    if not placar_str or placar_str.strip() == '':
        return "Placar não disponível", False, 0
    
    placar = placar_str.strip()
    
    try:
        # Match terminado - EVITAR
        if any(keyword in placar.lower() for keyword in ['finished', 'finalizado', 'ended']):
            return "Partida finalizada", False, 0
        
        # Tie-break detectado - EVITAR (muito volátil)
        if '(' in placar and ')' in placar:
            return "Tie-break em andamento", False, 0
        
        # Match point - EVITAR (resultado pode sair a qualquer momento)
        if re.search(r'[56]-[56]', placar):
            # Verificar se há match point (um jogador com 6 e outro com 5)
            if '6-5' in placar or '5-6' in placar:
                return "Match point detectado", False, 0
        
        # Extrair sets do placar (formato: "6-4, 2-3" ou "6-4 2-3")
        sets = re.findall(r'(\d+)-(\d+)', placar)
        
        if not sets:
            return "Formato de placar inválido", False, 0
        
        num_sets = len(sets)
        set_atual = sets[-1]  # Último set (em andamento)
        games_p1, games_p2 = int(set_atual[0]), int(set_atual[1])
        
        # ===== ANÁLISE POR NÚMERO DE SETS =====
        
        if num_sets >= 3:
            # 3º SET OU MAIS - PRIORIDADE MÁXIMA
            return f"3º set: {games_p1}-{games_p2}", True, 5
            
        elif num_sets == 2:
            # 2º SET - AVALIAR PROGRESSO
            total_games = games_p1 + games_p2
            
            if total_games >= 6:  # 3-3 para cima
                return f"2º set meio/final: {games_p1}-{games_p2}", True, 4
            else:  # 0-0 até 2-2
                return f"2º set início: {games_p1}-{games_p2}", True, 3
                
        elif num_sets == 1:
            # 1º SET - GERALMENTE CEDO DEMAIS
            total_games = games_p1 + games_p2
            
            if total_games >= 6:  # 3-3 para cima
                return f"1º set meio: {games_p1}-{games_p2}", False, 2
            else:  # 0-0 até 2-2
                return f"1º set início: {games_p1}-{games_p2}", False, 1
        
        else:
            return "Início da partida", False, 1
            
    except Exception as e:
        return f"Erro na análise: {str(e)}", False, 0

def filtrar_partidas_por_timing():
    """
    FILTRO DE TIMING RIGOROSO - Só aprova partidas com prioridade ≥3 (2º set ou mais).
    """
    
    print("🔴 FILTRO DE TIMING RIGOROSO ATIVADO")
    print("=" * 60)
    
    # Buscar eventos ao vivo
    eventos_ao_vivo = buscar_partidas_ao_vivo()
    
    if not eventos_ao_vivo:
        print("❌ Nenhuma partida ao vivo encontrada no momento.")
        return []
    
    partidas_filtradas = []
    
    print(f"🎾 TOTAL DE PARTIDAS ENCONTRADAS: {len(eventos_ao_vivo)}")
    print(f"📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("")
    print("🔴 FILTRO RIGOROSO: Só aprova prioridade ≥3")
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
        
        # ANÁLISE RIGOROSA DE TIMING - USAR VALORES REAIS
        fase, entrada_segura, prioridade = analisar_fase_jogo(ss_basico)
        
        # Criar objeto da partida
        partida_info = {
            'id': evento_id,
            'liga': liga,
            'jogador_casa': jogador_casa,
            'jogador_visitante': jogador_visitante,
            'placar': ss_basico,
            'fase': fase,
            'entrada_segura': entrada_segura,
            'prioridade': prioridade,
            'evento_completo': evento
        }
        
        # FILTRO RIGOROSO - SÓ APROVA PRIORIDADE ≥3
        if entrada_segura and prioridade >= 3:
            emoji = "🟢"  # Verde - Aprovado  
            status = "APROVADO"
            incluir_partida = True
        else:
            emoji = "🔴"  # Vermelho - Rejeitado
            status = f"REJEITADO (Prio {prioridade})"
            incluir_partida = False
        
        print(f"{emoji} PARTIDA {i} - {status}")
        print(f"   ID: {evento_id}")
        print(f"   🏟️  Liga: {liga}")
        print(f"   👤 {jogador_casa} vs {jogador_visitante}")
        print(f"   🎯 Games: {ss_basico}")
        print(f"   ⏱️  Fase: {fase}")
        print(f"   📊 Prioridade: {prioridade}/5 | Segura: {'✅' if entrada_segura else '❌'}")
        
        # INCLUIR APENAS SE APROVADO
        if incluir_partida:
            partidas_filtradas.append(partida_info)
            print(f"   ✅ INCLUÍDA")
        else:
            print(f"   ❌ REJEITADA - Timing insuficiente")
        
        print("-" * 60)
    
    # Resumo
    print("\n" + "=" * 80)
    print("📊 RESUMO DO FILTRO DE TIMING RIGOROSO")
    print("=" * 80)
    print(f"🎾 Total de partidas analisadas: {len(eventos_ao_vivo)}")
    print(f"🟢 Partidas aprovadas (prioridade ≥3): {len(partidas_filtradas)}")
    print(f"❌ Partidas rejeitadas: {len(eventos_ao_vivo) - len(partidas_filtradas)}")
    
    # Ordenar por prioridade (decrescente)
    partidas_filtradas.sort(key=lambda x: x['prioridade'], reverse=True)
    
    if partidas_filtradas:
        print("\n🎯 PARTIDAS APROVADAS (ordenadas por prioridade):")
        print("=" * 50)
        
        for i, partida in enumerate(partidas_filtradas[:10], 1):
            emoji_prio = "🟢" if partida['prioridade'] >= 4 else "🔵"
            print(f"{emoji_prio} {i}. {partida['jogador_casa']} vs {partida['jogador_visitante']}")
            print(f"      Prioridade: {partida['prioridade']}/5 | Fase: {partida['fase']}")
    
    print(f"\n🕐 Última atualização: {datetime.now().strftime('%H:%M:%S')}")
    print("🔴 FILTRO RIGOROSO ATIVO - Apenas prioridade ≥3")
    
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
    print("🟡 BOM (Prioridade 3) - MÍNIMO ACEITO:")
    print("   • 2º set - início (0x0 até 2x2)")
    print("   • ✅ Já temos dados do 1º set para análise")
    print("")
    print("🟠 POSSÍVEL (Prioridade 2) - REJEITADO:")
    print("   • 1º set - meio (3x3 até 5x5)")
    print("   • ❌ Filtro rigoroso, preferimos mais dados")
    print("")
    print("🔴 EVITAR (Prioridade 0-1):")
    print("   • 1º set início (0x0 até 2x2)")
    print("   • Tie-breaks (6x6)")
    print("   • Match points")
    print("   • Padrão tático ainda não claro")

if __name__ == "__main__":
    print("🎾 SISTEMA DE FILTRO DE TIMING - TENNIS IQ")
    print("=" * 50)
    
    explicar_criterios()
    print("\n" + "=" * 50)
    
    partidas = filtrar_partidas_por_timing()
    
    if partidas:
        print(f"\n✅ {len(partidas)} partidas aprovadas para análise!")
    else:
        print("\n❌ Nenhuma partida aprovada no momento.")
        print("🔄 Aguarde partidas entrarem no 2º set ou mais.")
