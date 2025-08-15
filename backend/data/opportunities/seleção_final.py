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

def _primeiro_set_terminou(placar):
    """
    Verifica se o primeiro set já terminou
    Formato esperado: "6-4, 3-2" (primeiro set 6-4, segundo set 3-2)
    """
    if not placar or ',' not in placar:
        return False
    
    try:
        sets = placar.split(',')
        if len(sets) < 2:
            return False
        
        primeiro_set = sets[0].strip()
        if '-' in primeiro_set:
            home_score, away_score = primeiro_set.split('-')
            home_score = int(home_score.strip())
            away_score = int(away_score.strip())
            
            # Verifica se o set terminou (6+ games para o vencedor e diferença adequada)
            if (home_score >= 6 or away_score >= 6):
                # Vitória normal (6-4, 6-3, etc.) ou tie-break (7-6)
                if abs(home_score - away_score) >= 2 or max(home_score, away_score) == 7:
                    return True
    except:
        return False
    
    return False

def _jogador_ganhou_primeiro_set(placar, tipo_jogador):
    """
    Verifica se o jogador ganhou o primeiro set
    tipo_jogador: 'HOME' ou 'AWAY'
    """
    if not placar or ',' not in placar:
        return False
    
    try:
        sets = placar.split(',')
        primeiro_set = sets[0].strip()
        
        if '-' in primeiro_set:
            home_score, away_score = primeiro_set.split('-')
            home_score = int(home_score.strip())
            away_score = int(away_score.strip())
            
            if tipo_jogador == 'HOME':
                return home_score > away_score
            else:
                return away_score > home_score
    except:
        return False
    
    return False

def _esta_ganhando_segundo_set(placar, tipo_jogador):
    """
    Verifica se o jogador está ganhando OU empatado no segundo set
    """
    if not placar or ',' not in placar:
        return False
    
    try:
        sets = placar.split(',')
        if len(sets) < 2:
            return False
        
        segundo_set = sets[1].strip()
        
        if '-' in segundo_set:
            home_score, away_score = segundo_set.split('-')
            home_score = int(home_score.strip())
            away_score = int(away_score.strip())
            
            if tipo_jogador == 'HOME':
                return home_score >= away_score
            else:
                return away_score >= home_score
    except:
        return False
    
    return False

