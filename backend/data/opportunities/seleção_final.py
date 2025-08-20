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
        'ev': 0,
        # Campos REAIS da API B365 para Supremacia Técnica Simplificada
        'aces': 0,
        'break_point_conversions': 0,
        'ranking': 999,
        'name': jogador_nome
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
                            
                            # Extrair estatísticas REAIS da API B365
                            stats_det = stats_info.get('stats_detalhadas', {})
                            
                            # Aces (campo real da API)
                            if 'aces' in stats_det and len(stats_det['aces']) >= 1:
                                try:
                                    dados_jogador['aces'] = int(stats_det['aces'][0])
                                except:
                                    pass
                            
                            # Double Faults (campo real da API)
                            if 'double_faults' in stats_det and len(stats_det['double_faults']) >= 1:
                                try:
                                    dados_jogador['double_faults'] = int(stats_det['double_faults'][0])
                                except:
                                    pass
                            
                            # Win 1st Serve % (campo real da API)
                            if 'win_1st_serve' in stats_det and len(stats_det['win_1st_serve']) >= 1:
                                try:
                                    dados_jogador['win_1st_serve'] = float(stats_det['win_1st_serve'][0])
                                except:
                                    pass
                            
                            # Break Point Conversions % (campo real da API)
                            if 'break_point_conversions' in stats_det and len(stats_det['break_point_conversions']) >= 1:
                                try:
                                    dados_jogador['break_point_conversions'] = float(stats_det['break_point_conversions'][0])
                                except:
                                    pass
                            
                            # Buscar ranking do jogador HOME no endpoint correto
                            try:
                                # Buscar dados detalhados no endpoint /v3/event/view que tem rankings
                                url_view = f"{base_url}/v3/event/view"
                                params_view = {'event_id': event_id, 'token': api_key}
                                response_view = requests.get(url_view, params=params_view, timeout=10)
                                
                                if response_view.status_code == 200:
                                    data_view = response_view.json()
                                    if data_view.get('success') == 1 and 'results' in data_view:
                                        result_view = data_view['results'][0] if isinstance(data_view['results'], list) else data_view['results']
                                        home_pos = result_view.get('extra', {}).get('home_pos', 999)
                                        dados_jogador['ranking'] = int(home_pos) if home_pos and home_pos != 999 else 999
                                    else:
                                        dados_jogador['ranking'] = 999
                                else:
                                    dados_jogador['ranking'] = 999
                            except:
                                dados_jogador['ranking'] = 999
                                try:
                                    dados_jogador['total_points_won'] = int(stats_det['total_points_won'][0])
                                except:
                                    pass
                            
                            # Winners
                            if 'winners' in stats_det and len(stats_det['winners']) >= 1:
                                try:
                                    dados_jogador['winners'] = int(stats_det['winners'][0])
                                except:
                                    pass
                            
                            # Unforced errors
                            if 'unforced_errors' in stats_det and len(stats_det['unforced_errors']) >= 1:
                                try:
                                    dados_jogador['unforced_errors'] = int(stats_det['unforced_errors'][0])
                                except:
                                    pass
                            
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
                            
                            # Extrair estatísticas REAIS da API B365 para jogador AWAY
                            stats_det = stats_info.get('stats_detalhadas', {})
                            
                            # Aces (campo real da API - índice 1 para away)
                            if 'aces' in stats_det and len(stats_det['aces']) >= 2:
                                try:
                                    dados_jogador['aces'] = int(stats_det['aces'][1])
                                except:
                                    pass
                            
                            # Double Faults (campo real da API - índice 1 para away)
                            if 'double_faults' in stats_det and len(stats_det['double_faults']) >= 2:
                                try:
                                    dados_jogador['double_faults'] = int(stats_det['double_faults'][1])
                                except:
                                    pass
                            
                            # Win 1st Serve % (campo real da API - índice 1 para away)
                            if 'win_1st_serve' in stats_det and len(stats_det['win_1st_serve']) >= 2:
                                try:
                                    dados_jogador['win_1st_serve'] = float(stats_det['win_1st_serve'][1])
                                except:
                                    pass
                            
                            # Break Point Conversions % (campo real da API - índice 1 para away)
                            if 'break_point_conversions' in stats_det and len(stats_det['break_point_conversions']) >= 2:
                                try:
                                    dados_jogador['break_point_conversions'] = float(stats_det['break_point_conversions'][1])
                                except:
                                    pass
                            
                            # Buscar ranking do jogador AWAY no endpoint correto
                            try:
                                # Buscar dados detalhados no endpoint /v3/event/view que tem rankings
                                url_view = f"{base_url}/v3/event/view"
                                params_view = {'event_id': event_id, 'token': api_key}
                                response_view = requests.get(url_view, params=params_view, timeout=10)
                                
                                if response_view.status_code == 200:
                                    data_view = response_view.json()
                                    if data_view.get('success') == 1 and 'results' in data_view:
                                        result_view = data_view['results'][0] if isinstance(data_view['results'], list) else data_view['results']
                                        away_pos = result_view.get('extra', {}).get('away_pos', 999)
                                        dados_jogador['ranking'] = int(away_pos) if away_pos and away_pos != 999 else 999
                                    else:
                                        dados_jogador['ranking'] = 999
                                else:
                                    dados_jogador['ranking'] = 999
                            except:
                                dados_jogador['ranking'] = 999
                            
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
    🧠 ESTRATÉGIA VIRADA MENTAL - CRITÉRIOS APRIMORADOS
    
    Objetivo: Apostar no jogador que está fazendo virada mental EM TEMPO REAL
    Critério Principal: Perdeu 1º set + empatando ou ganhando 2º set
    Odds: 1.70-2.20 (preferencialmente 1.85-2.05)
    
    Critérios Técnicos Básicos:
    - Momentum Score ≥ 55% | 1º Serviço ≥ 55% | Double Faults ≤ 4 | Break Points ≥ 40%
    
    🚀 NOVOS CRITÉRIOS DE DOMINÂNCIA NO RETORNO:
    - Games de Retorno ≥ 35% (quebrando o adversário)
    - Break Defense ≤ 60% (adversário vulnerável no saque)
    - Controle de Pontos ≥ 58% (dominando a maioria dos pontos)
    
    Exemplos de aprovação:
    - "3-6,5-2" → Perdeu 1º (3-6), dominando 2º (5-2) = +3 games ✅
    - "2-6,6-1" → Perdeu 1º (2-6), dominando 2º (6-1) = +5 games ✅
    - "4-6,4-3" → Perdeu 1º (4-6), dominando 2º (4-3) = +1 game ✅
    - "3-6,2-2" → Perdeu 1º (3-6), empatando 2º (2-2) = empate ✅
    - "4-6,4-3" → Perdeu 1º (4-6), liderando 2º (4-3) = +1 game ✅
    """
    
    print(f"      🧠 Testando VIRADA MENTAL...")
    
    # 1. NOVO CRITÉRIO: PERDEU 1º SET E GANHANDO 2º SET POR 1+ GAMES
    placar = partida.get('placar', '')
    jogador_virada = _identificar_virada_em_andamento(placar)
    
    if not jogador_virada:
        print(f"         ❌ VIRADA MENTAL rejeitada - critério não atendido")
        print(f"         📝 Necessário: perdeu 1º set + empatando ou ganhando 2º set")
        return None
    
    print(f"         🔄 VIRADA MENTAL detectada: {jogador_virada} (perdeu 1º, recuperando no 2º set)")
    
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
        'MOMENTUM_SCORE_MINIMO': 55,    # ≥ 55% (últimos 4 games)
        'WIN_1ST_SERVE_MINIMO': 55,     # ≥ 55% no set atual
        'DOUBLE_FAULTS_MAXIMO': 4,      # ≤ 4 DF no total (alterado de 2 para 4)
        'BREAK_POINTS_MINIMO': 40,      # ≥ 40% break points ganhos
        # NOVOS CRITÉRIOS - DOMINÂNCIA NO RETORNO
        'RETURN_GAMES_MINIMO': 35,      # ≥ 35% games de retorno ganhos
        'BREAK_DEFENSE_MAXIMO': 60,     # ≤ 60% break points salvos (adversário vulnerável)
        'TOTAL_POINTS_MINIMO': 58,      # ≥ 58% total de pontos ganhos
        # ODDS (mantidas originais)
        'ODDS_MIN': 1.70,               # Odds mínima (alterado de 1.80 para 1.70)
        'ODDS_MAX': 2.20,               # Odds máxima
        'ODDS_IDEAL_MIN': 1.85,         # Faixa ideal mínima
        'ODDS_IDEAL_MAX': 2.05,         # Faixa ideal máxima
        'PRIORIDADE_MINIMA': 4,         # Timing ultra específico - APENAS prioridade 4
        'PRIORIDADE_MAXIMA': 4,         # Timing ultra específico - APENAS prioridade 4
        'NOME': 'VIRADA_MENTAL'
    }
    
    # 6. VALIDAÇÃO DE TIMING ULTRA RIGOROSO
    prioridade_partida = partida.get('prioridade', 0)
    timing_aprovado = prioridade_partida == CRITERIOS['PRIORIDADE_MINIMA']  # Exatamente igual a 4
    
    print(f"         ⏰ Timing: Prioridade {prioridade_partida} {'✅' if timing_aprovado else '❌'} (= {CRITERIOS['PRIORIDADE_MINIMA']})")
    
    if not timing_aprovado:
        print(f"         ❌ VIRADA MENTAL rejeitada - timing insuficiente")
        return None
    
    # 7. VALIDAÇÃO DOS CRITÉRIOS TÉCNICOS - VERSÃO SIMPLIFICADA COM DADOS REAIS
    ms = dados_jogador.get('momentum_score', 0)
    w1s = float(dados_jogador.get('win_1st_serve', 0)) if dados_jogador.get('win_1st_serve') else 0
    df = int(dados_jogador.get('double_faults', 0)) if dados_jogador.get('double_faults') else 0
    
    # USAR DADOS REAIS DA API B365
    aces = int(dados_jogador.get('aces', 0))
    break_conversions = float(dados_jogador.get('break_point_conversions', 0))
    ranking = int(dados_jogador.get('ranking', 999))
    
    # Validações individuais - critérios básicos
    ms_aprovado = ms >= CRITERIOS['MOMENTUM_SCORE_MINIMO']
    w1s_aprovado = w1s >= CRITERIOS['WIN_1ST_SERVE_MINIMO']
    df_aprovado = df <= CRITERIOS['DOUBLE_FAULTS_MAXIMO']
    
    # Critérios simplificados de qualidade técnica (baseados na API real)
    aces_liquidos = aces - df
    qualidade_saque = aces_liquidos >= 2 and w1s >= 60  # Pelo menos 2 aces líquidos + 60% primeiro saque
    pressao_break = break_conversions >= 25  # 25%+ conversão break points
    ranking_decente = ranking <= 500  # Top 500 ranking
    
    print(f"")
    print(f"         📊 Momentum Score: {ms}% {'✅' if ms_aprovado else '❌'} (≥{CRITERIOS['MOMENTUM_SCORE_MINIMO']}%)")
    print(f"         🎾 1º Serviço: {w1s}% {'✅' if w1s_aprovado else '❌'} (≥{CRITERIOS['WIN_1ST_SERVE_MINIMO']}%)")
    print(f"         ⚠️ Double Faults: {df} {'✅' if df_aprovado else '❌'} (≤{CRITERIOS['DOUBLE_FAULTS_MAXIMO']})")
    print(f"")
    print(f"         🚀 QUALIDADE TÉCNICA (DADOS REAIS):")
    print(f"         � Aces líquidos: {aces_liquidos} ({aces}A - {df}DF) {'✅' if qualidade_saque else '❌'} (≥3 + 60% 1º saque)")
    print(f"         � Break conversão: {break_conversions}% {'✅' if pressao_break else '❌'} (≥25%)")
    print(f"         🏆 Ranking: #{ranking} {'✅' if ranking_decente else '❌'} (≤500)")
    
    # Verificar se critérios básicos + pelo menos 2 critérios técnicos foram atendidos
    criterios_basicos = ms_aprovado and w1s_aprovado and df_aprovado
    criterios_tecnicos = sum([qualidade_saque, pressao_break, ranking_decente])
    todos_criterios = criterios_basicos and criterios_tecnicos >= 2
    
    if not todos_criterios:
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
        'aces': aces,
        'break_conversions': break_conversions,
        'ranking': ranking,
        'odds_atual': odds_jogador,
        'odds_ideal': odds_ideal,
        'estrategia': 'VIRADA_MENTAL',
        'justificativa': f"Perdeu 1º set, recuperando no 2º set com {ms}% momentum, {aces_liquidos} aces líquidos e {break_conversions}% conversão break"
    }


def testar_estrategia_supremacia_tecnica(partida, dados_casa, dados_visitante, event_id, jogador_casa, jogador_visitante):
    """
    🏆 ESTRATÉGIA SUPREMACIA TÉCNICA - COMPLEMENTAR À VIRADA MENTAL
    
    Objetivo: Apostar no jogador tecnicamente superior que ainda oferece valor nas odds
    Situação: Dominância técnica clara mas odds ainda não refletem totalmente
    
    CRITÉRIOS DE SITUAÇÃO:
    - Qualquer resultado no 1º set (equilibrado ou perdido) 
    - 2º set início/meio (prioridade 3-4)
    - Odds: 1.60-2.00 (favorito técnico subvalorizado)
    
    CRITÉRIOS TÉCNICOS DE SUPREMACIA:
    - 1º Serviço ≥ 60% (dominância no saque)
    - Aces ≥ 5 (poder de finalização)
    - Service Games Won ≥ 85% (segurança no saque)
    - Return Points Won ≥ 45% (pressão no retorno)
    - Total Points Won ≥ 60% (controle geral)
    - Winners/Errors Ratio ≥ 1.5 (eficiência ofensiva)
    """
    
    print(f"      🏆 Testando SUPREMACIA TÉCNICA...")
    
    # 1. CRITÉRIOS ESPECÍFICOS DA SUPREMACIA TÉCNICA
    CRITERIOS = {
        # DOMINÂNCIA NO SAQUE
        'FIRST_SERVE_MINIMO': 60,       # ≥ 60% 1º serviço
        'ACES_MINIMO': 5,               # ≥ 5 aces
        'SERVICE_GAMES_MINIMO': 85,     # ≥ 85% service games won
        
        # PRESSÃO NO RETORNO  
        'RETURN_POINTS_MINIMO': 45,     # ≥ 45% return points won
        'BREAK_POINTS_CREATED_MINIMO': 8, # ≥ 8 break points criados
        
        # CONTROLE GERAL
        'TOTAL_POINTS_MINIMO': 60,      # ≥ 60% total points won
        'WINNERS_ERRORS_RATIO_MINIMO': 1.5, # ≥ 1.5 winners/errors ratio
        
        # TIMING E ODDS
        'PRIORIDADE_MINIMA': 3,         # Prioridade 3-4 (mais flexível)
        'PRIORIDADE_MAXIMA': 4,         # Prioridade 3-4 (mais flexível)
        'ODDS_MIN': 1.60,               # Favorito técnico
        'ODDS_MAX': 2.00,               # Ainda com valor
        'NOME': 'SUPREMACIA_TECNICA'
    }
    
    # 2. VALIDAÇÃO DE TIMING (mais flexível que virada mental)
    prioridade_partida = partida.get('prioridade', 0)
    timing_aprovado = CRITERIOS['PRIORIDADE_MINIMA'] <= prioridade_partida <= CRITERIOS['PRIORIDADE_MAXIMA']
    
    print(f"         ⏰ Timing: Prioridade {prioridade_partida} {'✅' if timing_aprovado else '❌'} ({CRITERIOS['PRIORIDADE_MINIMA']}-{CRITERIOS['PRIORIDADE_MAXIMA']})")
    
    if not timing_aprovado:
        print(f"         ❌ SUPREMACIA TÉCNICA rejeitada - timing inadequado")
        return None
    
    # 3. IDENTIFICAR JOGADOR COM SUPREMACIA TÉCNICA
    supremacia_casa = _avaliar_supremacia_tecnica(dados_casa, CRITERIOS)
    supremacia_visitante = _avaliar_supremacia_tecnica(dados_visitante, CRITERIOS)
    
    if supremacia_casa and supremacia_visitante:
        print(f"         ❌ SUPREMACIA TÉCNICA rejeitada - ambos jogadores dominantes")
        return None
    elif supremacia_casa:
        dados_jogador = dados_casa
        nome_jogador = jogador_casa
        oponente = jogador_visitante
        tipo_jogador = 'HOME'
    elif supremacia_visitante:
        dados_jogador = dados_visitante
        nome_jogador = jogador_visitante
        oponente = jogador_casa
        tipo_jogador = 'AWAY'
    else:
        print(f"         ❌ SUPREMACIA TÉCNICA rejeitada - nenhum jogador demonstra supremacia")
        return None
    
    print(f"         🎯 SUPREMACIA DETECTADA: {nome_jogador} (tipo: {tipo_jogador})")
    
    # 4. VALIDAÇÃO DE ODDS
    odds_atuais = buscar_odds_partida_atual(event_id)
    odds_jogador = odds_atuais['casa'] if tipo_jogador == 'HOME' else odds_atuais['visitante']
    
    if odds_jogador != 'N/A':
        try:
            odds_float = float(odds_jogador)
            odds_aprovado = CRITERIOS['ODDS_MIN'] <= odds_float <= CRITERIOS['ODDS_MAX']
            
            print(f"         💰 Odds {nome_jogador}: {odds_float:.2f} {'✅' if odds_aprovado else '❌'} ({CRITERIOS['ODDS_MIN']}-{CRITERIOS['ODDS_MAX']})")
            
            if not odds_aprovado:
                print(f"         ❌ SUPREMACIA TÉCNICA rejeitada - odds fora da faixa")
                return None
        except:
            print(f"         ❌ SUPREMACIA TÉCNICA rejeitada - odds inválidas")
            return None
    else:
        print(f"         ❌ SUPREMACIA TÉCNICA rejeitada - odds não disponíveis")
        return None
    
    # 5. APROVAÇÃO FINAL
    print(f"")
    print(f"         ✅ SUPREMACIA TÉCNICA APROVADA!")
    print(f"         🏆 {nome_jogador} demonstra supremacia técnica com valor nas odds!")
    
    # Extrair estatísticas para o retorno
    first_serve = float(dados_jogador.get('first_serve_percentage', 0))
    aces = int(dados_jogador.get('aces', 0))
    total_points = float(dados_jogador.get('total_points_won', 0))
    
    return {
        'partida_id': event_id,
        'liga': partida['liga'],
        'jogador': nome_jogador,
        'oponente': oponente,
        'placar': partida.get('placar', ''),
        'fase_timing': partida['fase'],
        'prioridade_timing': partida['prioridade'],
        'tipo': tipo_jogador,
        'first_serve_pct': first_serve,
        'aces': aces,
        'total_points_won': total_points,
        'odds_atual': odds_jogador,
        'estrategia': 'SUPREMACIA_TECNICA',
        'justificativa': f"Supremacia técnica clara: {first_serve}% 1º serviço, {aces} aces, {total_points}% pontos totais"
    }


def _avaliar_supremacia_tecnica(dados_jogador, criterios):
    """
    Avalia se um jogador demonstra supremacia técnica - VERSÃO SIMPLIFICADA
    
    Usa apenas dados REAIS da API B365:
    - Aces vs Double Faults (eficiência no saque)  
    - Win 1st Serve % (consistência)
    - Break Point Conversions % (pressão)
    - Ranking (vantagem técnica esperada)
    """
    try:
        nome_jogador = dados_jogador.get('name', 'Jogador')
        
        # Campos disponíveis na API B365
        aces = int(dados_jogador.get('aces', 0))
        double_faults = int(dados_jogador.get('double_faults', 0))
        win_1st_serve = float(dados_jogador.get('win_1st_serve', 0))
        break_conversions = float(dados_jogador.get('break_point_conversions', 0))
        ranking = int(dados_jogador.get('ranking', 999))
        
        # Verificar se temos dados mínimos
        if win_1st_serve == 0:
            print(f"         ⚠️ {nome_jogador} - Dados insuficientes para supremacia técnica")
            return False
        
        # 1. EFICIÊNCIA NO SAQUE (Aces - Double Faults + Win 1st Serve%)
        saque_liquido = aces - double_faults  # Diferença líquida
        eficiencia_saque = (saque_liquido * 2) + (win_1st_serve * 0.8)  # Peso para % 1st serve
        
        # 2. PRESSÃO NO BREAK (Break Point Conversions%)
        pressao_break = break_conversions * 1.5  # Amplificar importância
        
        # 3. VANTAGEM DE RANKING (quanto menor o número, melhor)
        vantagem_ranking = max(0, (200 - ranking) / 200 * 100)  # Normalizar de 0-100
        
        # 4. ÍNDICE DE DOMINÂNCIA TÉCNICA COMBINADO
        indice_dominancia = (
            eficiencia_saque * 0.40 +      # 40% - eficiência no saque
            pressao_break * 0.35 +          # 35% - pressão no break
            vantagem_ranking * 0.25         # 25% - vantagem de ranking
        )
        
        # CRITÉRIOS SIMPLIFICADOS:
        criterios_check = {
            'saque_eficiente': saque_liquido >= 5,  # Pelo menos 5 aces líquidos
            'primeiro_saque': win_1st_serve >= 60,  # 60%+ no 1º saque
            'break_pressure': break_conversions >= 30,  # 30%+ conversão break
            'ranking_top': ranking <= 500  # Top 500 ranking
        }
        
        criterios_atendidos = sum(criterios_check.values())
        
        # LOGGING DOS CRITÉRIOS
        print(f"         📊 {nome_jogador} - Análise Supremacia Técnica:")
        print(f"         🎾 Aces líquidos: {saque_liquido} ({aces}A - {double_faults}DF) {'✅' if criterios_check['saque_eficiente'] else '❌'}")
        print(f"         🎯 1º saque: {win_1st_serve}% {'✅' if criterios_check['primeiro_saque'] else '❌'}")
        print(f"         � Break conversão: {break_conversions}% {'✅' if criterios_check['break_pressure'] else '❌'}")
        print(f"         🏆 Ranking: #{ranking} {'✅' if criterios_check['ranking_top'] else '❌'}")
        print(f"         ⚡ Índice Dominância: {indice_dominancia:.1f}")
        print(f"         📈 Critérios: {criterios_atendidos}/4 atendidos")
        
        # TEM SUPREMACIA se:
        # - Índice > 60 E pelo menos 2 critérios atendidos
        # OU Índice > 80 (dominância clara)
        tem_supremacia = (
            (indice_dominancia > 60.0 and criterios_atendidos >= 2) or
            indice_dominancia > 80.0
        )
        
        print(f"         🏆 Supremacia: {'✅ DETECTADA' if tem_supremacia else '❌ NÃO DETECTADA'}")
        
        return tem_supremacia
        
    except Exception as e:
        print(f"         ⚠️ Erro ao avaliar supremacia técnica: {e}")
        return False

def _identificar_virada_em_andamento(placar):
    """
    🎯 NOVO CRITÉRIO: Identifica virada mental em andamento
    
    Critério: Perdeu 1º set + empatando ou ganhando 2º set
    Exemplos válidos:
    - "3-6,5-2" (perdeu 1º 3-6, ganhando 2º 5-2 = 3 games diferença) ✅
    - "2-6,6-1" (perdeu 1º 2-6, ganhando 2º 6-1 = 5 games diferença) ✅
    - "4-6,4-3" (perdeu 1º 4-6, ganhando 2º 4-3 = 1 game diferença) ✅
    - "3-6,2-2" (perdeu 1º 3-6, empatando 2º 2-2 = empate) ✅
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
        
        # CRITÉRIO 1: Casa perdeu 1º set E está empatando ou ganhando 2º
        if (home_1 < away_1) and (home_2 - away_2 >= 0):
            status = "empatando" if home_2 == away_2 else f"dominando (+{home_2-away_2})"
            print(f"         🎯 VIRADA HOME: Perdeu 1º ({home_1}-{away_1}), {status} 2º ({home_2}-{away_2})")
            return 'HOME'
        
        # CRITÉRIO 2: Visitante perdeu 1º set E está empatando ou ganhando 2º  
        if (away_1 < home_1) and (away_2 - home_2 >= 0):
            status = "empatando" if away_2 == home_2 else f"dominando (+{away_2-home_2})"
            print(f"         🎯 VIRADA AWAY: Perdeu 1º ({away_1}-{home_1}), {status} 2º ({away_2}-{home_2})")
            return 'AWAY'
        
        # Debug dos critérios não atendidos
        print(f"         📊 Análise placar '{placar}':")
        print(f"             1º set: HOME {home_1}-{away_1} AWAY")
        print(f"             2º set: HOME {home_2}-{away_2} AWAY (diferença: HOME +{home_2-away_2}, AWAY +{away_2-home_2})")
        
        if home_1 >= away_1 and away_1 >= home_1:
            print(f"             ❌ Nenhum jogador perdeu o 1º set claramente")
        elif (home_1 < away_1) and (home_2 - away_2 < 0):
            print(f"             ❌ HOME perdeu 1º mas está perdendo 2º ({home_2-away_2} < 0 games)")
        elif (away_1 < home_1) and (away_2 - home_2 < 0):
            print(f"             ❌ AWAY perdeu 1º mas está perdendo 2º ({away_2-home_2} < 0 games)")
        
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
    
    print("🎾 SELEÇÃO FINAL - ESTRATÉGIAS DUPLAS")
    print("=" * 70)
    print("🧠 VIRADA MENTAL: Comebacks dramáticos em tempo real")
    print("🏆 SUPREMACIA TÉCNICA: Dominância técnica com valor nas odds")
    print("🚀 FILTROS DE DOMINÂNCIA NO RETORNO ATIVADOS")
    
    print("🔴 FILTRO DE TIMING ULTRA RIGOROSO ATIVADO")
    print("============================================================")
    print("🎯 VIRADA MENTAL:")
    print("   • Timing: Prioridade = 4 (2º set meio/final)")
    print("   • Critério: Perdeu 1º set + dominando 2º set por 1+ games")
    print("   • Odds: 1.70-2.20")
    print("")
    print("🏆 SUPREMACIA TÉCNICA (NOVA):")
    print("   • Timing: Prioridade 3-4 (mais flexível)")
    print("   • Critério: Dominância técnica clara em saque/retorno/controle")
    print("   • Odds: 1.60-2.00 (favoritos com valor)")
    print("")
    print("🚀 CRITÉRIOS DE DOMINÂNCIA NO RETORNO (AMBAS):")
    print("   • Games de Retorno ≥ 35% (quebrando o adversário)")
    print("   • Break Defense ≤ 60% (adversário vulnerável)")
    print("   • Controle de Pontos ≥ 58% (dominando a partida)")
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
        
        # 🏆 ESTRATÉGIA 2: SUPREMACIA TÉCNICA (NOVA)
        if not resultado_virada:  # Só testa se virada mental não foi aprovada
            resultado_supremacia = testar_estrategia_supremacia_tecnica(
                partida, dados_casa, dados_visitante, event_id, jogador_casa, jogador_visitante
            )
            
            if resultado_supremacia:
                oportunidades_partida.append(resultado_supremacia)
                print(f"      🏆 SUPREMACIA TÉCNICA encontrada para {resultado_supremacia['jogador']}")
        
        # Adicionar oportunidades encontradas à lista final
        if oportunidades_partida:
            oportunidades_finais.extend(oportunidades_partida)
            estrategia_usada = oportunidades_partida[0]['estrategia']
            print(f"   ✅ {len(oportunidades_partida)} oportunidade(s) encontrada(s) - {estrategia_usada}")
        else:
            print(f"   ❌ Nenhuma estratégia aprovada para esta partida")
            
    
    # Resumo final com estatísticas por estratégia
    print("\n" + "=" * 80)
    print(f"🎯 RESULTADO FINAL: {len(oportunidades_finais)} oportunidades encontradas")
    print("=" * 80)
    
    # Contar por estratégia
    virada_mental = [op for op in oportunidades_finais if op['estrategia'] == 'VIRADA_MENTAL']
    supremacia_tecnica = [op for op in oportunidades_finais if op['estrategia'] == 'SUPREMACIA_TECNICA']
    
    print(f"🧠 VIRADA MENTAL: {len(virada_mental)} oportunidades")
    for op in virada_mental:
        print(f"   ✅ {op['jogador']} vs {op['oponente']} (Odds: {op['odds_atual']}) - {op['justificativa']}")
    
    print(f"\n🏆 SUPREMACIA TÉCNICA: {len(supremacia_tecnica)} oportunidades")
    for op in supremacia_tecnica:
        print(f"   ✅ {op['jogador']} vs {op['oponente']} (Odds: {op['odds_atual']}) - {op['justificativa']}")
    
    if len(oportunidades_finais) == 0:
        print("❌ Nenhuma oportunidade encontrada nas estratégias ativas")
        print("💡 Sistema ultra-seletivo priorizando qualidade sobre quantidade")
    
    print("=" * 80)
    return oportunidades_finais

if __name__ == "__main__":
    oportunidades = analisar_ev_partidas()
    print(f"Total de oportunidades: {len(oportunidades)}")
