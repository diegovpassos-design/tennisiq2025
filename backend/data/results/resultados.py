#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Verificação de Resultados TennisIQ
=============================================

Sistema para verificar o resultado das apostas enviadas pelo bot
e determinar se foram Green (vitória) ou Red (derrota).
"""

import requests
import json
import time
import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Adicionar diretórios ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'config'))

class VerificadorResultados:
    def __init__(self):
        """Inicializa o verificador com as configurações."""
        self.config = self.carregar_config()
        self.api_key = self.config.get('api_key')
        self.base_url = self.config.get('api_base_url', 'https://api.b365api.com')
        self.telegram_token = self.config.get('telegram_token')
        self.chat_id = self.config.get('chat_id')
        self.channel_id = self.config.get('channel_id')
        
        # Arquivo para salvar histórico de apostas
        self.arquivo_apostas = os.path.join(os.path.dirname(__file__), 'historico_apostas.json')
        self.arquivo_resultados = os.path.join(os.path.dirname(__file__), 'resultados_verificados.json')
        
        # Carregar histórico existente
        self.historico_apostas = self.carregar_historico_apostas()
        self.resultados_verificados = self.carregar_resultados_verificados()
        
    def carregar_config(self):
        """Carrega as configurações do arquivo config.json."""
        try:
            # Corrigir caminho para nova estrutura: backend/config/config.json
            config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'config.json')
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Erro ao carregar configurações: {e}")
            return {}
    
    def carregar_historico_apostas(self):
        """Carrega o histórico de apostas enviadas."""
        try:
            if os.path.exists(self.arquivo_apostas):
                with open(self.arquivo_apostas, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            print(f"❌ Erro ao carregar histórico: {e}")
            return []
    
    def carregar_resultados_verificados(self):
        """Carrega os resultados já verificados."""
        try:
            if os.path.exists(self.arquivo_resultados):
                with open(self.arquivo_resultados, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            print(f"❌ Erro ao carregar resultados: {e}")
            return []
    
    def normalizar_nome_jogador(self, nome: str) -> str:
        """Normaliza o nome do jogador para comparação."""
        if not nome:
            return ""
        # Remove espaços extras, converte para minúsculas e remove acentos
        nome = nome.lower().strip()
        # Remove caracteres especiais comuns
        nome = nome.replace("-", " ").replace("_", " ")
        # Remove espaços duplicados
        while "  " in nome:
            nome = nome.replace("  ", " ")
        return nome
    
    def calcular_similaridade_nomes(self, nome1: str, nome2: str) -> float:
        """Calcula a similaridade entre dois nomes de jogadores."""
        if not nome1 or not nome2:
            return 0.0
        
        # Normalizar ambos os nomes
        nome1_norm = self.normalizar_nome_jogador(nome1)
        nome2_norm = self.normalizar_nome_jogador(nome2)
        
        # Exato match
        if nome1_norm == nome2_norm:
            return 1.0
        
        # Separar palavras
        palavras1 = set(nome1_norm.split())
        palavras2 = set(nome2_norm.split())
        
        # Se algum nome está vazio após split
        if not palavras1 or not palavras2:
            return 0.0
        
        # Calcular intersecção
        intersecao = palavras1.intersection(palavras2)
        
        # Se têm pelo menos o sobrenome em comum (última palavra)
        if nome1_norm.split()[-1] == nome2_norm.split()[-1]:
            # Verificar se têm pelo menos uma palavra adicional em comum
            if len(intersecao) >= 2:
                return 0.8  # Alta similaridade se sobrenome igual + palavra adicional
            else:
                return 0.4  # Baixa similaridade se apenas sobrenome igual
        
        # Verificar sobrenome parcial (útil para nomes compostos)
        sobrenome1 = nome1_norm.split()[-1] if nome1_norm.split() else ""
        sobrenome2 = nome2_norm.split()[-1] if nome2_norm.split() else ""
        
        # Se uma das palavras do meio coincide com o sobrenome
        for palavra in palavras1:
            if palavra in palavras2 and len(palavra) > 3:  # Palavras significativas
                # Verificar se há pelo menos 2 palavras em comum
                if len(intersecao) >= 2:
                    return 0.7
                else:
                    return 0.3  # Reduzir score se apenas uma palavra em comum
        
        # Se contém pelo menos 2 palavras em comum
        if len(intersecao) >= 2:
            return 0.6
        
        # Calcular porcentagem de palavras em comum
        total_palavras = len(palavras1.union(palavras2))
        if total_palavras == 0:
            return 0.0
        
        similaridade = len(intersecao) / total_palavras
        
        # Bonus se alguma palavra longa é comum
        for palavra in intersecao:
            if len(palavra) > 5:  # Palavras longas têm mais peso
                similaridade += 0.2
                break
        
        return min(similaridade, 1.0)
    
    def encontrar_melhor_correspondencia(self, jogador_target: str, lista_jogadores: list) -> tuple:
        """Encontra a melhor correspondência para um jogador numa lista."""
        melhor_score = 0.0
        melhor_match = None
        
        for jogador in lista_jogadores:
            score = self.calcular_similaridade_nomes(jogador_target, jogador)
            if score > melhor_score:
                melhor_score = score
                melhor_match = jogador
        
        return melhor_match, melhor_score
    
    def salvar_historico_apostas(self):
        """Salva o histórico de apostas."""
        try:
            with open(self.arquivo_apostas, 'w', encoding='utf-8') as f:
                json.dump(self.historico_apostas, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Erro ao salvar histórico: {e}")
    
    def salvar_resultados_verificados(self):
        """Salva os resultados verificados."""
        try:
            with open(self.arquivo_resultados, 'w', encoding='utf-8') as f:
                json.dump(self.resultados_verificados, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Erro ao salvar resultados: {e}")
    
    def registrar_aposta(self, partida_id: str, jogador_apostado: str, oponente: str, 
                        odd: float, liga: str, placar_momento: str = ""):
        """Registra uma nova aposta no histórico."""
        aposta = {
            'id': f"aposta_{len(self.historico_apostas) + 1}",
            'partida_id': partida_id,
            'jogador_apostado': jogador_apostado,
            'oponente': oponente,
            'odd': odd,
            'liga': liga,
            'placar_momento': placar_momento,
            'data_aposta': datetime.now().isoformat(),
            'status': 'PENDENTE'
        }
        
        self.historico_apostas.append(aposta)
        self.salvar_historico_apostas()
        
        print(f"📝 Aposta registrada: {jogador_apostado} vs {oponente}")
        return aposta['id']
    
    def buscar_partidas_finalizadas(self, data_inicio: str = None):
        """Busca todas as partidas de tênis finalizadas usando o endpoint correto."""
        try:
            url = f"{self.base_url}/v3/events/ended"
            params = {
                'token': self.api_key,
                'sport_id': '13',  # Tennis
                'page': '1'
            }
            
            # Se data_inicio fornecida, usar formato YYYYMMDD
            if data_inicio:
                params['day'] = data_inicio
            
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success') == 1 and 'results' in data:
                    return data['results']
                    
            return []
            
        except Exception as e:
            print(f"❌ Erro ao buscar partidas finalizadas: {e}")
            return []

    def buscar_partidas_inplay(self):
        """Busca todas as partidas de tênis em andamento."""
        try:
            url = f"{self.base_url}/v3/events/inplay"
            params = {
                'token': self.api_key,
                'sport_id': '13'  # Tennis
            }
            
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success') == 1 and 'results' in data:
                    return data['results']
                    
            return []
            
        except Exception as e:
            print(f"❌ Erro ao buscar partidas inplay: {e}")
            return []

    def buscar_resultado_por_id(self, partida_id: str):
        """Busca o resultado de uma partida diretamente pelo ID."""
        try:
            print(f"🔍 Buscando resultado para ID: {partida_id}")
            
            # Verificar se é um ID real numérico
            if not partida_id.isdigit():
                print(f"❌ ID {partida_id} não é um ID numérico válido")
                return None
            
            # Buscar diretamente pelo ID do evento na API
            url = f"{self.base_url}/v3/event/view"
            params = {
                'token': self.api_key,
                'event_id': partida_id
            }
            
            print(f"� Consultando API para evento {partida_id}...")
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success') == 1 and 'results' in data and data['results']:
                    evento = data['results'][0]
                    print(f"✅ Evento encontrado: {evento.get('home', {}).get('name', '')} vs {evento.get('away', {}).get('name', '')}")
                    print(f"📊 Status: {evento.get('time_status', 'N/A')}")
                    
                    # Verificar se a partida está finalizada
                    time_status = evento.get('time_status', '')
                    if time_status in ['3', 'ended', 'finished']:
                        print(f"🏁 Partida finalizada, processando resultado...")
                        return self.processar_resultado_partida(evento)
                    else:
                        print(f"⏳ Partida ainda em andamento (status: {time_status})")
                        return {
                            'partida_terminada': False,
                            'status': time_status,
                            'home_team': evento.get('home', {}).get('name', ''),
                            'away_team': evento.get('away', {}).get('name', ''),
                            'motivo': f'Partida em andamento (status: {time_status})'
                        }
                else:
                    print(f"❌ Evento {partida_id} não encontrado na resposta da API")
                    print(f"📋 Resposta: {data}")
                    return None
            else:
                print(f"❌ Erro na API: Status {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Erro ao buscar resultado da partida {partida_id}: {e}")
            return None
            
        except Exception as e:
            print(f"❌ Erro ao buscar resultado da partida {partida_id}: {e}")
            return None

    def buscar_resultado_partida_por_id(self, partida_id: str):
        """Busca o resultado de uma partida específica pelo ID (método legado)."""
        # Para IDs artificiais, não tenta buscar por ID real
        return None

    def processar_resultado_partida(self, partida_data: Dict):
        """Processa os dados de uma partida finalizada."""
        try:
            # Verificar se realmente terminou
            time_status = partida_data.get('time_status', '')
            if time_status not in ['3', 'ended', 'finished']:
                return {
                    'partida_terminada': False,
                    'status': time_status,
                    'home_team': partida_data.get('home', {}).get('name', ''),
                    'away_team': partida_data.get('away', {}).get('name', '')
                }
            
            # Obter informações dos jogadores
            home_team = partida_data.get('home', {}).get('name', '')
            away_team = partida_data.get('away', {}).get('name', '')
            scores = partida_data.get('scores', {})
            
            # Determinar vencedor baseado nos sets
            vencedor = self.determinar_vencedor_v3(partida_data)
            
            return {
                'partida_terminada': True,
                'home_team': home_team,
                'away_team': away_team,
                'vencedor': vencedor,
                'scores': scores,
                'status': time_status,
                'ss': partida_data.get('ss', ''),  # Score atual
                'stats': partida_data.get('stats', {})
            }
            
        except Exception as e:
            print(f"❌ Erro ao processar resultado da partida: {e}")
            return None
    
    def determinar_vencedor_v3(self, partida_data: Dict):
        """Determina o vencedor baseado nos dados do endpoint v3."""
        try:
            home_team = partida_data.get('home', {}).get('name', '')
            away_team = partida_data.get('away', {}).get('name', '')
            
            # Verificar se há um resultado direto
            stats = partida_data.get('stats', {})
            
            # Método 1: Verificar se tem winner nos stats
            if 'winner' in stats:
                if stats['winner'] == '1':
                    return home_team
                elif stats['winner'] == '2':
                    return away_team
            
            # Método 2: Analisar o score string (ss)
            ss = partida_data.get('ss', '')
            if ss:
                # Formato típico: "6-4, 6-3" ou "6-4, 3-6, 6-2"
                sets = ss.replace(' ', '').split(',')  # Remove espaços e divide
                sets_home = 0
                sets_away = 0
                
                for set_score in sets:
                    if '-' in set_score:
                        try:
                            home_score, away_score = map(int, set_score.split('-'))
                            if home_score > away_score:
                                sets_home += 1
                            elif away_score > home_score:
                                sets_away += 1
                        except ValueError:
                            continue
                
                # Tennis precisa de pelo menos 2 sets para vencer
                if sets_home >= 2 and sets_home > sets_away:
                    return home_team
                elif sets_away >= 2 and sets_away > sets_home:
                    return away_team
            
            # Método 3: Analisar scores tradicionais
            scores = partida_data.get('scores', {})
            if scores:
                return self.determinar_vencedor_melhorado(scores, home_team, away_team)
            
            return "ERRO"
                
        except Exception as e:
            print(f"❌ Erro ao determinar vencedor v3: {e}")
            return "ERRO"
    
    def determinar_vencedor_melhorado(self, scores: Dict, home_team: str, away_team: str):
        """Determina o vencedor baseado nos scores dos sets com lógica melhorada."""
        try:
            sets_home = 0
            sets_away = 0
            sets_jogados = 0
            
            print(f"🔍 Analisando vencedor: {home_team} (home) vs {away_team} (away)")
            
            # Contar sets ganhos por cada jogador
            for set_num, set_scores in scores.items():
                if isinstance(set_scores, dict) and 'home' in set_scores and 'away' in set_scores:
                    try:
                        home_score = int(set_scores['home']) if set_scores['home'].isdigit() else 0
                        away_score = int(set_scores['away']) if set_scores['away'].isdigit() else 0
                        
                        print(f"   Set {set_num}: {home_team} {home_score} x {away_score} {away_team}")
                        
                        if home_score > away_score:
                            sets_home += 1
                            print(f"     ✅ Set para {home_team}")
                        elif away_score > home_score:
                            sets_away += 1
                            print(f"     ✅ Set para {away_team}")
                        
                        sets_jogados += 1
                    except (ValueError, TypeError):
                        continue
            
            print(f"📊 Resultado: {home_team} {sets_home} x {sets_away} {away_team}")
            
            # Tennis: precisa ganhar pelo menos 2 sets E ter mais sets que o oponente
            if sets_home >= 2 and sets_home > sets_away:
                print(f"🏆 Vencedor: {home_team}")
                return home_team
            elif sets_away >= 2 and sets_away > sets_home:
                print(f"🏆 Vencedor: {away_team}")
                return away_team
            else:
                # Verificar se é uma partida incompleta
                if sets_jogados < 2:
                    print(f"⚠️ Partida incompleta: apenas {sets_jogados} set(s) jogado(s)")
                    return "PARTIDA_INCOMPLETA"
                else:
                    print(f"⚠️ Caso especial: {home_team} ({sets_home} sets) vs {away_team} ({sets_away} sets)")
                    return "ERRO"
                
        except Exception as e:
            print(f"❌ Erro ao determinar vencedor melhorado: {e}")
            return "ERRO"
    
    def determinar_vencedor(self, scores: Dict, home_team: str, away_team: str):
        """Determina o vencedor baseado nos scores dos sets (método fallback)."""
        try:
            sets_home = 0
            sets_away = 0
            
            # Contar sets ganhos por cada jogador
            # Os scores estão organizados por número do set: {"1": {"home": "4", "away": "6"}, ...}
            for set_num, set_scores in scores.items():
                if isinstance(set_scores, dict) and 'home' in set_scores and 'away' in set_scores:
                    try:
                        home_score = int(set_scores['home']) if set_scores['home'].isdigit() else 0
                        away_score = int(set_scores['away']) if set_scores['away'].isdigit() else 0
                        
                        if home_score > away_score:
                            sets_home += 1
                        elif away_score > home_score:
                            sets_away += 1
                    except (ValueError, TypeError):
                        continue
            
            # Tennis: precisa ganhar pelo menos 2 sets E ter mais sets que o oponente
            if sets_home >= 2 and sets_home > sets_away:
                return home_team
            elif sets_away >= 2 and sets_away > sets_home:
                return away_team
            else:
                # No tennis não existe empate - se chegou aqui é erro ou partida incompleta
                if sets_home == sets_away:
                    return "PARTIDA_INCOMPLETA"  # Não pode empatar em sets no tennis
                else:
                    return "ERRO"  # Algum erro na análise
                
        except Exception as e:
            print(f"❌ Erro ao determinar vencedor: {e}")
            return "ERRO"

    def verificar_resultado_aposta(self, aposta: Dict):
        """Verifica se uma aposta foi Green ou Red usando o ID da partida."""
        try:
            partida_id = aposta.get('partida_id', '')
            jogador_apostado = aposta.get('jogador_apostado', '')
            oponente = aposta.get('oponente', '')
            
            if not partida_id:
                print(f"❌ ID da partida não encontrado para {jogador_apostado} vs {oponente}")
                return {
                    'status': 'ERRO',
                    'motivo': 'ID da partida não encontrado na aposta'
                }
            
            # Buscar resultado diretamente pelo ID
            resultado = self.buscar_resultado_por_id(partida_id)
            
            if not resultado:
                print(f"❌ Partida ID {partida_id} não foi encontrada na API de dados")
                return {
                    'status': 'ERRO',
                    'motivo': f'Partida ID {partida_id} não foi encontrada na API de dados'
                }
            
            if not resultado.get('partida_terminada', False):
                return {
                    'status': 'PENDENTE',
                    'motivo': f"Partida ainda em andamento - Status: {resultado.get('status', 'unknown')}"
                }
        
        except Exception as e:
            return {
                'status': 'ERRO',
                'motivo': f'Erro ao verificar aposta: {str(e)}'
            }
        
        # Determinar quem é home e away
        home_team = resultado.get('home_team', '')
        away_team = resultado.get('away_team', '')
        vencedor = resultado.get('vencedor', 'ERRO')
        
        # Verificar se conseguimos obter o vencedor
        if vencedor == 'ERRO' or not vencedor:
            return {
                'status': 'ERRO',
                'motivo': f"Não foi possível determinar o vencedor de {home_team} vs {away_team}"
            }
        
        # Verificar se conseguimos identificar os jogadores
        jogador_apostado_norm = self.normalizar_nome_jogador(jogador_apostado)
        oponente_norm = self.normalizar_nome_jogador(oponente)
        home_norm = self.normalizar_nome_jogador(home_team)
        away_norm = self.normalizar_nome_jogador(away_team)
        
        # Determinar quem é home e away
        if home_norm == jogador_apostado_norm:
            jogador_home = jogador_apostado
            jogador_away = oponente
            apostado_eh_home = True
        elif away_norm == jogador_apostado_norm:
            jogador_home = oponente
            jogador_away = jogador_apostado
            apostado_eh_home = False
        elif home_norm == oponente_norm:
            jogador_home = oponente
            jogador_away = jogador_apostado
            apostado_eh_home = False
        elif away_norm == oponente_norm:
            jogador_home = jogador_apostado
            jogador_away = oponente
            apostado_eh_home = True
        else:
            # Não conseguimos identificar claramente
            return {
                'status': 'VOID',
                'motivo': f"Não foi possível identificar os jogadores: {home_team} vs {away_team}",
                'jogador_home': home_team,
                'jogador_away': away_team,
                'jogador_apostado': jogador_apostado,
                'jogador_winner': vencedor,
                'scores': resultado['scores'],
                'score_string': resultado.get('ss', ''),
                'data_verificacao': datetime.now().isoformat()
            }
        
        # Determinar o resultado da aposta
        if vencedor == jogador_apostado:
            resultado_aposta = 'GREEN'
            motivo = f"{jogador_apostado} VENCEU!"
        elif vencedor in [home_team, away_team] and vencedor != jogador_apostado:
            resultado_aposta = 'RED'
            motivo = f"{vencedor} venceu, {jogador_apostado} PERDEU"
        else:
            resultado_aposta = 'VOID'
            motivo = f"Resultado inconclusivo: {vencedor}"
        
        return {
            'status': resultado_aposta,
            'motivo': motivo,
            'jogador_home': jogador_home,
            'jogador_away': jogador_away,
            'jogador_apostado': jogador_apostado,
            'jogador_winner': vencedor,
            'apostado_eh_home': apostado_eh_home,
            'scores': resultado['scores'],
            'score_string': resultado.get('ss', ''),
            'data_verificacao': datetime.now().isoformat()
        }

    def verificar_todas_apostas_pendentes(self):
        """Verifica todas as apostas pendentes."""
        print("🔍 Verificando resultados das apostas pendentes...")
        print("=" * 60)
        
        apostas_pendentes = [a for a in self.historico_apostas if a['status'] == 'PENDENTE']
        
        if not apostas_pendentes:
            print("✅ Nenhuma aposta pendente encontrada.")
            return
        
        print(f"📊 {len(apostas_pendentes)} aposta(s) pendente(s) encontrada(s)")
        print()
        
        for aposta in apostas_pendentes:
            print(f"🎾 Verificando: {aposta['jogador_apostado']} vs {aposta['oponente']}")
            print(f"📅 Data da aposta: {aposta['data_aposta']}")
            print(f"💰 Odd: {aposta['odd']}")
            
            resultado = self.verificar_resultado_aposta(aposta)
            
            if resultado:
                if resultado['status'] == 'PENDENTE':
                    print(f"⏳ {resultado['motivo']}")
                elif resultado['status'] == 'ERRO':
                    print(f"❌ {resultado['motivo']}")
                else:
                    # Atualizar status da aposta
                    aposta['status'] = resultado['status']
                    aposta['resultado_verificacao'] = resultado
                    
                    # Salvar no arquivo de resultados verificados
                    resultado_completo = aposta.copy()
                    resultado_completo.update(resultado)
                    self.resultados_verificados.append(resultado_completo)
                    
                    # Emoji baseado no resultado
                    emoji = "🟢" if resultado['status'] == 'GREEN' else "🔴" if resultado['status'] == 'RED' else "⚪"
                    
                    print(f"{emoji} RESULTADO: {resultado['status']}")
                    print(f"📝 {resultado['motivo']}")
                    
                    # Enviar notificação no Telegram
                    self.enviar_notificacao_resultado(aposta, resultado)
            else:
                print("❌ Erro ao verificar resultado - resposta vazia")
            
            print("-" * 40)
            time.sleep(1)  # Pausa otimizada entre verificações - reduzido de 2 para 1
        
        # Salvar arquivos atualizados
        self.salvar_historico_apostas()
        self.salvar_resultados_verificados()
        
        print("✅ Verificação concluída!")
    
    def enviar_notificacao_resultado(self, aposta: Dict, resultado: Dict):
        """Envia notificação do resultado via Telegram."""
        try:
            emoji = "🟢" if resultado['status'] == 'GREEN' else "🔴" if resultado['status'] == 'RED' else "⚪"
            
            mensagem = f"""
{emoji} **RESULTADO VERIFICADO** {emoji}