def testar_estrategia_alavancagem(partida, dados_casa, dados_visitante, ev_principal, event_id, jogador_casa, jogador_visitante):
    """Testa se a partida atende aos critérios da estratégia ALAVANCAGEM"""
    
    # Critérios específicos da ALAVANCAGEM
    CRITERIOS = {
        'EV_MINIMO': 0.05,
        'MOMENTUM_SCORE_MINIMO': 55,
        'WIN_1ST_SERVE_MINIMO': 55,
        'DOUBLE_FAULTS_MAXIMO': 8,
        'ODDS_MIN': 1.20,
        'ODDS_MAX': 1.50,
        'PRIORIDADE_MINIMA': 4,       # 2º SET MEIO/FINAL - TIMING RIGOROSO
        'NOME': 'ALAVANCAGEM'
    }
    
    print(f"      🚀 Testando ALAVANCAGEM...")
    
    # 1. VALIDAÇÃO DE TIMING - PRIORIDADE MÍNIMA
    prioridade_partida = partida.get('prioridade', 0)
    prioridade_minima = CRITERIOS['PRIORIDADE_MINIMA']
    timing_aprovado = prioridade_partida >= prioridade_minima
    
    print(f"         ⏰ Timing: Prioridade {prioridade_partida} {'✅' if timing_aprovado else '❌'} (≥{prioridade_minima})")
    
    if not timing_aprovado:
        print(f"         ❌ ALAVANCAGEM rejeitada - timing insuficiente")
        return None
    
    # Dados dos jogadores
    ms_casa = dados_casa.get('momentum_score', 0)
    ms_visitante = dados_visitante.get('momentum_score', 0)
    w1s_casa = float(dados_casa.get('win_1st_serve', 0)) if dados_casa.get('win_1st_serve') else 0
    w1s_visitante = float(dados_visitante.get('win_1st_serve', 0)) if dados_visitante.get('win_1st_serve') else 0
    
    # Validação individual
    casa_dominante = (ms_casa >= CRITERIOS['MOMENTUM_SCORE_MINIMO']) and (w1s_casa >= CRITERIOS['WIN_1ST_SERVE_MINIMO'])
    visitante_dominante = (ms_visitante >= CRITERIOS['MOMENTUM_SCORE_MINIMO']) and (w1s_visitante >= CRITERIOS['WIN_1ST_SERVE_MINIMO'])
    dominancia_aprovada = casa_dominante or visitante_dominante
    ev_aprovado = ev_principal >= CRITERIOS['EV_MINIMO']
    
    print(f"")
    print(f"         📊 Dominância: Casa={'✅' if casa_dominante else '❌'}, Visitante={'✅' if visitante_dominante else '❌'}")
    print(f"")
    print(f"         ⚡ EV: {ev_principal:.3f} {'✅' if ev_aprovado else '❌'} (≥{CRITERIOS['EV_MINIMO']})")
    
    if not (dominancia_aprovada and ev_aprovado):
        print(f"")
        print(f"         ❌ ALAVANCAGEM rejeitada")
        return None
    
    # ========== VALIDAÇÕES ESPECÍFICAS DE ALAVANCAGEM ==========
    placar = partida.get('placar', '')
    
    # 1. Verificar se o primeiro set terminou
    if not _primeiro_set_terminou(placar):
        print(f"         ❌ ALAVANCAGEM rejeitada - primeiro set ainda não terminou (placar: {placar})")
        return None
    
    # 2. Identificar quem ganhou o primeiro set e se está ganhando no segundo
    casa_ganhou_1set = _jogador_ganhou_primeiro_set(placar, 'HOME')
    visitante_ganhou_1set = _jogador_ganhou_primeiro_set(placar, 'AWAY')
    casa_ganhando_2set = _esta_ganhando_segundo_set(placar, 'HOME')
    visitante_ganhando_2set = _esta_ganhando_segundo_set(placar, 'AWAY')
    
    print(f"         🏆 1º Set: Casa={'✅' if casa_ganhou_1set else '❌'}, Visitante={'✅' if visitante_ganhou_1set else '❌'}")
    print(f"         ⚡ 2º Set: Casa={'✅' if casa_ganhando_2set else '❌'}, Visitante={'✅' if visitante_ganhando_2set else '❌'}")
    
    # 3. Validar contexto de alavancagem: ganhou 1º set + (ganhando ou empatado no 2º) + dominante
    casa_alavancagem_valida = casa_ganhou_1set and casa_ganhando_2set and casa_dominante
    visitante_alavancagem_valida = visitante_ganhou_1set and visitante_ganhando_2set and visitante_dominante
    
    if not (casa_alavancagem_valida or visitante_alavancagem_valida):
        print(f"         ❌ ALAVANCAGEM rejeitada - contexto de sets não atende critérios")
        print(f"            Casa: ganhou1º={casa_ganhou_1set}, ganha2º={casa_ganhando_2set}, dominante={casa_dominante}")
        print(f"            Visitante: ganhou1º={visitante_ganhou_1set}, ganha2º={visitante_ganhando_2set}, dominante={visitante_dominante}")
        return None
    
    print(f"         ✅ CONTEXTO ALAVANCAGEM VÁLIDO!")
    
    # Selecionar jogador target baseado no contexto de alavancagem
    if casa_alavancagem_valida and not visitante_alavancagem_valida:
        jogador_target = {'dados': dados_casa, 'nome': jogador_casa, 'oponente': jogador_visitante, 'tipo': 'HOME'}
    elif visitante_alavancagem_valida and not casa_alavancagem_valida:
        jogador_target = {'dados': dados_visitante, 'nome': jogador_visitante, 'oponente': jogador_casa, 'tipo': 'AWAY'}
    else:
        # Ambos dominantes - escolher o com maior MS
        if ms_casa >= ms_visitante:
            jogador_target = {'dados': dados_casa, 'nome': jogador_casa, 'oponente': jogador_visitante, 'tipo': 'HOME'}
        else:
            jogador_target = {'dados': dados_visitante, 'nome': jogador_visitante, 'oponente': jogador_casa, 'tipo': 'AWAY'}
    
    # Validações finais - buscar odds atuais
    odds_atuais = buscar_odds_partida_atual(event_id)
    odds_jogador = odds_atuais['casa'] if jogador_target['tipo'] == 'HOME' else odds_atuais['visitante']
    if odds_jogador != 'N/A':
        try:
            odds_float = float(odds_jogador)
            odds_aprovado = CRITERIOS['ODDS_MIN'] <= odds_float <= CRITERIOS['ODDS_MAX']
        except:
            odds_aprovado = False
    else:
        odds_aprovado = False
    
    df_value = int(jogador_target['dados'].get('double_faults', 0)) if jogador_target['dados'].get('double_faults') else 0
    df_aprovado = df_value <= CRITERIOS['DOUBLE_FAULTS_MAXIMO']
    
    print(f"")
    print(f"         💰 Odds: {odds_jogador} {'✅' if odds_aprovado else '❌'}")
    print(f"")
    print(f"         🎾 DF: {df_value} {'✅' if df_aprovado else '❌'}")
    
    if odds_aprovado and df_aprovado:
        print(f"")
        print(f"         ✅ ALAVANCAGEM APROVADA!")
        return {
            'partida_id': event_id,
            'liga': partida['liga'],
            'jogador': jogador_target['nome'],
            'oponente': jogador_target['oponente'],
            'placar': partida['placar'],
            'fase_timing': partida['fase'],
            'prioridade_timing': partida['prioridade'],
            'tipo': jogador_target['tipo'],
            'ev': jogador_target['dados']['ev'],
            'momentum': jogador_target['dados']['momentum_score'],
            'double_faults': jogador_target['dados']['double_faults'],
            'win_1st_serve': jogador_target['dados']['win_1st_serve'],
            'estrategia': 'ALAVANCAGEM',
            'ms_casa': ms_casa,
            'ms_visitante': ms_visitante,
            'w1s_casa': w1s_casa,
            'w1s_visitante': w1s_visitante
        }
    else:
        print(f"")
        print(f"         ❌ ALAVANCAGEM rejeitada na validação final")
        return None

