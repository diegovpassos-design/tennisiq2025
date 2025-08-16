import requests
import json
import time
from datetime import datetime
import sys
import os

# Adicionar o diretório dados ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'dados'))
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Importar funções dos módulos - corrigido para nova estrutura
from .seleção_time import filtrar_partidas_por_timing

# Importar dashboard logger
try:
    import sys
    import os
    # Corrigir import para nova estrutura - usar import absoluto
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    from backend.services.dashboard_logger import dashboard_logger
    DASHBOARD_DISPONIVEL = True
    print("✅ Dashboard logger importado com sucesso")
except ImportError as e:
    DASHBOARD_DISPONIVEL = False
    print(f"❌ Erro ao importar dashboard logger: {e}")

# Importar logger formatado
try:
    from ...utils.logger_formatado import logger_formatado
    LOGGER_FORMATADO_DISPONIVEL = True
except ImportError:
    try:
        # Fallback para import absoluto
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
        from backend.utils.logger_formatado import logger_formatado
        LOGGER_FORMATADO_DISPONIVEL = True
    except ImportError:
        LOGGER_FORMATADO_DISPONIVEL = False

# Variáveis globais para dados das partidas (para integração com logger)
partidas_timing_dados = []
partidas_analisadas_dados = []

def get_dados_partidas_para_logger():
    """Retorna dados das partidas para o logger formatado"""
    return {
        'total_partidas': len(partidas_analisadas_dados),
        'aprovadas_timing': len(partidas_timing_dados),
        'partidas_timing': partidas_timing_dados,
        'partidas_analisadas': partidas_analisadas_dados
    }

def limpar_dados_partidas():
    """Limpa os dados das partidas para novo ciclo"""
    global partidas_timing_dados, partidas_analisadas_dados
    partidas_timing_dados = []
    partidas_analisadas_dados = []

def buscar_odds_evento(event_id, api_key, base_url):
    """Busca as odds de um evento específico com múltiplas estratégias."""
    url = f"{base_url}/v3/event/odds"
    params = {
        'event_id': event_id,
        'token': api_key
    }
    
    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        if data.get('success') == 1 and 'results' in data:
            results = data['results']
            
            if 'odds' in results and results['odds']:
                odds_data = results['odds']
                
                # Estratégia 1: Tentar 13_1 (main market)
                if '13_1' in odds_data and odds_data['13_1']:
                    latest_odds = odds_data['13_1'][0]
                    
                    if 'home_od' in latest_odds and 'away_od' in latest_odds:
                        home_odd = latest_odds.get('home_od', '-')
                        away_odd = latest_odds.get('away_od', '-')
                        
                        # Verificar se são valores válidos
                        if home_odd != '-' and away_odd != '-':
                            try:
                                float(home_odd)
                                float(away_odd)
                                return {
                                    'jogador1_odd': home_odd,
                                    'jogador2_odd': away_odd
                                }
                            except ValueError:
                                print(f"⚠️ Odds inválidas (13_1): Casa={home_odd}, Visitante={away_odd}")
                
                # Estratégia 2: Tentar outros mercados
                for market_id in ['1', '18', '2', '3']:
                    if market_id in odds_data and odds_data[market_id]:
                        try:
                            market_odds = odds_data[market_id][0]
                            home_odd = market_odds.get('home_od', '-')
                            away_odd = market_odds.get('away_od', '-')
                            
                            if home_odd != '-' and away_odd != '-':
                                float(home_odd)
                                float(away_odd)
                                return {
                                    'jogador1_odd': home_odd,
                                    'jogador2_odd': away_odd
                                }
                        except (ValueError, IndexError, KeyError):
                            continue
        
        return {'jogador1_odd': 'N/A', 'jogador2_odd': 'N/A'}
        
    except Exception as e:
        print(f"❌ Erro ao buscar odds do evento {event_id}: {e}")
        return {'jogador1_odd': 'N/A', 'jogador2_odd': 'N/A'}

