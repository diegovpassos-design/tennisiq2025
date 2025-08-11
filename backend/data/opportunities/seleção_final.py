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

def buscar_odds_evento(event_id, api_key, base_url):
    """Busca as odds de um evento específico (baseado em ev.py)."""
    url = f"{base_url}/v3/event/odds"
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
            
            if 'odds' in results and results['odds']:
                odds_data = results['odds']
                
                if '13_1' in odds_data and odds_data['13_1']:
                    latest_odds = odds_data['13_1'][0]
                    
                    if 'home_od' in latest_odds and 'away_od' in latest_odds:
                        return {
                            'jogador1_odd': latest_odds.get('home_od', 'N/A'),
                            'jogador2_odd': latest_odds.get('away_od', 'N/A')
                        }
        
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
    print("🔍 Aplicando filtros: Timing OBRIGATÓRIO + EV + MS + DF + W1S")
    # FILTROS AJUSTADOS - ESTRATÉGIA RIGOROSA
    CRITERIOS_RIGOROSOS = {
        'EV_MINIMO': 0.15,        # EV mínimo 0.15 (máx 0.50)
        'MOMENTUM_SCORE_MINIMO': 65,  # MS ≥ 65% sem limite máximo
        'WIN_1ST_SERVE_MINIMO': 65,   # W1S ≥ 65% sem limite máximo
        'DOUBLE_FAULTS_MAXIMO': 5,    # DF ≤ 5
        'PRIORIDADE_MINIMA': 3        # Prioridade ≥ 3
    }
    
    # 🎯 CRITÉRIOS ESPECIAIS PARA ESTRATÉGIA INVERTIDA (3º sets e alta tensão)
    CRITERIOS_INVERTIDOS = {
        'EV_MINIMO': -1.0,        # EV relaxado para 3º sets
        'EV_MAXIMO': 2.0,         # Permitir EVs altos também
        'MOMENTUM_SCORE_MINIMO': 55,  # MS ≥ 55% sem limite máximo
        'WIN_1ST_SERVE_MINIMO': 55,   # W1S ≥ 55% sem limite máximo
        'DOUBLE_FAULTS_MAXIMO': 5,    # DF ≤ 5
        'PRIORIDADE_MINIMA': 3        # Prioridade ≥ 3
    }
    
    print("🎯 FILTROS AJUSTADOS - Configuração moderada")
    print(f"   • EV mínimo: {CRITERIOS_RIGOROSOS['EV_MINIMO']}")
    print(f"   • Momentum Score mínimo: {CRITERIOS_RIGOROSOS['MOMENTUM_SCORE_MINIMO']}%")
    print(f"   • Win 1st Serve mínimo: {CRITERIOS_RIGOROSOS['WIN_1ST_SERVE_MINIMO']}%")
    print(f"   • Double Faults máximo: {CRITERIOS_RIGOROSOS['DOUBLE_FAULTS_MAXIMO']}")
    
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
                        # Pegar momentum dos stats_reais se disponível
                        stats_j1 = stats_reais.get('stats_jogador1', {})
                        stats_j2 = stats_reais.get('stats_jogador2', {})
                        
                        momentum_j1 = stats_j1.get('momentum_score', 0)
                        momentum_j2 = stats_j2.get('momentum_score', 0)
                        
                        if momentum_j1 > 0:
                            ev_j1 = calcular_ev(momentum_j1, partida.get('odds_casa', 2.0))
                            ev_principal = max(ev_principal, ev_j1)
                        
                        if momentum_j2 > 0:
                            ev_j2 = calcular_ev(momentum_j2, partida.get('odds_visitante', 2.0))
                            ev_principal = max(ev_principal, ev_j2)
                            
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
            
            # 🚨 FILTRO ELIMINATÓRIO ABSOLUTO: TIMING OBRIGATÓRIO
            # FILTROS RIGOROSOS - Verificar se a partida passou em todos os critérios
            timing_aprovado = partida.get('prioridade', 0) >= CRITERIOS_RIGOROSOS['PRIORIDADE_MINIMA']
            
            if not timing_aprovado:
                print(f"   🚨 ELIMINADO POR TIMING INSUFICIENTE - Prioridade: {partida.get('prioridade', 0)}/5")
                print(f"      ❌ FILTRO ELIMINATÓRIO: Só aceita timing ÓTIMO (4) ou EXCELENTE (5)")
                continue
            
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
                print(f"   🎯 APLICANDO ESTRATÉGIA INVERTIDA - Critérios relaxados para cenário de alta tensão")
            else:
                criterios = CRITERIOS_RIGOROSOS
                estrategia_tipo = "RIGOROSA (situação normal)"
                print(f"   📊 APLICANDO CRITÉRIOS RIGOROSOS - Situação normal")
            
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
            
            # Se passou em TODOS os filtros
            if len(filtros_aprovados) == 4 and len(filtros_rejeitados) == 0:
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
                
                print(f"   🎯 OPORTUNIDADE ENCONTRADA - {jogador_info['nome']}")
                print(f"      {' | '.join(filtros_aprovados)}")
            else:
                print(f"   ❌ {jogador_info['nome']} - Filtros reprovados:")
                for filtro in filtros_rejeitados:
                    print(f"      {filtro}")
        
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
        print("💡 ESTRATÉGIA DUPLA IMPLEMENTADA:")
        print("\n📊 CRITÉRIOS RIGOROSOS (situações normais):")
        print("   • 🚨 TIMING: OBRIGATÓRIO - Só ÓTIMO (4) ou EXCELENTE (5)")
        print(f"   • EV: +{CRITERIOS_RIGOROSOS['EV_MINIMO']} a +0.50")
        print(f"   • Momentum Score: {CRITERIOS_RIGOROSOS['MOMENTUM_SCORE_MINIMO']}% a 70%")
        print(f"   • Double Faults: 0 a {CRITERIOS_RIGOROSOS['DOUBLE_FAULTS_MAXIMO']}")
        print(f"   • Win 1st Serve: {CRITERIOS_RIGOROSOS['WIN_1ST_SERVE_MINIMO']}% a 80%")
        print("\n🎯 ESTRATÉGIA INVERTIDA (3º sets e alta tensão):")
        print(f"   • EV: {CRITERIOS_INVERTIDOS['EV_MINIMO']} a +{CRITERIOS_INVERTIDOS['EV_MAXIMO']} (MUITO RELAXADO)")
        print(f"   • Momentum Score: {CRITERIOS_INVERTIDOS['MOMENTUM_SCORE_MINIMO']}% a 85% (RELAXADO)")
        print(f"   • Double Faults: 0 a {CRITERIOS_INVERTIDOS['DOUBLE_FAULTS_MAXIMO']} (MUITO RELAXADO)")
        print(f"   • Win 1st Serve: {CRITERIOS_INVERTIDOS['WIN_1ST_SERVE_MINIMO']}% a 85% (RELAXADO)")
        print("   • 🎯 OBJETIVO: Aproveitar cenários de alta pressão e fadiga")
    
    print(f"\n🕐 Última atualização: {datetime.now().strftime('%H:%M:%S')}")
    
    return oportunidades_finais

if __name__ == "__main__":
    analisar_ev_partidas()