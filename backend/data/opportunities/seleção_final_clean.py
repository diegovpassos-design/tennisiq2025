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

def analisar_ev_partidas():
    """Analisa EV das partidas com filtros refinados."""
    
    print("🎾 SELEÇÃO FINAL - ANÁLISE REFINADA COM MÚLTIPLOS FILTROS")
    print("=" * 70)
    print("🔍 Aplicando filtros: ESTRATÉGIAS INDEPENDENTES")
    
    # 🚀 ESTRATÉGIA ALAVANCAGEM - Para EVs muito altos (independente)
    CRITERIOS_ALAVANCAGEM = {
        'EV_MINIMO': 0.1,             # EVs baixos mas válidos (0.1+)
        'EV_MAXIMO': 50.0,            # Sem limite superior
        'MOMENTUM_SCORE_MINIMO': 55,  # MS ≥ 55% (DOMINÂNCIA - apenas um jogador precisa)
        'WIN_1ST_SERVE_MINIMO': 55,   # W1S ≥ 55% (DOMINÂNCIA - apenas um jogador precisa)
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
        'MOMENTUM_SCORE_MINIMO': 55,  # MS ≥ 55% (DOMINÂNCIA - apenas um jogador precisa)
        'WIN_1ST_SERVE_MINIMO': 55,   # W1S ≥ 55% (DOMINÂNCIA - apenas um jogador precisa)
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
        'MOMENTUM_SCORE_MINIMO': 55,  # MS ≥ 55% (DOMINÂNCIA - apenas um jogador precisa)
        'WIN_1ST_SERVE_MINIMO': 55,   # W1S ≥ 55% (DOMINÂNCIA - apenas um jogador precisa)
        'DOUBLE_FAULTS_MAXIMO': 6,    # DF ≤ 6 (relaxado)
        'ODDS_MIN': 1.80,             # Odds mínima
        'ODDS_MAX': 2.50,             # Odds máxima
        'PRIORIDADE_MINIMA': 0,       # SEM RESTRIÇÃO DE TIMING - 24H LIBERADO
        'NOME': 'INVERTIDA'
    }
    
    print("🎯 ESTRATÉGIAS INDEPENDENTES - Cada uma com seus critérios:")
    print(f"   🚀 ALAVANCAGEM: EV ≥ {CRITERIOS_ALAVANCAGEM['EV_MINIMO']}, MS ≥ {CRITERIOS_ALAVANCAGEM['MOMENTUM_SCORE_MINIMO']}% (DOMINÂNCIA), W1S ≥ {CRITERIOS_ALAVANCAGEM['WIN_1ST_SERVE_MINIMO']}% (DOMINÂNCIA)")
    print(f"   📊 TRADICIONAL: EV ≥ {CRITERIOS_TRADICIONAL['EV_MINIMO']}, MS ≥ {CRITERIOS_TRADICIONAL['MOMENTUM_SCORE_MINIMO']}% (DOMINÂNCIA), W1S ≥ {CRITERIOS_TRADICIONAL['WIN_1ST_SERVE_MINIMO']}% (DOMINÂNCIA)")
    print(f"   🔄 INVERTIDA: EV ≥ {CRITERIOS_INVERTIDOS['EV_MINIMO']}, MS ≥ {CRITERIOS_INVERTIDOS['MOMENTUM_SCORE_MINIMO']}% (DOMINÂNCIA), W1S ≥ {CRITERIOS_INVERTIDOS['WIN_1ST_SERVE_MINIMO']}% (DOMINÂNCIA)")
    
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
            
        # Determinar estratégia baseada na situação da partida
        placar = partida.get('placar', '')
        ev_principal = max(dados_casa.get('ev', 0), dados_visitante.get('ev', 0))
        is_terceiro_set = verificar_se_e_terceiro_set(placar)
        is_pos_tiebreak = verificar_pos_tiebreak(placar)
        is_alta_tensao = is_terceiro_set or is_pos_tiebreak or partida.get('prioridade', 0) == 5
        
        # Escolher critérios baseados na situação
        if is_alta_tensao:
            criterios = CRITERIOS_INVERTIDOS
            estrategia_tipo = "INVERTIDA (3º set/alta tensão)"
        elif ev_principal >= 3.0:
            criterios = CRITERIOS_ALAVANCAGEM
            estrategia_tipo = "ALAVANCAGEM (EV muito alto)"
        elif ev_principal >= 0.15:
            criterios = CRITERIOS_TRADICIONAL
            estrategia_tipo = "TRADICIONAL (EV moderado)"
        else:
            print(f"   ❌ EV muito baixo ({ev_principal:.3f}) - sem estratégia aplicável")
            continue
        
        # 🎯 VALIDAÇÃO DE DOMINÂNCIA PARA PARTIDA COMPLETA
        # MS: Pelo menos UM jogador deve ter ≥55%
        ms_casa = dados_casa.get('momentum_score', 0)
        ms_visitante = dados_visitante.get('momentum_score', 0)
        ms_maximo = max(ms_casa, ms_visitante)
        ms_aprovado = ms_maximo >= criterios['MOMENTUM_SCORE_MINIMO']
        
        # W1S: Pelo menos UM jogador deve ter ≥55%
        w1s_casa = float(dados_casa.get('win_1st_serve', 0)) if dados_casa.get('win_1st_serve') else 0
        w1s_visitante = float(dados_visitante.get('win_1st_serve', 0)) if dados_visitante.get('win_1st_serve') else 0
        w1s_maximo = max(w1s_casa, w1s_visitante)
        w1s_aprovado = w1s_maximo >= criterios['WIN_1ST_SERVE_MINIMO']
        
        # EV: Pelo menos UM jogador deve atender aos critérios
        ev_aprovado = ev_principal >= criterios['EV_MINIMO']
        
        # Logs de validação
        print(f"   🎯 {estrategia_tipo}")
        print(f"   📊 MS: Casa={ms_casa:.1f}%, Visitante={ms_visitante:.1f}%, Máximo={ms_maximo:.1f}% {'✅' if ms_aprovado else '❌'}")
        print(f"   🎾 W1S: Casa={w1s_casa:.1f}%, Visitante={w1s_visitante:.1f}%, Máximo={w1s_maximo:.1f}% {'✅' if w1s_aprovado else '❌'}")
        print(f"   ⚡ EV: {ev_principal:.3f} {'✅' if ev_aprovado else '❌'} (min {criterios['EV_MINIMO']})")
        print(f"   🔗 LÓGICA: MS ≥ 55% AND W1S ≥ 55% AND EV ≥ {criterios['EV_MINIMO']} = {ms_aprovado and w1s_aprovado and ev_aprovado}")
        
        # Verificar se passou em TODOS os critérios de dominância (AND lógico)
        if ms_aprovado and w1s_aprovado and ev_aprovado:
            # Determinar qual jogador é o melhor candidato (maior MS ou maior EV)
            if ms_casa >= ms_visitante:
                jogador_target = {'dados': dados_casa, 'nome': jogador_casa, 'oponente': jogador_visitante, 'tipo': 'HOME'}
            else:
                jogador_target = {'dados': dados_visitante, 'nome': jogador_visitante, 'oponente': jogador_casa, 'tipo': 'AWAY'}
                
            # Validar odds do jogador target
            odds_jogador = partida.get('odds_casa' if jogador_target['tipo'] == 'HOME' else 'odds_visitante', 'N/A')
            odds_aprovado = False
            
            if odds_jogador != 'N/A':
                try:
                    odds_float = float(odds_jogador)
                    odds_aprovado = criterios['ODDS_MIN'] <= odds_float <= criterios['ODDS_MAX']
                    print(f"   💰 Odds: {odds_float} {'✅' if odds_aprovado else '❌'} (range {criterios['ODDS_MIN']}-{criterios['ODDS_MAX']})")
                except (ValueError, TypeError):
                    print(f"   💰 Odds: inválidas ❌")
            else:
                print(f"   💰 Odds: N/A ❌")
            
            # Double Faults (validação individual do jogador target)
            df_value = int(jogador_target['dados'].get('double_faults', 0)) if jogador_target['dados'].get('double_faults') else 0
            df_aprovado = df_value <= criterios['DOUBLE_FAULTS_MAXIMO']
            print(f"   🎾 DF: {df_value} {'✅' if df_aprovado else '❌'} (max {criterios['DOUBLE_FAULTS_MAXIMO']})")
            
            # Decisão final
            if odds_aprovado and df_aprovado:
                oportunidade = {
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
                    'estrategia': estrategia_tipo,
                    'ms_casa': ms_casa,
                    'ms_visitante': ms_visitante,
                    'w1s_casa': w1s_casa,
                    'w1s_visitante': w1s_visitante
                }
                oportunidades_finais.append(oportunidade)
                print(f"   ✅ OPORTUNIDADE APROVADA - {estrategia_tipo}")
            else:
                print(f"   ❌ REJEITADA - Falhou em odds ou DF")
        else:
            print(f"   ❌ REJEITADA - Não atendeu critérios de dominância")
            
        print("-" * 60)
    
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