def buscar_stats_detalhadas(event_id, api_key, base_url):
    """Busca estatísticas detalhadas do evento (baseado em ev.py)."""
    url = f"{base_url}/v3/event/view"
    params = {
        'event_id': event_id,
        'token': api_key
    }
    
    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        if data.get('success') == 1 and 'results' in data:
            results = data['results']
            if results and len(results) > 0:
                event_data = results[0]
                
                # Extrair estatísticas
                stats = event_data.get('stats', {})
                
                # Calcular momentum score baseado em estatísticas reais
                jogador1_ms = 50
                jogador2_ms = 50
                
                if stats:
                    momentum_factors = []
                    
                    # Aces (peso: 10)
                    if 'aces' in stats and len(stats['aces']) >= 2:
                        try:
                            aces1 = int(stats['aces'][0])
                            aces2 = int(stats['aces'][1])
                            if aces1 + aces2 > 0:
                                momentum_factors.append((aces1, aces2, 10))
                        except:
                            pass
                    
                    # Win 1st serve % (peso: 15)
                    if 'win_1st_serve' in stats and len(stats['win_1st_serve']) >= 2:
                        try:
                            serve1 = int(stats['win_1st_serve'][0])
                            serve2 = int(stats['win_1st_serve'][1])
                            momentum_factors.append((serve1, serve2, 15))
                        except:
                            pass
                    
                    # Break point conversions % (peso: 20)
                    if 'break_point_conversions' in stats and len(stats['break_point_conversions']) >= 2:
                        try:
                            bp1 = int(stats['break_point_conversions'][0])
                            bp2 = int(stats['break_point_conversions'][1])
                            momentum_factors.append((bp1, bp2, 20))
                        except:
                            pass
                    
                    # Calcular momentum ponderado
                    if momentum_factors:
                        total_weighted_score1 = 0
                        total_weighted_score2 = 0
                        total_weight = 0
                        
                        for stat1, stat2, weight in momentum_factors:
                            total_weighted_score1 += stat1 * weight
                            total_weighted_score2 += stat2 * weight
                            total_weight += weight
                        
                        if total_weight > 0:
                            total_score = total_weighted_score1 + total_weighted_score2
                            if total_score > 0:
                                jogador1_ms = round((total_weighted_score1 / total_score) * 100)
                                jogador2_ms = 100 - jogador1_ms
                
                # Extrair double faults
                df1 = 0
                df2 = 0
                if 'double_faults' in stats and len(stats['double_faults']) >= 2:
                    try:
                        df1 = int(stats['double_faults'][0])
                        df2 = int(stats['double_faults'][1])
                    except:
                        pass
                
                # Extrair win 1st serve %
                w1s1 = 0
                w1s2 = 0
                if 'win_1st_serve' in stats and len(stats['win_1st_serve']) >= 2:
                    try:
                        w1s1 = int(stats['win_1st_serve'][0])
                        w1s2 = int(stats['win_1st_serve'][1])
                    except:
                        pass
                
                return {
                    'jogador1_ms': str(jogador1_ms),
                    'jogador2_ms': str(jogador2_ms),
                    'jogador1_df': str(df1),
                    'jogador2_df': str(df2),
                    'jogador1_w1s': str(w1s1),
                    'jogador2_w1s': str(w1s2),
                    'stats_detalhadas': stats
                }
        
        return {
            'jogador1_ms': '50',
            'jogador2_ms': '50',
            'jogador1_df': '0',
            'jogador2_df': '0',
            'jogador1_w1s': '0',
            'jogador2_w1s': '0',
            'stats_detalhadas': {}
        }
        
    except Exception as e:
        return {
            'jogador1_ms': '50',
            'jogador2_ms': '50',
            'jogador1_df': '0',
            'jogador2_df': '0',
            'jogador1_w1s': '0',
            'jogador2_w1s': '0',
            'stats_detalhadas': {}
        }

