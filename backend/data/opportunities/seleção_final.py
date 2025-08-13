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
                
                # Aviso suprimido para logs mais limpos
        
        # Aviso suprimido para logs mais limpos
        return {'jogador1_odd': 'N/A', 'jogador2_odd': 'N/A'}
        
    except Exception as e:
        print(f"❌ Erro ao buscar odds do evento {event_id}: {e}")
        return {'jogador1_odd': 'N/A', 'jogador2_odd': 'N/A'}
        
    except Exception as e:
        return {'jogador1_odd': 'N/A', 'jogador2_odd': 'N/A'}

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
        response = requests.get(url_inplay, params=params, timeout=15)  # Aumentar timeout
        
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

def buscar_stats_detalhadas(event_id, api_key, base_url):
    """Busca estatísticas detalhadas do evento (baseado em ev.py)."""
    url = f"{base_url}/v3/event/view"
    params = {
        'event_id': event_id,
        'token': api_key
    }
    
    try:
        response = requests.get(url, params=params, timeout=15)  # Aumentar timeout
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

def calcular_momentum_score(stats):
    """Calcula o momentum score baseado nas estatísticas."""
    
    try:
        # Momentum para casa (home)
        aces_home = stats.get('aces_home', 0)
        df_home = stats.get('double_faults_home', 0)
        w1s_home = stats.get('win_1st_serve_home', 0)
        
        # Momentum para visitante (away)
        aces_away = stats.get('aces_away', 0)
        df_away = stats.get('double_faults_away', 0)
        w1s_away = stats.get('win_1st_serve_away', 0)
        
        # Fórmula do momentum: (Aces - Double Faults) + (Win 1st Serve %)
        momentum_home = (aces_home - df_home) + (w1s_home if w1s_home <= 100 else w1s_home/100)
        momentum_away = (aces_away - df_away) + (w1s_away if w1s_away <= 100 else w1s_away/100)
        
        # Converter para porcentagem (0-100)
        total_momentum = momentum_home + momentum_away
        if total_momentum > 0:
            momentum_home_pct = (momentum_home / total_momentum) * 100
            momentum_away_pct = (momentum_away / total_momentum) * 100
        else:
            momentum_home_pct = 50
            momentum_away_pct = 50
        
        return momentum_home_pct, momentum_away_pct
    
    except Exception as e:
        return 50, 50

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