def testar_estrategia_tradicional(partida, dados_casa, dados_visitante, ev_principal, event_id, jogador_casa, jogador_visitante):
    """Testa se a partida atende aos critérios da estratégia TRADICIONAL"""
    
    # Critérios específicos da TRADICIONAL
    CRITERIOS = {
        'EV_MINIMO': 0.15,
        'MOMENTUM_SCORE_MINIMO': 55,
        'WIN_1ST_SERVE_MINIMO': 55,
        'DOUBLE_FAULTS_MAXIMO': 5,
        'ODDS_MIN': 1.80,
        'ODDS_MAX': 2.50,
        'PRIORIDADE_MINIMA': 4,       # 2º SET MEIO/FINAL - TIMING RIGOROSO
        'NOME': 'TRADICIONAL'
    }
    
    print(f"      📊 Testando TRADICIONAL...")
    
    # 1. VALIDAÇÃO DE TIMING - PRIORIDADE MÍNIMA
    prioridade_partida = partida.get('prioridade', 0)
    prioridade_minima = CRITERIOS['PRIORIDADE_MINIMA']
    timing_aprovado = prioridade_partida >= prioridade_minima
    
    print(f"         ⏰ Timing: Prioridade {prioridade_partida} {'✅' if timing_aprovado else '❌'} (≥{prioridade_minima})")
    
    if not timing_aprovado:
        print(f"         ❌ TRADICIONAL rejeitada - timing insuficiente")
        return None
    
    # Dados dos jogadores
    ms_casa = dados_casa.get('momentum_score', 0)
    ms_visitante = dados_visitante.get('momentum_score', 0)
    w1s_casa = float(dados_casa.get('win_1st_serve', 0)) if dados_casa.get('win_1st_serve') else 0
    w1s_visitante = float(dados_visitante.get('win_1st_serve', 0)) if dados_visitante.get('win_1st_serve') else 0
    
    # Validação individual
    casa_dominante = (ms_casa >= CRITERIOS['MOMENTUM_SCORE_MINIMO']) and (w1s_casa >= CRITERIOS['WIN_1ST_SERVE_MINIMO'])
    visitante_dominante = (ms_visitante >= CRITERIOS['MOMENTUM_SCORE_MINIMO']) and (w1s_visitante >= CRITERIOS['WIN_1ST_SERVE_MINIMO'])
    dominancia_aprovada = casa_dominante or visitante_dominante
    ev_aprovado = ev_principal >= CRITERIOS['EV_MINIMO']
    
    print(f"")
    print(f"         📊 Dominância: Casa={'✅' if casa_dominante else '❌'}, Visitante={'✅' if visitante_dominante else '❌'}")
    print(f"")
    print(f"         ⚡ EV: {ev_principal:.3f} {'✅' if ev_aprovado else '❌'} (≥{CRITERIOS['EV_MINIMO']})")
    
    if not (dominancia_aprovada and ev_aprovado):
        print(f"")
        print(f"         ❌ TRADICIONAL rejeitada")
        return None
    
    # Selecionar jogador target (mesmo código da alavancagem)
    if casa_dominante and not visitante_dominante:
        jogador_target = {'dados': dados_casa, 'nome': jogador_casa, 'oponente': jogador_visitante, 'tipo': 'HOME'}
    elif visitante_dominante and not casa_dominante:
        jogador_target = {'dados': dados_visitante, 'nome': jogador_visitante, 'oponente': jogador_casa, 'tipo': 'AWAY'}
    else:
        if ms_casa >= ms_visitante:
            jogador_target = {'dados': dados_casa, 'nome': jogador_casa, 'oponente': jogador_visitante, 'tipo': 'HOME'}
        else:
            jogador_target = {'dados': dados_visitante, 'nome': jogador_visitante, 'oponente': jogador_casa, 'tipo': 'AWAY'}
    
    # Validações finais - buscar odds atuais
    odds_atuais = buscar_odds_partida_atual(event_id)
    odds_jogador = odds_atuais['casa'] if jogador_target['tipo'] == 'HOME' else odds_atuais['visitante']
    if odds_jogador != 'N/A':
        try:
            odds_float = float(odds_jogador)
            odds_aprovado = CRITERIOS['ODDS_MIN'] <= odds_float <= CRITERIOS['ODDS_MAX']
        except:
            odds_aprovado = False
    else:
        odds_aprovado = False
    
    df_value = int(jogador_target['dados'].get('double_faults', 0)) if jogador_target['dados'].get('double_faults') else 0
    df_aprovado = df_value <= CRITERIOS['DOUBLE_FAULTS_MAXIMO']
    
    print(f"")
    print(f"         💰 Odds: {odds_jogador} {'✅' if odds_aprovado else '❌'}")
    print(f"")
    print(f"         🎾 DF: {df_value} {'✅' if df_aprovado else '❌'}")
    
    if odds_aprovado and df_aprovado:
        print(f"")
        print(f"         ✅ TRADICIONAL APROVADA!")
        return {
            'partida_id': event_id,
            'liga': partida['liga'],
            'jogador': jogador_target['nome'],
            'oponente': jogador_target['oponente'],
            'placar': partida['placar'],
            'fase_timing': partida['fase'],
            'prioridade_timing': partida['prioridade'],
            'tipo': jogador_target['tipo'],
            'ev': jogador_target['dados']['ev'],
            'momentum': jogador_target['dados']['momentum_score'],
            'double_faults': jogador_target['dados']['double_faults'],
            'win_1st_serve': jogador_target['dados']['win_1st_serve'],
            'estrategia': 'TRADICIONAL',
            'ms_casa': ms_casa,
            'ms_visitante': ms_visitante,
            'w1s_casa': w1s_casa,
            'w1s_visitante': w1s_visitante
        }
    else:
        print(f"")
        print(f"         ❌ TRADICIONAL rejeitada na validação final")
        return None