def buscar_dados_jogador(jogador_nome, event_id):
    """Busca dados individuais do jogador usando a mesma lógica do ev.py."""
    
    dados_jogador = {
        'momentum_score': 50,
        'double_faults': 0,
        'win_1st_serve': 0,
        'ev': 0
    }
    
    try:
        # Configurações da API - corrigir caminho para backend/config/config.json
        config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'config.json')
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        api_key = config.get('api_key')
        base_url = config.get('api_base_url', 'https://api.b365api.com')
        
        if not api_key:
            return dados_jogador
        
        # Buscar odds usando a função do ev.py
        odds_info = buscar_odds_evento(event_id, api_key, base_url)
        
        # Buscar estatísticas usando a função do ev.py  
        stats_info = buscar_stats_detalhadas(event_id, api_key, base_url)
        
        # Determinar se é HOME ou AWAY
        url_inplay = f"{base_url}/v3/events/inplay"
        params = {'token': api_key, 'sport_id': 13}
        response = requests.get(url_inplay, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success') == 1 and 'results' in data:
                for evento in data['results']:
                    if str(evento.get('id')) == str(event_id):
                        jogador_casa = evento.get('home', {}).get('name', '')
                        jogador_visitante = evento.get('away', {}).get('name', '')
                        
                        is_home = jogador_nome in jogador_casa or jogador_casa in jogador_nome
                        
                        if is_home:
                            # Dados do jogador HOME (usando formato do partidas.py)
                            dados_jogador['momentum_score'] = float(stats_info['jogador1_ms'])
                            dados_jogador['double_faults'] = int(stats_info['jogador1_df'])
                            dados_jogador['win_1st_serve'] = int(stats_info['jogador1_w1s'])
                            
                            # Calcular EV para HOME (usando mesma lógica do ev.py)
                            if odds_info['jogador1_odd'] != 'N/A' and odds_info['jogador1_odd'] != '-':
                                try:
                                    odd1 = float(odds_info['jogador1_odd'])
                                    ms1 = float(stats_info['jogador1_ms'])
                                    dados_jogador['ev'] = calcular_ev(ms1, odd1)
                                except:
                                    dados_jogador['ev'] = 0
                        else:
                            # Dados do jogador AWAY (usando formato do partidas.py)
                            dados_jogador['momentum_score'] = float(stats_info['jogador2_ms'])
                            dados_jogador['double_faults'] = int(stats_info['jogador2_df'])
                            dados_jogador['win_1st_serve'] = int(stats_info['jogador2_w1s'])
                            
                            # Calcular EV para AWAY (usando mesma lógica do ev.py)
                            if odds_info['jogador2_odd'] != 'N/A' and odds_info['jogador2_odd'] != '-':
                                try:
                                    odd2 = float(odds_info['jogador2_odd'])
                                    ms2 = float(stats_info['jogador2_ms'])
                                    dados_jogador['ev'] = calcular_ev(ms2, odd2)
                                except:
                                    dados_jogador['ev'] = 0
                        break
    
    except Exception as e:
        print(f"⚠️ Erro ao buscar dados do jogador {jogador_nome}: {e}")
    
    return dados_jogador

def calcular_ev(momentum_score, odd):
    """Calcula o Expected Value (EV)."""
    
    try:
        if not odd or odd <= 1:
            return 0
        
        # Converter momentum em probabilidade (0-1)
        probabilidade = momentum_score / 100
        
        # Fórmula EV: (probabilidade × odd) - 1
        ev = (probabilidade * odd) - 1
        
        return ev
    
    except Exception:
        return 0

def buscar_odds_partida_atual(event_id):
    """Busca as odds atuais de uma partida específica"""
    try:
        # Configurações da API
        config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'config.json')
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        api_key = config.get('api_key')
        base_url = config.get('api_base_url', 'https://api.b365api.com')
        
        if not api_key:
            return {'casa': 'N/A', 'visitante': 'N/A'}
        
        # Buscar odds usando a função existente
        odds_info = buscar_odds_evento(event_id, api_key, base_url)
        
        return {
            'casa': odds_info.get('jogador1_odd', 'N/A'),
            'visitante': odds_info.get('jogador2_odd', 'N/A')
        }
    except Exception as e:
        print(f"⚠️ Erro ao buscar odds da partida {event_id}: {e}")
        return {'casa': 'N/A', 'visitante': 'N/A'}