def analisar_ev_partidas():
    """Analisa EV das partidas com filtros refinados."""
    
    print("🎾 SELEÇÃO FINAL - ANÁLISE REFINADA COM MÚLTIPLOS FILTROS")
    print("=" * 70)
    print("🔍 Aplicando filtros: ESTRATÉGIAS INDEPENDENTES")
    
    # 🚀 ESTRATÉGIA ALAVANCAGEM - Para EVs muito altos (independente)
    CRITERIOS_ALAVANCAGEM = {
        'EV_MINIMO': 0.1,             # EVs baixos mas válidos (0.1+)
        'EV_MAXIMO': 50.0,            # Sem limite superior
        'MOMENTUM_SCORE_MINIMO': 55,  # MS ≥ 55% (EQUILIBRADO)
        'WIN_1ST_SERVE_MINIMO': 55,   # W1S ≥ 55% (EQUILIBRADO)
        'DOUBLE_FAULTS_MAXIMO': 8,    # DF ≤ 8 (RELAXADO)
        'ODDS_MIN': 1.20,             # Odds mínima
        'ODDS_MAX': 1.50,             # Odds máxima para alavancagem
        'PRIORIDADE_MINIMA': 0,       # SEM RESTRIÇÃO DE TIMING - 24H LIBERADO
        'NOME': 'ALAVANCAGEM'
    }

    # 📊 ESTRATÉGIA TRADICIONAL - Para situações normais e equilibradas (independente)
    CRITERIOS_TRADICIONAL = {
        'EV_MINIMO': 0.15,            # EV moderado
        'EV_MAXIMO': 2.0,             # Limite moderado
        'MOMENTUM_SCORE_MINIMO': 55,  # MS ≥ 55% (equilibrado)
        'WIN_1ST_SERVE_MINIMO': 55,   # W1S ≥ 55% (equilibrado)
        'DOUBLE_FAULTS_MAXIMO': 5,    # DF ≤ 5 (moderado)
        'ODDS_MIN': 1.80,             # Odds mínima
        'ODDS_MAX': 2.50,             # Odds máxima para tradicional
        'PRIORIDADE_MINIMA': 0,       # SEM RESTRIÇÃO DE TIMING - 24H LIBERADO
        'NOME': 'TRADICIONAL'
    }

    # 🔄 ESTRATÉGIA INVERTIDA - Para fadiga e 3º sets (independente)
    CRITERIOS_INVERTIDOS = {
        'EV_MINIMO': 0.1,             # EV baixo (situações especiais)
        'EV_MAXIMO': 3.0,             # Permite EVs altos
        'MOMENTUM_SCORE_MINIMO': 55,  # MS ≥ 55% (EQUILIBRADO)
        'WIN_1ST_SERVE_MINIMO': 55,   # W1S ≥ 55% (EQUILIBRADO)
        'DOUBLE_FAULTS_MAXIMO': 6,    # DF ≤ 6 (relaxado)
        'ODDS_MIN': 1.80,             # Odds mínima
        'ODDS_MAX': 2.50,             # Odds máxima
        'PRIORIDADE_MINIMA': 0,       # SEM RESTRIÇÃO DE TIMING - 24H LIBERADO
        'NOME': 'INVERTIDA'
    }
    
    print("🎯 ESTRATÉGIAS INDEPENDENTES - Cada uma com seus critérios:")
    print(f"   🚀 ALAVANCAGEM: EV ≥ {CRITERIOS_ALAVANCAGEM['EV_MINIMO']}, MS ≥ {CRITERIOS_ALAVANCAGEM['MOMENTUM_SCORE_MINIMO']}%, W1S ≥ {CRITERIOS_ALAVANCAGEM['WIN_1ST_SERVE_MINIMO']}%")
    print(f"   📊 TRADICIONAL: EV ≥ {CRITERIOS_TRADICIONAL['EV_MINIMO']}, MS ≥ {CRITERIOS_TRADICIONAL['MOMENTUM_SCORE_MINIMO']}%, W1S ≥ {CRITERIOS_TRADICIONAL['WIN_1ST_SERVE_MINIMO']}%")
    print(f"   🔄 INVERTIDA: EV ≥ {CRITERIOS_INVERTIDOS['EV_MINIMO']}, MS ≥ {CRITERIOS_INVERTIDOS['MOMENTUM_SCORE_MINIMO']}%, W1S ≥ {CRITERIOS_INVERTIDOS['WIN_1ST_SERVE_MINIMO']}%")
    
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
    
    def verificar_sets_empatados(placar):
        """Verifica se os sets estão empatados (1-1)"""
        if not placar or ',' not in placar:
            return False
        try:
            sets = placar.split(',')
            if len(sets) >= 2:
                vitorias_home = vitorias_away = 0
                for set_score in sets[:-1]:
                    if '-' in set_score:
                        home, away = set_score.split('-')
                        if int(home.strip()) > int(away.strip()):
                            vitorias_home += 1
                        else:
                            vitorias_away += 1
                return vitorias_home == vitorias_away
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
    
    # NOVO: Salvar partidas aprovadas no timing para o dashboard
    if DASHBOARD_DISPONIVEL and partidas_timing:
        for partida in partidas_timing:
            try:
                jogador1 = partida.get('jogador_casa', 'Jogador 1')
                jogador2 = partida.get('jogador_visitante', 'Jogador 2')
                event_id = partida.get('id', '')
                print(f"🎯 Salvando para dashboard: {jogador1} vs {jogador2}")
                
                # Coletar estatísticas reais dos jogadores
                stats_reais = {'stats_jogador1': {}, 'stats_jogador2': {}}
                if event_id:
                    try:
                        # Importar função de coleta de dados da API
                        import sys
                        import os
                        sys.path.append(os.path.dirname(os.path.dirname(__file__)))
                        
                        # Carregar configurações da API
                        try:
                            # Corrigir import para nova estrutura
                            import json
                            from pathlib import Path
                            config_path = Path(__file__).parent.parent.parent / 'config' / 'config.json'
                            with open(config_path, 'r', encoding='utf-8') as f:
                                config = json.load(f)
                            api_key = config.get('api_key')
                            base_url = config.get('api_base_url')
                        except:
                            # Fallback para config manual
                            api_key = '226997-BVn3XP4cGLAUfL'
                            base_url = 'https://api.b365api.com'
                        
                        # 1. Buscar odds da API
                        if api_key and base_url:
                            print(f"🎲 Coletando odds para evento {event_id}...")
                            odds_info = buscar_odds_evento(event_id, api_key, base_url)
                            
                            # Adicionar odds reais à partida
                            if odds_info['jogador1_odd'] != 'N/A' and odds_info['jogador1_odd'] != '-':
                                try:
                                    partida['odds_casa'] = float(odds_info['jogador1_odd'])
                                    print(f"✅ Odd Casa: {odds_info['jogador1_odd']}")
                                except:
                                    pass
                                    
                            if odds_info['jogador2_odd'] != 'N/A' and odds_info['jogador2_odd'] != '-':
                                try:
                                    partida['odds_visitante'] = float(odds_info['jogador2_odd'])
                                    print(f"✅ Odd Visitante: {odds_info['jogador2_odd']}")
                                except:
                                    pass
                        
                        # 2. Coletar estatísticas
                        # Corrigir import para nova estrutura - usar import absoluto
                        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
                        from backend.core.extrair_stats_jogadores import extrair_stats_completas
                        
                        print(f"📊 Coletando estatísticas reais para evento {event_id}...")
                        stats_reais = extrair_stats_completas(event_id)
                        
                        if stats_reais and stats_reais.get('stats_jogador1'):
                            j1_stats = stats_reais['stats_jogador1']
                            j2_stats = stats_reais['stats_jogador2']
                            j1_total = sum([v for v in j1_stats.values() if isinstance(v, (int, float))])
                            j2_total = sum([v for v in j2_stats.values() if isinstance(v, (int, float))])
                            
                            if j1_total > 0 or j2_total > 0:
                                print(f"✅ Estatísticas coletadas: J1 Total={j1_total}, J2 Total={j2_total}")
                            else:
                                print("⚠️ Estatísticas coletadas estão vazias")
                        else:
                            print("⚠️ Nenhuma estatística retornada pela API")
                            
                    except Exception as e:
                        print(f"❌ Erro ao coletar estatísticas: {e}")
                        stats_reais = {'stats_jogador1': {}, 'stats_jogador2': {}}
                
                # 3. Calcular Score Mental usando o detector correto
                try:
                    # Importar detector de vantagem mental
                    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
                    from backend.core.detector_vantagem_mental import DetectorVantagemMental
                    
                    detector = DetectorVantagemMental()
                    
                    # Preparar dados para análise mental
                    partida_data = {
                        'favorito': {
                            'nome': jogador1 if partida.get('odds_casa', 2.0) < partida.get('odds_visitante', 2.0) else jogador2,
                            'odd': min(partida.get('odds_casa', 2.0), partida.get('odds_visitante', 2.0))
                        },
                        'adversario': {
                            'nome': jogador2 if partida.get('odds_casa', 2.0) < partida.get('odds_visitante', 2.0) else jogador1,
                            'odd': max(partida.get('odds_casa', 2.0), partida.get('odds_visitante', 2.0))
                        },
                        'score': partida.get('placar', '0-0')
                    }
                    
                    # Calcular score mental real
                    analise_mental = detector.analisar_partida(partida_data)
                    score_mental_real = analise_mental.get('score_mental', 0)
                    
                    print(f"🧠 Score Mental calculado: {score_mental_real} pontos")
                    
                    # Calcular EV principal da partida (usando momentum_score se disponível)
                    ev_principal = 0.0
                    try:
                        # *** CORREÇÃO: Usar sistema de coleta interno para calcular EV correto ***
                        
                        # Buscar stats calculados da partida usando função disponível
                        stats_info = buscar_stats_detalhadas(partida['id'], api_key, base_url)
                        
                        # Buscar odds da partida usando função já disponível
                        odds_info = buscar_odds_evento(partida['id'], api_key, base_url)
                        
                        # Debug: Mostrar dados coletados
                        print(f"🔍 Stats coletados: MS1={stats_info.get('jogador1_ms', '0')}, MS2={stats_info.get('jogador2_ms', '0')}")
                        print(f"🔍 Odds coletados: Odd1={odds_info.get('jogador1_odd', 'N/A')}, Odd2={odds_info.get('jogador2_odd', 'N/A')}")
                        
                        # Calcular EV para jogador HOME (casa)
                        odd1 = odds_info.get('jogador1_odd', 'N/A')
                        ms1 = stats_info.get('jogador1_ms', '50')
                        
                        if (odd1 not in ['N/A', '-', None, 'N/A'] and 
                            ms1 not in ['50', '0', None] and
                            str(ms1) != '50'):
                            try:
                                odd_casa = float(odd1)
                                ms_casa = float(ms1)
                                
                                # Verificar se valores são válidos
                                if odd_casa > 1.0 and 0 < ms_casa <= 100 and ms_casa != 50:
                                    ev_casa = calcular_ev(ms_casa, odd_casa)
                                    ev_principal = max(ev_principal, ev_casa)
                                    print(f"📊 EV Jogador Casa: MS={ms_casa}%, Odd={odd_casa}, EV={ev_casa:.3f}")
                                else:
                                    print(f"⚠️ Valores inválidos - Casa: Odd={odd_casa}, MS={ms_casa}")
                            except (ValueError, TypeError) as e:
                                print(f"⚠️ Erro ao converter valores casa: Odd={odd1}, MS={ms1} - {e}")
                        else:
                            print(f"⚠️ Dados casa insuficientes: Odd={odd1}, MS={ms1}")
                        
                        # Calcular EV para jogador AWAY (visitante)
                        odd2 = odds_info.get('jogador2_odd', 'N/A')
                        ms2 = stats_info.get('jogador2_ms', '50')
                        
                        if (odd2 not in ['N/A', '-', None, 'N/A'] and 
                            ms2 not in ['50', '0', None] and
                            str(ms2) != '50'):
                            try:
                                odd_visitante = float(odd2)
                                ms_visitante = float(ms2)
                                
                                # Verificar se valores são válidos
                                if odd_visitante > 1.0 and 0 < ms_visitante <= 100 and ms_visitante != 50:
                                    ev_visitante = calcular_ev(ms_visitante, odd_visitante)
                                    ev_principal = max(ev_principal, ev_visitante)
                                    print(f"📊 EV Jogador Visitante: MS={ms_visitante}%, Odd={odd_visitante}, EV={ev_visitante:.3f}")
                                else:
                                    print(f"⚠️ Valores inválidos - Visitante: Odd={odd_visitante}, MS={ms_visitante}")
                            except (ValueError, TypeError) as e:
                                print(f"⚠️ Erro ao converter valores visitante: Odd={odd2}, MS={ms2} - {e}")
                        else:
                            print(f"⚠️ Dados visitante insuficientes: Odd={odd2}, MS={ms2}")
                            
                        print(f"📊 EV Principal calculado: {ev_principal:.3f}")
                            
                    except Exception as e:
                        print(f"⚠️ Erro ao calcular EV principal: {e}")
                        ev_principal = 0.0
                    
                except Exception as e:
                    print(f"⚠️ Erro ao calcular score mental: {e}")
                    score_mental_real = 0
                    ev_principal = 0.0

                dashboard_logger.log_partida_analisada(
                    jogador1=jogador1,
                    jogador2=jogador2,
                    placar=partida.get('placar', '0-0'),
                    odds1=partida.get('odds_casa', 2.0),
                    odds2=partida.get('odds_visitante', 2.0),
                    ev=ev_principal,  # Usar EV calculado
                    momentum_score=0.0,  # Será calculado depois
                    timing_priority=partida.get('prioridade', 0),
                    mental_score=score_mental_real,  # Usar score mental correto
                    decisao='APROVADO_TIMING',
                    motivo=f"Passou no filtro de timing - Prioridade {partida.get('prioridade', 0)}/5",
                    stats_jogador1=stats_reais.get('stats_jogador1', {}),
                    stats_jogador2=stats_reais.get('stats_jogador2', {})
                )
            except Exception as e:
                print(f"⚠️ Erro ao salvar partida para dashboard: {e}")
                print(f"   Dados da partida: {partida}")
    
    print("🔄 Analisando dados individuais de cada jogador...")
    print("=" * 80)
    
    oportunidades_finais = []
    
    # Aplicar filtros refinados nas partidas aprovadas por timing
    for partida in partidas_timing:
        event_id = partida['id']
        jogador_casa = partida['jogador_casa']
        jogador_visitante = partida['jogador_visitante']
        
        print(f"📊 Analisando: {jogador_casa} vs {jogador_visitante}")
        
        # Analisar cada jogador individualmente
        jogadores = [
            {'nome': jogador_casa, 'oponente': jogador_visitante, 'tipo': 'HOME'},
            {'nome': jogador_visitante, 'oponente': jogador_casa, 'tipo': 'AWAY'}
        ]
        
        for jogador_info in jogadores:
            # Buscar dados individuais do jogador
            dados_jogador = buscar_dados_jogador(jogador_info['nome'], event_id)
            time.sleep(0.2)  # Rate limiting otimizado - reduzido de 0.5 para 0.2
            
            # � TIMING LIBERADO 24H - SEM RESTRIÇÕES DE HORÁRIO
            timing_aprovado = True  # SEMPRE APROVADO
            print(f"   🟢 Timing liberado 24h - APROVADO AUTOMATICAMENTE")
            
            # FILTROS ANTI-PROBLEMAS ESPECÍFICOS
            placar = partida.get('placar', '')
            motivos_bloqueio = []
            
            # 🎯 ESTRATÉGIA INVERTIDA - Comentados os bloqueios que não se aplicam
            # Justamente queremos 3º sets e pós tie-breaks para sinais invertidos!
            
            # Verificar 3º set - DESABILITADO para estratégia invertida
            # if verificar_se_e_terceiro_set(placar):
            #     motivos_bloqueio.append("3º set detectado (muito mental)")
            
            # Verificar pós tie-break - DESABILITADO para estratégia invertida  
            # if verificar_pos_tiebreak(placar):
            #     motivos_bloqueio.append("Pós tie-break detectado (fadiga)")
            
            # Verificar sets empatados - DESABILITADO para estratégia invertida
            # if verificar_sets_empatados(placar):
            #     motivos_bloqueio.append("Sets empatados 1-1 (incerteza)")
            
            if motivos_bloqueio:
                print(f"   🚫 BLOQUEADO: {', '.join(motivos_bloqueio)}")
                continue
            
            # 🎯 DETERMINAR QUAL CRITÉRIO USAR BASEADO NA SITUAÇÃO
            placar = partida.get('placar', '')
            is_terceiro_set = verificar_se_e_terceiro_set(placar)
            is_pos_tiebreak = verificar_pos_tiebreak(placar)
            is_alta_tensao = is_terceiro_set or is_pos_tiebreak or partida.get('prioridade', 0) == 5
            
            # Escolher critérios baseados na situação
            if is_alta_tensao:
                criterios = CRITERIOS_INVERTIDOS
                estrategia_tipo = "INVERTIDA (3º set/alta tensão)"
                # Debug suprimido para logs mais limpos
            elif ev_principal >= 3.0:  # Alavancagem para EVs muito altos
                criterios = CRITERIOS_ALAVANCAGEM
                estrategia_tipo = "ALAVANCAGEM (EV muito alto)"
            elif ev_principal >= 0.15:  # Tradicional para EVs moderados
                criterios = CRITERIOS_TRADICIONAL
                estrategia_tipo = "TRADICIONAL (EV moderado)"
            else:
                # EVs baixos (0.1-0.14): usar ALAVANCAGEM
                criterios = CRITERIOS_ALAVANCAGEM
                estrategia_tipo = "ALAVANCAGEM (EV baixo)"
                # Debug suprimido para logs mais limpos
            
            # APLICAR FILTROS BASEADOS NA ESTRATÉGIA ESCOLHIDA
            filtros_aprovados = []
            filtros_rejeitados = []
            
            # Filtro EV: Adaptativo baseado na estratégia
            if is_alta_tensao:
                # Para estratégia invertida: aceitar faixa muito mais ampla
                if criterios['EV_MINIMO'] <= dados_jogador['ev'] <= criterios['EV_MAXIMO']:
                    filtros_aprovados.append(f"EV: {dados_jogador['ev']:.3f} ✅ (estratégia invertida)")
                else:
                    filtros_rejeitados.append(f"EV: {dados_jogador['ev']:.3f} ❌ (faixa invertida: {criterios['EV_MINIMO']} a {criterios['EV_MAXIMO']})")
            else:
                # Para estratégia normal: critérios rigorosos
                if criterios['EV_MINIMO'] <= dados_jogador['ev'] <= 0.50:
                    filtros_aprovados.append(f"EV: {dados_jogador['ev']:.3f} ✅")
                else:
                    filtros_rejeitados.append(f"EV: {dados_jogador['ev']:.3f} ❌ (min {criterios['EV_MINIMO']})")
            
            # Filtro Momentum Score: Apenas mínimo
            if dados_jogador['momentum_score'] >= criterios['MOMENTUM_SCORE_MINIMO']:
                filtros_aprovados.append(f"MS: {dados_jogador['momentum_score']:.1f}% ✅ ({estrategia_tipo})")
            else:
                filtros_rejeitados.append(f"MS: {dados_jogador['momentum_score']:.1f}% ❌ (min {criterios['MOMENTUM_SCORE_MINIMO']}% - {estrategia_tipo})")
            
            # Filtro Double Faults: Adaptativo
            try:
                df_value = int(dados_jogador['double_faults']) if dados_jogador['double_faults'] else 0
                if 0 <= df_value <= criterios['DOUBLE_FAULTS_MAXIMO']:
                    filtros_aprovados.append(f"DF: {df_value} ✅ ({estrategia_tipo})")
                else:
                    filtros_rejeitados.append(f"DF: {df_value} ❌ (max {criterios['DOUBLE_FAULTS_MAXIMO']} - {estrategia_tipo})")
            except (ValueError, TypeError):
                filtros_rejeitados.append(f"DF: dados inválidos ❌")
            
            # Filtro Win 1st Serve: Apenas mínimo
            try:
                w1s_value = float(dados_jogador['win_1st_serve']) if dados_jogador['win_1st_serve'] else 0
                if w1s_value >= criterios['WIN_1ST_SERVE_MINIMO']:
                    filtros_aprovados.append(f"W1S: {w1s_value}% ✅ ({estrategia_tipo})")
                else:
                    filtros_rejeitados.append(f"W1S: {w1s_value}% ❌ (min {criterios['WIN_1ST_SERVE_MINIMO']}% - {estrategia_tipo})")
            except (ValueError, TypeError):
                filtros_rejeitados.append(f"W1S: dados inválidos ❌")
            
            # ⚠️ FILTRO ODDS INDEPENDENTE PARA CADA ESTRATÉGIA (se disponível)
            # Determinar a odd específica do jogador baseado no tipo
            if jogador_info['tipo'] == 'HOME':
                odds_jogador = partida.get('odds_casa', 'N/A')
            else:  # AWAY
                odds_jogador = partida.get('odds_visitante', 'N/A')
            
            if odds_jogador != 'N/A':
                try:
                    odds_float = float(odds_jogador)
                    if criterios['ODDS_MIN'] <= odds_float <= criterios['ODDS_MAX']:
                        filtros_aprovados.append(f"ODDS: {odds_float} ✅ (range {criterios['ODDS_MIN']}-{criterios['ODDS_MAX']} - {estrategia_tipo})")
                    else:
                        filtros_rejeitados.append(f"ODDS: {odds_float} ❌ (range {criterios['ODDS_MIN']}-{criterios['ODDS_MAX']} - {estrategia_tipo})")
                except (ValueError, TypeError):
                    filtros_rejeitados.append(f"ODDS: {odds_jogador} ❌ (inválida)")
            else:
                filtros_rejeitados.append(f"ODDS: N/A ❌ (não disponível)")
            
            # Se passou em TODOS os filtros (agora são 6 filtros independentes: EV, MS, DF, W1S, ODDS, TIMING)
            if len(filtros_aprovados) == 6 and len(filtros_rejeitados) == 0:
                oportunidade = {
                    'partida_id': event_id,
                    'liga': partida['liga'],
                    'jogador': jogador_info['nome'],
                    'oponente': jogador_info['oponente'],
                    'placar': partida['placar'],
                    'fase_timing': partida['fase'],
                    'prioridade_timing': partida['prioridade'],
                    'tipo': jogador_info['tipo'],
                    'ev': dados_jogador['ev'],
                    'momentum': dados_jogador['momentum_score'],
                    'double_faults': dados_jogador['double_faults'],
                    'win_1st_serve': dados_jogador['win_1st_serve'],
                    'filtros_aprovados': filtros_aprovados
                }
                oportunidades_finais.append(oportunidade)
                
                # Debug suprimido - oportunidade encontrada
                pass
            else:
                # Debug suprimido - filtros reprovados  
                pass
        
        print("-" * 60)
    
    # Resumo final
    print("\n" + "=" * 80)
    print("🎯 SELEÇÃO FINAL - OPORTUNIDADES REFINADAS")
    print("=" * 80)
    print(f"✅ Partidas analisadas: {len(partidas_timing)}")
    print(f"🎯 Oportunidades encontradas: {len(oportunidades_finais)}")
    
    if oportunidades_finais:
        # Ordenar por EV (maior primeiro)
        oportunidades_finais.sort(key=lambda x: x['ev'], reverse=True)
        
        print("\n🏆 OPORTUNIDADES APROVADAS EM TODOS OS FILTROS:")
        print("=" * 70)
        
        for i, op in enumerate(oportunidades_finais, 1):
            # Classificar EV
            if op['ev'] >= 0.40:
                emoji_ev = "🟢"
                classe_ev = "EXCELENTE"
            elif op['ev'] >= 0.15:
                emoji_ev = "🔵"
                classe_ev = "ÓTIMO"
            elif op['ev'] >= 0.10:
                emoji_ev = "🟡"
                classe_ev = "BOM"
            elif op['ev'] >= 0.05:
                emoji_ev = "🟠"
                classe_ev = "MARGINAL"
            else:
                emoji_ev = "🟤"
                classe_ev = "BAIXO"
            
            print(f"{emoji_ev} {i}. {op['jogador']} vs {op['oponente']}")
            print(f"      Liga: {op['liga']}")
            print(f"      Placar: {op['placar']} | Fase: {op['fase_timing']} | Timing: {op['prioridade_timing']}/5")
            print(f"      📊 EV: +{op['ev']:.3f} ({classe_ev})")
            print(f"      📈 MS: {op['momentum']:.1f}% | DF: {op['double_faults']} | W1S: {op['win_1st_serve']}%")
            print("")
    else:
        print("\n❌ Nenhuma oportunidade encontrada que passe em TODOS os filtros")
        print("💡 ESTRATÉGIAS INDEPENDENTES IMPLEMENTADAS:")
        print("\n� ALAVANCAGEM (EVs altos ≥0.5):")
        print(f"   • EV: +{CRITERIOS_ALAVANCAGEM['EV_MINIMO']} ou mais")
        print(f"   • Momentum Score: {CRITERIOS_ALAVANCAGEM['MOMENTUM_SCORE_MINIMO']}% (EQUILIBRADO)")
        print(f"   • Win 1st Serve: {CRITERIOS_ALAVANCAGEM['WIN_1ST_SERVE_MINIMO']}% (EQUILIBRADO)")
        print("\n📊 TRADICIONAL (EVs moderados 0.15-2.0):")
        print(f"   • EV: +{CRITERIOS_TRADICIONAL['EV_MINIMO']} a +{CRITERIOS_TRADICIONAL['EV_MAXIMO']}")
        print(f"   • Momentum Score: {CRITERIOS_TRADICIONAL['MOMENTUM_SCORE_MINIMO']}% (EQUILIBRADO)")
        print(f"   • Win 1st Serve: {CRITERIOS_TRADICIONAL['WIN_1ST_SERVE_MINIMO']}% (EQUILIBRADO)")
        print("\n🔄 INVERTIDA (3º sets e alta tensão 0.1-3.0):")
        print(f"   • EV: {CRITERIOS_INVERTIDOS['EV_MINIMO']} a +{CRITERIOS_INVERTIDOS['EV_MAXIMO']}")
        print(f"   • Momentum Score: {CRITERIOS_INVERTIDOS['MOMENTUM_SCORE_MINIMO']}% (EQUILIBRADO)")
        print(f"   • Win 1st Serve: {CRITERIOS_INVERTIDOS['WIN_1ST_SERVE_MINIMO']}% (EQUILIBRADO)")
        print("   • 🎯 OBJETIVO: Aproveitar cenários de alta pressão e fadiga no 3º set")
    
    print(f"\n🕐 Última atualização: {datetime.now().strftime('%H:%M:%S')}")
    
    return oportunidades_finais

if __name__ == "__main__":
    analisar_ev_partidas()