def testar_estrategia_invertida(partida, dados_casa, dados_visitante, is_alta_tensao, event_id, jogador_casa, jogador_visitante):
    """Testa se a partida atende aos critérios da estratégia INVERTIDA"""
    
    # Critérios específicos da INVERTIDA
    CRITERIOS = {
        'EV_MINIMO': 0.1,
        'MOMENTUM_SCORE_MINIMO': 55,
        'WIN_1ST_SERVE_MINIMO': 55,
        'DOUBLE_FAULTS_MAXIMO': 6,
        'ODDS_MIN': 1.80,
        'ODDS_MAX': 2.50,
        'PRIORIDADE_MINIMA': 4,       # 2º SET MEIO/FINAL - TIMING RIGOROSO
        'NOME': 'INVERTIDA'
    }
    
    print(f"      🔄 Testando INVERTIDA...")
    
    # 1. VALIDAÇÃO DE TIMING - PRIORIDADE MÍNIMA
    prioridade_partida = partida.get('prioridade', 0)
    prioridade_minima = CRITERIOS['PRIORIDADE_MINIMA']
    timing_aprovado = prioridade_partida >= prioridade_minima
    
    print(f"         ⏰ Timing: Prioridade {prioridade_partida} {'✅' if timing_aprovado else '❌'} (≥{prioridade_minima})")
    
    if not timing_aprovado:
        print(f"         ❌ INVERTIDA rejeitada - timing insuficiente")
        return None
    
    # INVERTIDA só ativa em alta tensão
    if not is_alta_tensao:
        print(f"         ❌ INVERTIDA rejeitada - não é alta tensão")
        return None
    
    # Dados dos jogadores
    ms_casa = dados_casa.get('momentum_score', 0)
    ms_visitante = dados_visitante.get('momentum_score', 0)
    w1s_casa = float(dados_casa.get('win_1st_serve', 0)) if dados_casa.get('win_1st_serve') else 0
    w1s_visitante = float(dados_visitante.get('win_1st_serve', 0)) if dados_visitante.get('win_1st_serve') else 0
    
    # Validação individual
    casa_dominante = (ms_casa >= CRITERIOS['MOMENTUM_SCORE_MINIMO']) and (w1s_casa >= CRITERIOS['WIN_1ST_SERVE_MINIMO'])
    visitante_dominante = (ms_visitante >= CRITERIOS['MOMENTUM_SCORE_MINIMO']) and (w1s_visitante >= CRITERIOS['WIN_1ST_SERVE_MINIMO'])
    dominancia_aprovada = casa_dominante or visitante_dominante
    
    ev_principal = max(dados_casa.get('ev', 0), dados_visitante.get('ev', 0))
    ev_aprovado = ev_principal >= CRITERIOS['EV_MINIMO']
    
    print(f"")
    print(f"         📊 Dominância: Casa={'✅' if casa_dominante else '❌'}, Visitante={'✅' if visitante_dominante else '❌'}")
    print(f"")
    print(f"         ⚡ EV: {ev_principal:.3f} {'✅' if ev_aprovado else '❌'} (≥{CRITERIOS['EV_MINIMO']})")
    print(f"")
    print(f"         🔥 Alta Tensão: ✅")
    
    if not (dominancia_aprovada and ev_aprovado):
        print(f"")
        print(f"         ❌ INVERTIDA rejeitada")
        return None
    
    # Selecionar jogador target (mesmo código das outras)
    if casa_dominante and not visitante_dominante:
        jogador_target = {'dados': dados_casa, 'nome': jogador_casa, 'oponente': jogador_visitante, 'tipo': 'HOME'}
    elif visitante_dominante and not casa_dominante:
        jogador_target = {'dados': dados_visitante, 'nome': jogador_visitante, 'oponente': jogador_casa, 'tipo': 'AWAY'}
    else:
        if ms_casa >= ms_visitante:
            jogador_target = {'dados': dados_casa, 'nome': jogador_casa, 'oponente': jogador_visitante, 'tipo': 'HOME'}
        else:
            jogador_target = {'dados': dados_visitante, 'nome': jogador_visitante, 'oponente': jogador_casa, 'tipo': 'AWAY'}
    
    # Validações finais - buscar odds atuais
    odds_atuais = buscar_odds_partida_atual(event_id)
    odds_jogador = odds_atuais['casa'] if jogador_target['tipo'] == 'HOME' else odds_atuais['visitante']
    if odds_jogador != 'N/A':
        try:
            odds_float = float(odds_jogador)
            odds_aprovado = CRITERIOS['ODDS_MIN'] <= odds_float <= CRITERIOS['ODDS_MAX']
        except:
            odds_aprovado = False
    else:
        odds_aprovado = False
    
    df_value = int(jogador_target['dados'].get('double_faults', 0)) if jogador_target['dados'].get('double_faults') else 0
    df_aprovado = df_value <= CRITERIOS['DOUBLE_FAULTS_MAXIMO']
    
    print(f"")
    print(f"         💰 Odds: {odds_jogador} {'✅' if odds_aprovado else '❌'}")
    print(f"")
    print(f"         🎾 DF: {df_value} {'✅' if df_aprovado else '❌'}")
    
    if odds_aprovado and df_aprovado:
        print(f"")
        print(f"         ✅ INVERTIDA APROVADA!")
        return {
            'partida_id': event_id,
            'liga': partida['liga'],
            'jogador': jogador_target['nome'],
            'oponente': jogador_target['oponente'],
            'placar': partida['placar'],
            'fase_timing': partida['fase'],
            'prioridade_timing': partida['prioridade'],
            'tipo': jogador_target['tipo'],
            'ev': jogador_target['dados']['ev'],
            'momentum': jogador_target['dados']['momentum_score'],
            'double_faults': jogador_target['dados']['double_faults'],
            'win_1st_serve': jogador_target['dados']['win_1st_serve'],
            'estrategia': 'INVERTIDA',
            'ms_casa': ms_casa,
            'ms_visitante': ms_visitante,
            'w1s_casa': w1s_casa,
            'w1s_visitante': w1s_visitante
        }
    else:
        print(f"")
        print(f"         ❌ INVERTIDA rejeitada na validação final")
        return None