def testar_estrategia_virada_mental(partida, dados_casa, dados_visitante, event_id, jogador_casa, jogador_visitante):
    """
    🧠 ESTRATÉGIA VIRADA MENTAL - NOVO CRITÉRIO
    
    Objetivo: Apostar no jogador que está fazendo virada mental EM TEMPO REAL
    Critério: Perdeu 1º set + ganhando 2º set por 3+ games de diferença
    Odds ideais: 1.80-2.20 (preferencialmente 1.85-2.05)
    
    Exemplos de aprovação:
    - "3-6,5-2" → Perdeu 1º (3-6), dominando 2º (5-2) = +3 games ✅
    - "2-6,6-1" → Perdeu 1º (2-6), dominando 2º (6-1) = +5 games ✅
    - "4-6,4-3" → Perdeu 1º (4-6), liderando 2º (4-3) = +1 game ❌
    """
    
    print(f"      🧠 Testando VIRADA MENTAL...")
    
    # 1. NOVO CRITÉRIO: PERDEU 1º SET E GANHANDO 2º SET POR 3+ GAMES
    placar = partida.get('placar', '')
    jogador_virada = _identificar_virada_em_andamento(placar)
    
    if not jogador_virada:
        print(f"         ❌ VIRADA MENTAL rejeitada - critério não atendido")
        print(f"         � Necessário: perdeu 1º set + ganhando 2º set por 3+ games")
        return None
    
    print(f"         🔄 VIRADA MENTAL detectada: {jogador_virada} (perdeu 1º, dominando 2º set)")
    
    # 2. SELECIONAR DADOS DO JOGADOR DA VIRADA
    if jogador_virada == 'HOME':
        dados_jogador = dados_casa
        nome_jogador = jogador_casa
        oponente = jogador_visitante
        tipo_jogador = 'HOME'
    else:
        dados_jogador = dados_visitante
        nome_jogador = jogador_visitante
        oponente = jogador_casa
        tipo_jogador = 'AWAY'
    
    # 5. CRITÉRIOS ESPECÍFICOS DA VIRADA MENTAL
    CRITERIOS = {
        'MOMENTUM_SCORE_MINIMO': 60,    # ≥ 60% (últimos 4 games)
        'WIN_1ST_SERVE_MINIMO': 65,     # ≥ 65% no set atual
        'DOUBLE_FAULTS_MAXIMO': 2,      # < 3 DF no total
        'BREAK_POINTS_MINIMO': 40,      # ≥ 40% break points ganhos
        'ODDS_MIN': 1.80,               # Odds mínima
        'ODDS_MAX': 2.20,               # Odds máxima
        'ODDS_IDEAL_MIN': 1.85,         # Faixa ideal mínima
        'ODDS_IDEAL_MAX': 2.05,         # Faixa ideal máxima
        'PRIORIDADE_MINIMA': 4,         # Timing rigoroso
        'NOME': 'VIRADA_MENTAL'
    }
    
    # 6. VALIDAÇÃO DE TIMING
    prioridade_partida = partida.get('prioridade', 0)
    timing_aprovado = prioridade_partida >= CRITERIOS['PRIORIDADE_MINIMA']
    
    print(f"         ⏰ Timing: Prioridade {prioridade_partida} {'✅' if timing_aprovado else '❌'} (≥{CRITERIOS['PRIORIDADE_MINIMA']})")
    
    if not timing_aprovado:
        print(f"         ❌ VIRADA MENTAL rejeitada - timing insuficiente")
        return None
    
    # 7. VALIDAÇÃO DOS CRITÉRIOS TÉCNICOS
    ms = dados_jogador.get('momentum_score', 0)
    w1s = float(dados_jogador.get('win_1st_serve', 0)) if dados_jogador.get('win_1st_serve') else 0
    df = int(dados_jogador.get('double_faults', 0)) if dados_jogador.get('double_faults') else 0
    bp_won = 50  # Default 50% - será melhorado com dados reais
    
    # Validações individuais
    ms_aprovado = ms >= CRITERIOS['MOMENTUM_SCORE_MINIMO']
    w1s_aprovado = w1s >= CRITERIOS['WIN_1ST_SERVE_MINIMO']
    df_aprovado = df <= CRITERIOS['DOUBLE_FAULTS_MAXIMO']
    bp_aprovado = bp_won >= CRITERIOS['BREAK_POINTS_MINIMO']
    
    print(f"")
    print(f"         📊 Momentum Score: {ms}% {'✅' if ms_aprovado else '❌'} (≥{CRITERIOS['MOMENTUM_SCORE_MINIMO']}%)")
    print(f"         🎾 1º Serviço: {w1s}% {'✅' if w1s_aprovado else '❌'} (≥{CRITERIOS['WIN_1ST_SERVE_MINIMO']}%)")
    print(f"         ⚠️ Double Faults: {df} {'✅' if df_aprovado else '❌'} (≤{CRITERIOS['DOUBLE_FAULTS_MAXIMO']})")
    print(f"         💪 Break Points: {bp_won}% {'✅' if bp_aprovado else '❌'} (≥{CRITERIOS['BREAK_POINTS_MINIMO']}%)")
    
    if not (ms_aprovado and w1s_aprovado and df_aprovado and bp_aprovado):
        print(f"")
        print(f"         ❌ VIRADA MENTAL rejeitada - critérios técnicos não atendidos")
        return None
    
    # 8. VALIDAÇÃO DE ODDS
    odds_atuais = buscar_odds_partida_atual(event_id)
    odds_jogador = odds_atuais['casa'] if tipo_jogador == 'HOME' else odds_atuais['visitante']
    
    if odds_jogador != 'N/A':
        try:
            odds_float = float(odds_jogador)
            odds_aprovado = CRITERIOS['ODDS_MIN'] <= odds_float <= CRITERIOS['ODDS_MAX']
            odds_ideal = CRITERIOS['ODDS_IDEAL_MIN'] <= odds_float <= CRITERIOS['ODDS_IDEAL_MAX']
            odds_status = "IDEAL ⭐" if odds_ideal else "VÁLIDA ✅" if odds_aprovado else "FORA ❌"
        except:
            odds_aprovado = False
            odds_status = "ERRO ❌"
    else:
        odds_aprovado = False
        odds_status = "N/A ❌"
    
    print(f"")
    print(f"         💰 Odds: {odds_jogador} {odds_status}")
    print(f"             Faixa válida: {CRITERIOS['ODDS_MIN']}-{CRITERIOS['ODDS_MAX']}")
    print(f"             Faixa ideal: {CRITERIOS['ODDS_IDEAL_MIN']}-{CRITERIOS['ODDS_IDEAL_MAX']}")
    
    if not odds_aprovado:
        print(f"")
        print(f"         ❌ VIRADA MENTAL rejeitada - odds fora da faixa permitida")
        return None
    
    # 9. APROVAÇÃO FINAL
    print(f"")
    print(f"         ✅ VIRADA MENTAL APROVADA!")
    print(f"         🏆 {nome_jogador} demonstrou virada mental em tempo real!")
    
    return {
        'partida_id': event_id,
        'liga': partida['liga'],
        'jogador': nome_jogador,
        'oponente': oponente,
        'placar': placar,
        'fase_timing': partida['fase'],
        'prioridade_timing': partida['prioridade'],
        'tipo': tipo_jogador,
        'momentum': ms,
        'win_1st_serve': w1s,
        'double_faults': df,
        'break_points_won': bp_won,
        'odds_atual': odds_jogador,
        'odds_ideal': odds_ideal,
        'estrategia': 'VIRADA_MENTAL',
        'justificativa': f"Perdeu 1º set, dominando 2º set por 3+ games com {ms}% momentum e {w1s}% 1º serviço"
    }