🎾 **{aposta['jogador_apostado']} vs {aposta['oponente']}**
🏟️ Liga: {aposta['liga']}
💰 Odd: {aposta['odd']}

📊 **RESULTADO: {resultado['status']}**
📝 {resultado['motivo']}

📅 Aposta: {datetime.fromisoformat(aposta['data_aposta']).strftime('%d/%m/%Y %H:%M')}
🔍 Verificado: {datetime.fromisoformat(resultado['data_verificacao']).strftime('%d/%m/%Y %H:%M')}

#TennisIQ #Resultado
"""
            
            # Enviar para chat pessoal e canal
            self.enviar_telegram(mensagem)
            
        except Exception as e:
            print(f"❌ Erro ao enviar notificação: {e}")
    
    def enviar_telegram(self, mensagem: str):
        """Envia mensagem para o Telegram."""
        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            
            # Enviar para chat pessoal
            payload_chat = {
                'chat_id': self.chat_id,
                'text': mensagem,
                'parse_mode': 'Markdown'
            }
            requests.post(url, json=payload_chat, timeout=10)
            
            # Enviar para canal
            payload_canal = {
                'chat_id': self.channel_id,
                'text': mensagem,
                'parse_mode': 'Markdown'
            }
            requests.post(url, json=payload_canal, timeout=10)
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao enviar Telegram: {e}")
            return False

    def gerar_relatorio_performance(self):
        """Gera relatório de performance das apostas."""
        print("📊 RELATÓRIO DE PERFORMANCE")
        print("=" * 50)
        
        if not self.resultados_verificados:
            print("❌ Nenhum resultado verificado encontrado.")
            return
        
        total_apostas = len(self.resultados_verificados)
        green_count = len([r for r in self.resultados_verificados if r['status'] == 'GREEN'])
        red_count = len([r for r in self.resultados_verificados if r['status'] == 'RED'])
        void_count = len([r for r in self.resultados_verificados if r['status'] == 'VOID'])
        
        win_rate = (green_count / total_apostas * 100) if total_apostas > 0 else 0
        
        print(f"📈 Total de apostas verificadas: {total_apostas}")
        print(f"🟢 Green: {green_count}")
        print(f"🔴 Red: {red_count}")
        print(f"⚪ Void: {void_count}")
        print(f"📊 Win Rate: {win_rate:.1f}%")
        print()
        
        print("🎯 ÚLTIMOS RESULTADOS:")
        print("-" * 30)
        
        for resultado in self.resultados_verificados[-10:]:  # Últimos 10
            emoji = "🟢" if resultado['status'] == 'GREEN' else "🔴" if resultado['status'] == 'RED' else "⚪"
            data = datetime.fromisoformat(resultado['data_verificacao']).strftime('%d/%m %H:%M')
            print(f"{emoji} {resultado['jogador_apostado']} vs {resultado['oponente']} | {resultado['odd']} | {data}")

def main():
    """Função principal."""
    verificador = VerificadorResultados()
    
    print("🎾 SISTEMA DE VERIFICAÇÃO DE RESULTADOS - TENNISIQ")
    print("=" * 55)
    print()
    
    try:
        # Executar verificação automática das apostas pendentes
        print("🔍 Iniciando verificação automática de resultados...")
        verificador.verificar_todas_apostas_pendentes()
        
        print("\n" + "="*60)
        
        # Gerar relatório de performance
        print("📊 Gerando relatório de performance...")
        verificador.gerar_relatorio_performance()
        
        print("\n" + "="*60)
        print("✅ Verificação completa finalizada!")
        print("💡 Para registrar apostas manuais, use registrar_apostas_manual.py")
        print("🔄 Para verificação contínua, execute novamente o script")
        
    except KeyboardInterrupt:
        print("\n⏹️ Verificação interrompida pelo usuário.")
    except Exception as e:
        print(f"❌ Erro durante a verificação: {e}")

if __name__ == "__main__":
    main()