def analisar_ev_partidas():
    """Analisa EV das partidas com filtros refinados."""
    
    print("🎾 SELEÇÃO FINAL - ANÁLISE REFINADA COM MÚLTIPLOS FILTROS")
    print("=" * 70)
    print("🔍 Aplicando filtros: ESTRATÉGIAS INDEPENDENTES")
    
    # 🚀 ESTRATÉGIA ALAVANCAGEM - Para EVs muito altos (independente)
    CRITERIOS_ALAVANCAGEM = {
        'EV_MINIMO': 0.1,             # EVs baixos mas válidos (0.1+)
        'EV_MAXIMO': 50.0,            # Sem limite superior
        'MOMENTUM_SCORE_MINIMO': 55,  # MS ≥ 55% (MESMO JOGADOR deve ter MS E W1S ≥ 55%)
        'WIN_1ST_SERVE_MINIMO': 55,   # W1S ≥ 55% (MESMO JOGADOR deve ter MS E W1S ≥ 55%)
        'DOUBLE_FAULTS_MAXIMO': 8,    # DF ≤ 8 (RELAXADO)
        'ODDS_MIN': 1.20,             # Odds mínima
        'ODDS_MAX': 1.50,             # Odds máxima para alavancagem
        'PRIORIDADE_MINIMA': 4,       # 2º SET MEIO/FINAL - TIMING RIGOROSO
        'NOME': 'ALAVANCAGEM'
    }

    # 📊 ESTRATÉGIA TRADICIONAL - Para situações normais e equilibradas (independente)
    CRITERIOS_TRADICIONAL = {
        'EV_MINIMO': 0.15,            # EV moderado
        'EV_MAXIMO': 2.0,             # Limite moderado
        'MOMENTUM_SCORE_MINIMO': 55,  # MS ≥ 55% (MESMO JOGADOR deve ter MS E W1S ≥ 55%)
        'WIN_1ST_SERVE_MINIMO': 55,   # W1S ≥ 55% (MESMO JOGADOR deve ter MS E W1S ≥ 55%)
        'DOUBLE_FAULTS_MAXIMO': 5,    # DF ≤ 5 (moderado)
        'ODDS_MIN': 1.80,             # Odds mínima
        'ODDS_MAX': 2.50,             # Odds máxima para tradicional
        'PRIORIDADE_MINIMA': 4,       # 2º SET MEIO/FINAL - TIMING RIGOROSO
        'NOME': 'TRADICIONAL'
    }

    # 🔄 ESTRATÉGIA INVERTIDA - Para fadiga e 3º sets (independente)
    CRITERIOS_INVERTIDOS = {
        'EV_MINIMO': 0.1,             # EV baixo (situações especiais)
        'EV_MAXIMO': 3.0,             # Permite EVs altos
        'MOMENTUM_SCORE_MINIMO': 55,  # MS ≥ 55% (MESMO JOGADOR deve ter MS E W1S ≥ 55%)
        'WIN_1ST_SERVE_MINIMO': 55,   # W1S ≥ 55% (MESMO JOGADOR deve ter MS E W1S ≥ 55%)
        'DOUBLE_FAULTS_MAXIMO': 6,    # DF ≤ 6 (relaxado)
        'ODDS_MIN': 1.80,             # Odds mínima
        'ODDS_MAX': 2.50,             # Odds máxima
        'PRIORIDADE_MINIMA': 4,       # 2º SET MEIO/FINAL - TIMING RIGOROSO
        'NOME': 'INVERTIDA'
    }
    
    print("🎯 ESTRATÉGIAS INDEPENDENTES - Cada uma com seus critérios:")
    print(f"   🚀 ALAVANCAGEM: EV ≥ {CRITERIOS_ALAVANCAGEM['EV_MINIMO']}, MESMO JOGADOR: MS ≥ {CRITERIOS_ALAVANCAGEM['MOMENTUM_SCORE_MINIMO']}% AND W1S ≥ {CRITERIOS_ALAVANCAGEM['WIN_1ST_SERVE_MINIMO']}%")
    print(f"   📊 TRADICIONAL: EV ≥ {CRITERIOS_TRADICIONAL['EV_MINIMO']}, MESMO JOGADOR: MS ≥ {CRITERIOS_TRADICIONAL['MOMENTUM_SCORE_MINIMO']}% AND W1S ≥ {CRITERIOS_TRADICIONAL['WIN_1ST_SERVE_MINIMO']}%")
    print(f"   🔄 INVERTIDA: EV ≥ {CRITERIOS_INVERTIDOS['EV_MINIMO']}, MESMO JOGADOR: MS ≥ {CRITERIOS_INVERTIDOS['MOMENTUM_SCORE_MINIMO']}% AND W1S ≥ {CRITERIOS_INVERTIDOS['WIN_1ST_SERVE_MINIMO']}%")
    
    print("🔴 FILTRO DE TIMING ULTRA RIGOROSO ATIVADO")
    print("============================================================")
    print("⏰ TIMING ATUALIZADO: PRIORIDADE ≥ 4 (2º SET MEIO/FINAL)")
    print("🎯 Apenas partidas com prioridade 4 ou 5 serão analisadas")
    print("⚡ Mudança: 3→4 = Filtro mais restritivo para maior precisão")
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
        
        # 🎯 NOVA ABORDAGEM: VALIDAÇÃO POR PARTIDA (DOMINÂNCIA)
        # Coletar dados de AMBOS os jogadores primeiro
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
        
        # 🚀 SISTEMA PARALELO: TESTAR TODAS AS ESTRATÉGIAS INDEPENDENTEMENTE
        oportunidades_partida = []
        
        print(f"📊 Testando TODAS as estratégias em paralelo...")
        print(f"   📈 EV Principal: {ev_principal:.3f}")
        print(f"   🎯 Alta Tensão: {'✅' if is_alta_tensao else '❌'}")
        
        # 1️⃣ TESTAR ESTRATÉGIA ALAVANCAGEM
        oportunidade_alavancagem = testar_estrategia_alavancagem(
            partida, dados_casa, dados_visitante, ev_principal, event_id, jogador_casa, jogador_visitante
        )
        if oportunidade_alavancagem:
            oportunidades_partida.append(oportunidade_alavancagem)
            
        # 2️⃣ TESTAR ESTRATÉGIA TRADICIONAL  
        oportunidade_tradicional = testar_estrategia_tradicional(
            partida, dados_casa, dados_visitante, ev_principal, event_id, jogador_casa, jogador_visitante
        )
        if oportunidade_tradicional:
            oportunidades_partida.append(oportunidade_tradicional)
            
        # 3️⃣ TESTAR ESTRATÉGIA INVERTIDA
        oportunidade_invertida = testar_estrategia_invertida(
            partida, dados_casa, dados_visitante, is_alta_tensao, event_id, jogador_casa, jogador_visitante
        )
        if oportunidade_invertida:
            oportunidades_partida.append(oportunidade_invertida)
        
        # Adicionar TODAS as oportunidades encontradas desta partida
        if oportunidades_partida:
            oportunidades_finais.extend(oportunidades_partida)
            estrategias = [op['estrategia'] for op in oportunidades_partida]
            print(f"   ✅ {len(oportunidades_partida)} OPORTUNIDADE(S) APROVADA(S): {', '.join(estrategias)}")
        else:
            print(f"   ❌ Nenhuma estratégia aprovada para esta partida")
            
    
    # Resumo final
    print("\n" + "=" * 80)
    print(f"🎯 RESULTADO FINAL: {len(oportunidades_finais)} oportunidades encontradas")
    
    for oportunidade in oportunidades_finais:
        print(f"✅ {oportunidade['estrategia']}: {oportunidade['jogador']} vs {oportunidade['oponente']} (EV: {oportunidade['ev']:.3f})")
    
    print("=" * 80)
    return oportunidades_finais

if __name__ == "__main__":
    oportunidades = analisar_ev_partidas()
    print(f"Total de oportunidades: {len(oportunidades)}")