def _identificar_virada_em_andamento(placar):
    """
    🎯 NOVO CRITÉRIO: Identifica virada mental em andamento
    
    Critério: Perdeu 1º set + ganhando 2º set por 3+ games de diferença
    Exemplos válidos:
    - "3-6,5-2" (perdeu 1º 3-6, ganhando 2º 5-2 = 3 games diferença) ✅
    - "2-6,6-1" (perdeu 1º 2-6, ganhando 2º 6-1 = 5 games diferença) ✅
    - "4-6,4-3" (perdeu 1º 4-6, ganhando 2º 4-3 = 1 game diferença) ❌
    """
    if not placar:
        return None
    
    try:
        # Remover espaços e dividir por vírgula
        sets = [s.strip() for s in placar.split(',')]
        
        # Verificar se temos pelo menos 2 sets (1º terminado, 2º em andamento)
        if len(sets) < 2:
            return None
        
        primeiro_set = sets[0]
        segundo_set = sets[1]
        
        # Verificar formato válido (X-Y)
        if '-' not in primeiro_set or '-' not in segundo_set:
            return None
        
        # Extrair games do 1º set (terminado)
        home_1, away_1 = map(int, primeiro_set.split('-'))
        
        # Extrair games do 2º set (em andamento)
        home_2, away_2 = map(int, segundo_set.split('-'))
        
        # CRITÉRIO 1: Casa perdeu 1º set E está ganhando 2º por 3+ games
        if (home_1 < away_1) and (home_2 - away_2 >= 3):
            print(f"         🎯 VIRADA HOME: Perdeu 1º ({home_1}-{away_1}), dominando 2º ({home_2}-{away_2}) = +{home_2-away_2} games")
            return 'HOME'
        
        # CRITÉRIO 2: Visitante perdeu 1º set E está ganhando 2º por 3+ games  
        if (away_1 < home_1) and (away_2 - home_2 >= 3):
            print(f"         🎯 VIRADA AWAY: Perdeu 1º ({away_1}-{home_1}), dominando 2º ({away_2}-{home_2}) = +{away_2-home_2} games")
            return 'AWAY'
        
        # Debug dos critérios não atendidos
        print(f"         📊 Análise placar '{placar}':")
        print(f"             1º set: HOME {home_1}-{away_1} AWAY")
        print(f"             2º set: HOME {home_2}-{away_2} AWAY (diferença: HOME +{home_2-away_2}, AWAY +{away_2-home_2})")
        
        if home_1 >= away_1 and away_1 >= home_1:
            print(f"             ❌ Nenhum jogador perdeu o 1º set claramente")
        elif (home_1 < away_1) and (home_2 - away_2 < 3):
            print(f"             ❌ HOME perdeu 1º mas não está dominando 2º (+{home_2-away_2} < 3 games)")
        elif (away_1 < home_1) and (away_2 - home_2 < 3):
            print(f"             ❌ AWAY perdeu 1º mas não está dominando 2º (+{away_2-home_2} < 3 games)")
        
        return None
        
    except Exception as e:
        print(f"         ⚠️ Erro ao analisar placar '{placar}': {e}")
        return None

def _esta_no_terceiro_set(placar):
    """Verifica se a partida está no 3º set"""
    if not placar or ',' not in placar:
        return False
    
    try:
        sets = placar.split(',')
        return len(sets) >= 3  # Pelo menos 3 sets (2 terminados + 1 em andamento)
    except:
        return False

def _identificar_jogador_virada(placar):
    """Identifica se algum jogador fez virada (perdeu 1º, ganhou 2º)"""
    if not placar or ',' not in placar:
        return None
    
    try:
        sets = placar.split(',')
        if len(sets) < 3:
            return None
        
        # Analisar 1º e 2º sets
        primeiro_set = sets[0].strip()
        segundo_set = sets[1].strip()
        
        if '-' not in primeiro_set or '-' not in segundo_set:
            return None
        
        # Placar do 1º set
        home_1, away_1 = map(int, primeiro_set.split('-'))
        # Placar do 2º set  
        home_2, away_2 = map(int, segundo_set.split('-'))
        
        # Verificar virada: perdeu 1º E ganhou 2º
        if home_1 < away_1 and home_2 > away_2:  # Casa perdeu 1º, ganhou 2º
            return 'HOME'
        elif away_1 < home_1 and away_2 > home_2:  # Visitante perdeu 1º, ganhou 2º
            return 'AWAY'
        
        return None
        
    except:
        return None

def _esta_liderando_terceiro_set(placar, jogador_virada):
    """Verifica se o jogador da virada está liderando/igualado no 3º set"""
    if not placar or ',' not in placar:
        return False
    
    try:
        sets = placar.split(',')
        if len(sets) < 3:
            return False
        
        terceiro_set = sets[2].strip()
        if '-' not in terceiro_set:
            return False
        
        home_3, away_3 = map(int, terceiro_set.split('-'))
        
        if jogador_virada == 'HOME':
            return home_3 >= away_3  # Casa liderando ou igualado
        else:
            return away_3 >= home_3  # Visitante liderando ou igualado
            
    except:
        return False

def analisar_ev_partidas():
    """Analisa EV das partidas com estratégia VIRADA MENTAL."""
    
    print("🎾 SELEÇÃO FINAL - ESTRATÉGIA VIRADA MENTAL")
    print("=" * 70)
    print("🧠 Nova estratégia focada em comebacks mentais implementada")
    
    print("🔴 FILTRO DE TIMING ULTRA RIGOROSO ATIVADO")
    print("============================================================")
    print("⏰ TIMING PADRÃO: PRIORIDADE ≥ 4 (2º SET MEIO/FINAL)")
    print("🎯 Apenas partidas com prioridade 4 ou 5 serão analisadas")
    print("============================================================")
    
    def verificar_se_e_terceiro_set(placar):
        """Verifica se a partida está no 3º set"""
        if not placar or '-' not in placar:
            return False
        try:
            sets_jogados = placar.count(',') + 1
            return sets_jogados >= 3
        except:
            return False
    
    def verificar_pos_tiebreak(placar):
        """Verifica se houve tie-break no set anterior"""
        if not placar or ',' not in placar:
            return False
        try:
            sets = placar.split(',')
            for set_score in sets[:-1]:
                if '-' in set_score:
                    home, away = set_score.split('-')
                    if (home.strip() == '7' and away.strip() == '6') or (home.strip() == '6' and away.strip() == '7'):
                        return True
        except:
            return False
        return False
    
    print("")
    
    # Buscar partidas filtradas por timing
    partidas_timing = filtrar_partidas_por_timing()
    
    if not partidas_timing:
        print("❌ Nenhuma partida aprovada no filtro de timing.")
        return []
    
    print(f"🎯 {len(partidas_timing)} partidas aprovadas no timing.")
    print("🔄 Analisando dados individuais de cada jogador...")
    print("=" * 80)
    
    oportunidades_finais = []
    
    # Aplicar filtros refinados nas partidas aprovadas por timing
    for partida in partidas_timing:
        event_id = partida['id']
        jogador_casa = partida['jogador_casa']
        jogador_visitante = partida['jogador_visitante']
        
        print(f"📊 Analisando: {jogador_casa} vs {jogador_visitante}")
        
        # Coletar dados de AMBOS os jogadores
        dados_casa = buscar_dados_jogador(jogador_casa, event_id)
        time.sleep(0.2)
        dados_visitante = buscar_dados_jogador(jogador_visitante, event_id)
        time.sleep(0.2)
        
        # Verificar se temos dados válidos para ambos
        if not dados_casa or not dados_visitante:
            print("   ❌ Dados insuficientes para um ou ambos jogadores")
            continue
            
        # Determinar informações base da partida
        placar = partida.get('placar', '')
        ev_principal = max(dados_casa.get('ev', 0), dados_visitante.get('ev', 0))
        is_terceiro_set = verificar_se_e_terceiro_set(placar)
        is_pos_tiebreak = verificar_pos_tiebreak(placar)
        is_alta_tensao = is_terceiro_set or is_pos_tiebreak or partida.get('prioridade', 0) == 5
        
        # SEÇÃO PARA ESTRATÉGIAS
        oportunidades_partida = []
        
        print(f"📊 Analisando estratégias disponíveis...")
        print(f"   📈 EV Principal: {ev_principal:.3f}")
        print(f"   🎯 Alta Tensão: {'✅' if is_alta_tensao else '❌'}")
        print(f"   ⏰ Timing: Prioridade {partida.get('prioridade', 0)}")
        print("")
        
        # 🎯 ESTRATÉGIA 1: VIRADA MENTAL
        resultado_virada = testar_estrategia_virada_mental(
            partida, dados_casa, dados_visitante, event_id, jogador_casa, jogador_visitante
        )
        
        if resultado_virada:
            oportunidades_partida.append(resultado_virada)
            print(f"      🎯 VIRADA MENTAL encontrada para {resultado_virada['jogador']}")
        
        # Adicionar oportunidades encontradas à lista final
        if oportunidades_partida:
            oportunidades_finais.extend(oportunidades_partida)
            print(f"   ✅ {len(oportunidades_partida)} oportunidade(s) encontrada(s) nesta partida")
        else:
            print(f"   ❌ Nenhuma estratégia aprovada para esta partida")
            
    
    # Resumo final
    print("\n" + "=" * 80)
    print(f"🎯 RESULTADO FINAL: {len(oportunidades_finais)} oportunidades encontradas")
    
    for oportunidade in oportunidades_finais:
        print(f"✅ {oportunidade['estrategia']}: {oportunidade['jogador']} vs {oportunidade['oponente']} (Odds: {oportunidade['odds_atual']})")
    
    print("=" * 80)
    return oportunidades_finais

if __name__ == "__main__":
    oportunidades = analisar_ev_partidas()
    print(f"Total de oportunidades: {len(oportunidades)}")
