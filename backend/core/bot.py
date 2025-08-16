#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TennisIQ Bot - Sistema de Monitoramento de Apostas
=================================================

Bot para monitoramento automático de oportunidades de apostas em tênis
com notificações via Telegram.
"""

import requests
import json
import time
import signal
import sys
import os
# Configurar codificacao para evitar erros
import locale
import codecs
import io
# Importar gerenciador de links da Bet365
from backend.services.bet365_link_manager import bet365_manager

# Configurar stdout para UTF-8 apenas se necessário
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, 'buffer'):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
        if hasattr(sys.stderr, 'buffer'):
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")
    except (AttributeError, ValueError):
        # Se não conseguir configurar, continue sem problemas
        pass

from datetime import datetime, timedelta, timezone

# Importar sistemas de rate limiting e logging otimizado
try:
    from ..utils.rate_limiter import api_rate_limiter
    from ..utils.logger_producao import logger_prod
    from ..utils.logger_ultra import logger_ultra  # NOVO: Logger ultra-otimizado
    from ..utils.logger_estrategias import logger_estrategias  # NOVO: Logger estratégias resumido
    RATE_LIMITER_DISPONIVEL = True
    print("✅ Rate Limiter, Logger Produção, Logger Ultra e Logger Estratégias carregados")
except ImportError:
    print("⚠️ Rate Limiter não disponível - usando fallback")
    class RateLimiterFallback:
        def wait_if_needed(self): pass
        def register_request(self): pass
        def register_429_error(self): pass
        def can_make_request(self): return True
        def get_stats(self): return {'requests_last_hour': 0}
    
    class LoggerFallback:
        def log(self, cat, msg, force=False): print(msg)
        def error(self, msg, det=None): print(f"� {msg}")
        def warning(self, msg): print(f"⚠️ {msg}")
        def info(self, msg): print(f"ℹ️ {msg}")
        def success(self, msg): print(f"✅ {msg}")
        def ciclo_inicio(self, num): print(f"🔄 Ciclo {num}")
        def oportunidade_encontrada(self, jog, ev): print(f"🎯 {jog} (EV: {ev})")
        def stats_ciclo(self, p, a, o, r): print(f"� {p} partidas | {a} timing OK")
        def rate_limit_429(self, url): print(f"🚨 Rate Limit: {url}")
        def finalizar(self): pass
    
    api_rate_limiter = RateLimiterFallback()
    logger_prod = LoggerFallback()
    RATE_LIMITER_DISPONIVEL = False

# Importar logger formatado como fallback
try:
    from ..utils.logger_formatado import logger_formatado
    LOGGER_FORMATADO_DISPONIVEL = True
except ImportError:
    logger_formatado = LoggerFallback()
    LOGGER_FORMATADO_DISPONIVEL = False

# Importações condicionais baseadas no contexto de execução
try:
    from .extrair_stats_jogadores import extrair_stats_completas
    from .detector_vantagem_mental import DetectorVantagemMental
    from ..services.dashboard_logger import dashboard_logger
except ImportError:
    # Execução direta - ajustar imports
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from core.extrair_stats_jogadores import extrair_stats_completas
    from core.detector_vantagem_mental import DetectorVantagemMental
    from services.dashboard_logger import dashboard_logger

# Adicionar diretórios ao path - nova estrutura
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(os.path.join(PROJECT_ROOT, 'backend', 'data', 'opportunities'))
sys.path.append(os.path.join(PROJECT_ROOT, 'backend', 'data', 'analysis'))
sys.path.append(os.path.join(PROJECT_ROOT, 'backend', 'data', 'results'))

# Importar análise de oportunidades com tratamento de erro
try:
    # Tentar import relativo primeiro
    from ..data.opportunities.seleção_final import analisar_ev_partidas
    ANALISE_DISPONIVEL = True
    print("Sistema de analise de oportunidades carregado (modo relativo)")
except ImportError:
    try:
        # Tentar import absoluto
        sys.path.insert(0, PROJECT_ROOT)
        from backend.data.opportunities.seleção_final import analisar_ev_partidas
        ANALISE_DISPONIVEL = True
        print("Sistema de analise de oportunidades carregado (modo absoluto)")
    except Exception as e:
        print(f"Erro ao importar analise de oportunidades: {e}")
        # Função placeholder caso não consiga importar
        def analisar_ev_partidas(*args, **kwargs):
            print("Funcao de analise nao disponivel")
            return []
        ANALISE_DISPONIVEL = False

# Importar integrador de resultados
try:
    from ..services.integrador_resultados import integrador_resultados
    from ..data.results.resultados import VerificadorResultados
    RESULTADOS_DISPONIVEL = True
    print("Sistema de verificacao de resultados integrado")
except ImportError:
    integrador_resultados = None
    VerificadorResultados = None
    RESULTADOS_DISPONIVEL = False
    print("Sistema de verificacao de resultados nao disponivel")

class TennisIQBot:
    def __init__(self):
        """Inicializa o bot com as configurações do config.json."""
        self.running = True
        self.config = self.carregar_config()
        self.telegram_token = self.config.get('telegram_token')
        self.chat_id = self.config.get('chat_id')
        self.channel_id = self.config.get('channel_id')
        self.sinais_enviados = set()  # Controle de sinais únicos
        self.partidas_processadas = set()  # Controle de partidas já processadas
        self.api_key = self.config.get('api_key')
        self.base_url = self.config.get('api_base_url', 'https://api.b365api.com')
        self.requests_contador = 0  # Contador de requests para rate limiting
        
        # Inicializar gerenciador de links da Bet365
        self.inicializar_bet365_manager()
        self.hora_atual = datetime.now().hour  # Para resetar contador a cada hora
        
        # NOVO: Sistema de Vantagem Mental
        self.detector_mental = DetectorVantagemMental()
        
        # NOVO: Cache para odds (reduzir requisições duplicadas)
        self.cache_odds = {}
        self.cache_odds_timeout = 45  # 45 segundos de cache
        
        # Sistema de contabilização de greens seguidos
        self.greens_seguidos = 0
        self.total_greens = 0
        self.total_reds = 0
        self.total_voids = 0
        self.melhor_sequencia = 0
        self.carregar_estatisticas()
        
        # Sistema de relatórios
        self.greens_diarios = 0
        self.reds_diarios = 0
        self.voids_diarios = 0
        self.greens_mensais = 0
        self.reds_mensais = 0
        self.voids_mensais = 0
        self.data_ultimo_relatorio_diario = None
        self.data_ultimo_relatorio_mensal = None
        self.relatorio_atraso_verificado = False  # Flag para verificar atraso apenas uma vez por execução
        self.carregar_dados_relatorios()
        
        # Inicializar verificador de resultados
        self.verificador_resultados = None
        if RESULTADOS_DISPONIVEL and VerificadorResultados:
            try:
                self.verificador_resultados = VerificadorResultados()
                print("✅ Verificador de resultados inicializado")
            except Exception as e:
                print(f"⚠️ Erro ao inicializar verificador de resultados: {e}")
        
        # Configurar handler para Ctrl+C
        signal.signal(signal.SIGINT, self.signal_handler)
        
    def carregar_estatisticas(self):
        """Carrega as estatísticas de greens seguidos do arquivo."""
        try:
            stats_path = os.path.join(PROJECT_ROOT, 'storage', 'database', 'estatisticas_greens.json')
            if os.path.exists(stats_path):
                with open(stats_path, 'r', encoding='utf-8') as f:
                    stats = json.load(f)
                    self.greens_seguidos = stats.get('greens_seguidos', 0)
                    self.total_greens = stats.get('total_greens', 0)
                    self.total_reds = stats.get('total_reds', 0)
                    self.total_voids = stats.get('total_voids', 0)
                    self.melhor_sequencia = stats.get('melhor_sequencia', 0)
                    print(f"📊 Estatísticas carregadas: {self.greens_seguidos} greens seguidos")
        except Exception as e:
            print(f"⚠️ Erro ao carregar estatísticas: {e}")
    
    def salvar_estatisticas(self):
        """Salva as estatísticas de greens seguidos no arquivo."""
        try:
            stats_path = os.path.join(PROJECT_ROOT, 'storage', 'database', 'estatisticas_greens.json')
            stats = {
                'greens_seguidos': self.greens_seguidos,
                'total_greens': self.total_greens,
                'total_reds': self.total_reds,
                'total_voids': self.total_voids,
                'melhor_sequencia': self.melhor_sequencia,
                'ultima_atualizacao': datetime.now().isoformat()
            }
            with open(stats_path, 'w', encoding='utf-8') as f:
                json.dump(stats, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Erro ao salvar estatísticas: {e}")
    
    def atualizar_estatisticas(self, resultado_status):
        """Atualiza as estatísticas baseado no resultado."""
        if resultado_status == 'GREEN':
            self.greens_seguidos += 1
            self.total_greens += 1
            self.greens_diarios += 1
            self.greens_mensais += 1
            # Atualizar melhor sequência se necessário
            if self.greens_seguidos > self.melhor_sequencia:
                self.melhor_sequencia = self.greens_seguidos
        elif resultado_status == 'RED':
            self.greens_seguidos = 0  # Zerar sequência
            self.total_reds += 1
            self.reds_diarios += 1
            self.reds_mensais += 1
        elif resultado_status == 'VOID':
            # VOID não quebra a sequência nem adiciona
            self.total_voids += 1
            self.voids_diarios += 1
            self.voids_mensais += 1
        
        self.salvar_estatisticas()
        self.salvar_dados_relatorios()
    
    def rastrear_estrategia(self, estrategia, resultado, motivo, jogador):
        """Rastreia análises de estratégias para resumo do ciclo"""
        try:
            # Cache para evitar logs repetidos da mesma partida
            estrategias_testadas = getattr(self, '_estrategias_testadas_cache', {})
            jogador_key = jogador.replace(' vs ', '_').replace(' ', '_')
            
            if jogador_key not in estrategias_testadas:
                estrategias_testadas[jogador_key] = []
            
            estrategias_testadas[jogador_key].append((estrategia, resultado, motivo))
            self._estrategias_testadas_cache = estrategias_testadas
            
            # Log resumido da partida se todas as estratégias foram testadas
            if len(estrategias_testadas[jogador_key]) >= 2:  # Pelo menos 2 estratégias testadas
                logger_estrategias.log_analise_partida(jogador, estrategias_testadas[jogador_key])
                
        except Exception as e:
            print(f"⚠️ Erro ao rastrear estratégia: {e}")
    
    def gerar_mensagem_sequencia(self, resultado_status):
        """Gera mensagem motivacional baseada na sequência de greens."""
        if resultado_status == 'GREEN':
            if self.greens_seguidos == 1:
                return "🎯 Começamos bem! Primeiro GREEN! 🔥"
            elif self.greens_seguidos == 2:
                return "🚀 2 GREENS seguidos! A máquina está ligada! ⚡"
            elif self.greens_seguidos == 3:
                return "🔥 HAT-TRICK! 3 GREENS em sequência! 🎩"
            elif self.greens_seguidos == 4:
                return "💎 4 GREENS! Estamos imparáveis! 💪"
            elif self.greens_seguidos == 5:
                return "👑 5 GREENS! SEQUÊNCIA REAL! 🏆"
            elif self.greens_seguidos >= 10:
                return f"🌟 LENDÁRIO! {self.greens_seguidos} GREENS seguidos! HISTÓRICO! 🎖️"
            elif self.greens_seguidos >= 6:
                return f"🚀 {self.greens_seguidos} GREENS seguidos! MÁQUINA DE VITÓRIAS! 🎰"
            else:
                return f"🔥 {self.greens_seguidos} GREENS seguidos! Imparáveis! 💥"
        
        elif resultado_status == 'RED':
            if self.total_greens == 0:
                return "💪 Primeiro resultado, vamos buscar o GREEN! 🎯"
            else:
                return f"😤 Sequência quebrada, mas já tivemos {self.melhor_sequencia} greens seguidos! Vamos novamente! 🔄"
        
        else:  # VOID
            if self.greens_seguidos > 0:
                return f"💫 VOID não quebra nossa sequência de {self.greens_seguidos} greens! Seguimos firmes! 🎯"
            else:
                return "💫 VOID! Partida anulada, próxima vem! 🔄"
    
    def gerar_estatisticas_resumo(self):
        """Gera resumo das estatísticas para a mensagem."""
        total_apostas = self.total_greens + self.total_reds + self.total_voids
        if total_apostas > 0:
            win_rate = (self.total_greens / (self.total_greens + self.total_reds)) * 100 if (self.total_greens + self.total_reds) > 0 else 0
            return f"📊 Estatísticas: {self.total_greens}G-{self.total_reds}R-{self.total_voids}V | Win Rate: {win_rate:.1f}% | Melhor: {self.melhor_sequencia} seguidos"
        return "📊 Primeiras apostas - vamos começar a história! 🚀"
    
    def carregar_dados_relatorios(self):
        """Carrega os dados dos relatórios diários e mensais."""
        try:
            relatorios_path = os.path.join(PROJECT_ROOT, 'storage', 'database', 'relatorios_dados.json')
            if os.path.exists(relatorios_path):
                with open(relatorios_path, 'r', encoding='utf-8') as f:
                    dados = json.load(f)
                    self.greens_diarios = dados.get('greens_diarios', 0)
                    self.reds_diarios = dados.get('reds_diarios', 0)
                    self.voids_diarios = dados.get('voids_diarios', 0)
                    self.greens_mensais = dados.get('greens_mensais', 0)
                    self.reds_mensais = dados.get('reds_mensais', 0)
                    self.voids_mensais = dados.get('voids_mensais', 0)
                    self.data_ultimo_relatorio_diario = dados.get('data_ultimo_relatorio_diario')
                    self.data_ultimo_relatorio_mensal = dados.get('data_ultimo_relatorio_mensal')
                    print(f"📋 Dados de relatórios carregados")
        except Exception as e:
            print(f"⚠️ Erro ao carregar dados de relatórios: {e}")
    
    def salvar_dados_relatorios(self):
        """Salva os dados dos relatórios diários e mensais."""
        try:
            relatorios_path = os.path.join(PROJECT_ROOT, 'storage', 'database', 'relatorios_dados.json')
            dados = {
                'greens_diarios': self.greens_diarios,
                'reds_diarios': self.reds_diarios,
                'voids_diarios': self.voids_diarios,
                'greens_mensais': self.greens_mensais,
                'reds_mensais': self.reds_mensais,
                'voids_mensais': self.voids_mensais,
                'data_ultimo_relatorio_diario': self.data_ultimo_relatorio_diario,
                'data_ultimo_relatorio_mensal': self.data_ultimo_relatorio_mensal,
                'ultima_atualizacao': datetime.now().isoformat()
            }
            with open(relatorios_path, 'w', encoding='utf-8') as f:
                json.dump(dados, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Erro ao salvar dados de relatórios: {e}")
    
    def resetar_dados_diarios(self):
        """Reseta os dados diários."""
        self.greens_diarios = 0
        self.reds_diarios = 0
        self.voids_diarios = 0
        self.data_ultimo_relatorio_diario = datetime.now().strftime('%Y-%m-%d')
        self.salvar_dados_relatorios()
        print("🔄 Dados diários resetados")
    
    def resetar_dados_mensais(self):
        """Reseta os dados mensais."""
        self.greens_mensais = 0
        self.reds_mensais = 0
        self.voids_mensais = 0
        self.data_ultimo_relatorio_mensal = datetime.now().strftime('%Y-%m-%d')
        self.salvar_dados_relatorios()
        print("🔄 Dados mensais resetados")
    
    def gerar_relatorio_diario(self):
        """Gera e envia relatório diário. - DESABILITADO"""
        print("📅 Relatório diário desabilitado por solicitação do usuário")
        return  # ❌ FUNÇÃO DESABILITADA
        
        agora = datetime.now()
        data_atual = agora.strftime('%d/%m/%Y')
        
        # Calcular taxa de assertividade
        total_apostas_diarias = self.greens_diarios + self.reds_diarios
        if total_apostas_diarias > 0:
            taxa_assertividade = (self.greens_diarios / total_apostas_diarias) * 100
        else:
            taxa_assertividade = 0
        
        # Determinar emoji baseado na performance
        if taxa_assertividade >= 80:
            emoji_performance = "🏆"
        elif taxa_assertividade >= 70:
            emoji_performance = "🥇"
        elif taxa_assertividade >= 60:
            emoji_performance = "🥈"
        elif taxa_assertividade >= 50:
            emoji_performance = "🥉"
        else:
            emoji_performance = "📊"
        
        mensagem = f"""📅 RELATÓRIO DIÁRIO - {data_atual}
═══════════════════════════════

📊 RESULTADOS DO DIA:
🟢 Greens: {self.greens_diarios}
🔴 Reds: {self.reds_diarios}
⚪ Voids: {self.voids_diarios}
📈 Total de apostas: {total_apostas_diarias}

{emoji_performance} TAXA DE ASSERTIVIDADE: {taxa_assertividade:.1f}%

🎯 TennisIQ - Relatório Diário Automático
═══════════════════════════════"""
        
        sucesso = self.enviar_telegram(mensagem, para_canal=True)
        if sucesso:
            # Atualizar a data do último relatório para hoje
            self.data_ultimo_relatorio_diario = agora.strftime('%Y-%m-%d')
            self.salvar_dados_relatorios()
            print(f"✅ Relatório diário enviado - {data_atual}")
            self.resetar_dados_diarios()
        else:
            print(f"❌ Falha ao enviar relatório diário")
        
        return sucesso
    
    def gerar_relatorio_mensal(self):
        """Gera e envia relatório mensal. - DESABILITADO"""
        print("🗓️ Relatório mensal desabilitado por solicitação do usuário")
        return  # ❌ FUNÇÃO DESABILITADA
        
        agora = datetime.now()
        mes_anterior = agora.replace(day=1) - timedelta(days=1)
        nome_mes = mes_anterior.strftime('%B/%Y')
        
        # Traduzir mês para português
        meses_pt = {
            'January': 'Janeiro', 'February': 'Fevereiro', 'March': 'Março',
            'April': 'Abril', 'May': 'Maio', 'June': 'Junho',
            'July': 'Julho', 'August': 'Agosto', 'September': 'Setembro',
            'October': 'Outubro', 'November': 'Novembro', 'December': 'Dezembro'
        }
        
        for en, pt in meses_pt.items():
            nome_mes = nome_mes.replace(en, pt)
        
        # Calcular taxa de assertividade mensal
        total_apostas_mensais = self.greens_mensais + self.reds_mensais
        if total_apostas_mensais > 0:
            taxa_assertividade = (self.greens_mensais / total_apostas_mensais) * 100
        else:
            taxa_assertividade = 0
        
        # Calcular médias diárias
        dias_no_mes = mes_anterior.day
        media_apostas_dia = total_apostas_mensais / dias_no_mes if dias_no_mes > 0 else 0
        media_greens_dia = self.greens_mensais / dias_no_mes if dias_no_mes > 0 else 0
        
        # Determinar emoji e classificação mensal
        if taxa_assertividade >= 75:
            emoji_mensal = "👑"
            classificacao = "MÊS LENDÁRIO"
        elif taxa_assertividade >= 65:
            emoji_mensal = "🏆"
            classificacao = "MÊS EXCELENTE"
        elif taxa_assertividade >= 55:
            emoji_mensal = "🥇"
            classificacao = "MÊS MUITO BOM"
        elif taxa_assertividade >= 45:
            emoji_mensal = "🥈"
            classificacao = "MÊS REGULAR"
        else:
            emoji_mensal = "📊"
            classificacao = "MÊS DESAFIADOR"
        
        mensagem = f"""🗓️ RELATÓRIO MENSAL - {nome_mes}
═══════════════════════════════

📊 RESULTADOS DO MÊS:
🟢 Total Greens: {self.greens_mensais}
🔴 Total Reds: {self.reds_mensais}
⚪ Total Voids: {self.voids_mensais}
📈 Total de apostas: {total_apostas_mensais}

{emoji_mensal} TAXA DE ASSERTIVIDADE: {taxa_assertividade:.1f}%
🏅 Classificação: {classificacao}

📈 ESTATÍSTICAS AVANÇADAS:
📅 Dias no mês: {dias_no_mes}
📊 Média apostas/dia: {media_apostas_dia:.1f}
🎯 Média greens/dia: {media_greens_dia:.1f}
🏆 Melhor sequência: {self.melhor_sequencia} greens seguidos

💰 ANÁLISE DE PERFORMANCE:
{"🚀 Meta atingida! Excelente mês!" if taxa_assertividade >= 60 else "💪 Foco na melhoria para o próximo mês!"}

🎯 TennisIQ - Relatório Mensal Automático
═══════════════════════════════"""
        
        sucesso = self.enviar_telegram(mensagem, para_canal=True)
        if sucesso:
            print(f"✅ Relatório mensal enviado - {nome_mes}")
            self.resetar_dados_mensais()
        else:
            print(f"❌ Falha ao enviar relatório mensal")
        
        return sucesso
    
    def verificar_horario_relatorios(self):
        """Verifica se é hora de enviar relatórios ou se há relatórios em atraso."""
        agora = datetime.now()
        data_hoje = agora.strftime('%Y-%m-%d')
        
        # Verificar links da Bet365 proativamente
        self.verificar_links_bet365()
        
        # ❌ RELATÓRIOS DESABILITADOS POR SOLICITAÇÃO DO USUÁRIO
        # Verificar se há relatório diário em atraso (apenas uma vez por execução)
        # if not self.relatorio_atraso_verificado and self.data_ultimo_relatorio_diario != data_hoje:
        #     print("📅 Detectado relatório diário em atraso, enviando...")
        #     self.gerar_relatorio_diario()
        #     self.relatorio_atraso_verificado = True
                
        # Verificar relatório diário (janela flexível: 23:30 às 00:00)
        # janela_relatorio = ((agora.hour == 23 and agora.minute >= 30) or 
        #                    (agora.hour == 0 and agora.minute == 0))
        
        # if janela_relatorio:
        #     # Verificar se já enviou hoje
        #     if self.data_ultimo_relatorio_diario != data_hoje:
        #         print("🕐 Janela do relatório diário ativa (23:30-00:00)!")
        #         self.gerar_relatorio_diario()
        
        # Verificar relatório mensal (último dia do mês - janela flexível: 23:30 às 00:00)
        # if janela_relatorio:
        #     # Verificar se é o último dia do mês
        #     amanha = agora + timedelta(days=1)
        #     if amanha.day == 1:  # Se amanhã é dia 1, hoje é último dia do mês
        #         # Verificar se já enviou este mês
        #         if self.data_ultimo_relatorio_mensal != data_hoje:
        #             print("🗓️ Janela do relatório mensal ativa (23:30-00:00)!")
        #             self.gerar_relatorio_mensal()
        
    def limpar_cache_antigo(self):
        """Limpa cache de partidas antigas para evitar acúmulo excessivo."""
        # Limpar cache mais frequentemente para melhor performance
        if len(self.partidas_processadas) > 30:  # Reduzido de 50 para 30
            print(f"🧹 Limpando cache de partidas antigas ({len(self.partidas_processadas)} entradas)")
            self.partidas_processadas.clear()
            # Manter apenas os últimos 15 sinais para evitar duplicatas
            if len(self.sinais_enviados) > 15:  # Aumentado de 10 para 15
                self.sinais_enviados.clear()
        
    def carregar_config(self):
        """Carrega as configurações do arquivo config.json."""
        try:
            config_path = os.path.join(PROJECT_ROOT, 'backend', 'config', 'config.json')
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Erro ao carregar configurações: {e}")
            return {}
    
    def inicializar_bet365_manager(self):
        """Inicializa o gerenciador de links da Bet365 com parâmetro _h atual."""
        try:
            # Inicializando Bet365 Link Manager: silencioso
            
            # Definir parâmetro manual se disponível
            h_param_manual = "LKUUnzn5idsD_NCCi9iyvQ%3D%3D"  # Último valor conhecido
            
            # Tentar definir parâmetro manual primeiro
            if bet365_manager.set_h_param_manual(h_param_manual):
                # Bet365 Link Manager inicializado: silencioso
                pass
            else:
                # Parâmetro manual falhou, tentando captura automática: silencioso
                bet365_manager.update_h_param(force=True)
            
            # Verificar status
            status = bet365_manager.get_status()
            if status['h_param_available']:
                # Bet365 links prontos: silencioso
                pass
            else:
                # Bet365 links podem não funcionar: silencioso
                pass
                
        except Exception as e:
            # Erro ao inicializar Bet365 Link Manager: silencioso
            pass
    
    def verificar_links_bet365(self):
        """Verifica proativamente se os links da Bet365 estão funcionando."""
        try:
            # Verificar apenas a cada 2 horas para não sobrecarregar
            if not hasattr(self, 'ultima_verificacao_bet365'):
                self.ultima_verificacao_bet365 = 0
            
            agora = time.time()
            if agora - self.ultima_verificacao_bet365 < 7200:  # 2 horas
                return
            
            # Verificando links da Bet365: silencioso
            status = bet365_manager.get_status()
            
            if not status['link_working']:
                # Links da Bet365 não estão funcionando: silencioso
                bet365_manager.update_h_param(force=True)
                
                # Verificar novamente após atualização
                new_status = bet365_manager.get_status()
                if new_status['link_working']:
                    # Links da Bet365 atualizados com sucesso: silencioso
                    # Notificar via Telegram sobre a atualização
                    self.enviar_telegram(
                        "🔗 Links da Bet365 foram atualizados automaticamente",
                        para_canal=False
                    )
                else:
                    # Falha ao atualizar links da Bet365: silencioso
                    # Notificar sobre o problema
                    self.enviar_telegram(
                        "⚠️ ATENÇÃO: Links da Bet365 podem estar com problema. Verificação manual necessária.",
                        para_canal=False
                    )
            
            self.ultima_verificacao_bet365 = agora
            
        except Exception as e:
            # Erro na verificação dos links da Bet365: silencioso
            pass
    
    def buscar_odds_evento(self, event_id):
        """Busca as odds de um evento específico com rate limiting e cache."""
        
        # Verificar cache primeiro
        agora = time.time()
        cache_key = f"odds_{event_id}"
        
        if cache_key in self.cache_odds:
            timestamp, odds_data = self.cache_odds[cache_key]
            if agora - timestamp < self.cache_odds_timeout:
                # Cache válido - retornar sem fazer requisição
                return odds_data
        
        # Verificar rate limiting
        if not api_rate_limiter.can_make_request():
            api_rate_limiter.wait_if_needed()
        
        url = f"{self.base_url}/v3/event/odds"
        params = {
            'event_id': event_id,
            'token': self.api_key
        }
        
        try:
            # Registrar requisição
            api_rate_limiter.register_request()
            self.requests_contador += 1
            
            response = requests.get(url, params=params, timeout=3)
            
            # Verificar se é erro 429
            if response.status_code == 429:
                api_rate_limiter.register_429_error()
                logger_prod.rate_limit_429(url)
                return {'jogador1_odd': 'N/A', 'jogador2_odd': 'N/A', 'event_id': event_id}
            
            response.raise_for_status()
            data = response.json()
            
            if data.get('success') == 1 and 'results' in data:
                results = data['results']
                
                # Verificar se há odds disponíveis no formato v3
                if 'odds' in results and results['odds']:
                    odds_data = results['odds']
                    
                    # Procurar pelo mercado 13_1 (Match Winner)
                    if '13_1' in odds_data and odds_data['13_1']:
                        # Pegar a odd mais recente (primeira da lista)
                        latest_odds = odds_data['13_1'][0]
                        
                        if 'home_od' in latest_odds and 'away_od' in latest_odds:
                            odds_result = {
                                'jogador1_odd': latest_odds.get('home_od', 'N/A'),
                                'jogador2_odd': latest_odds.get('away_od', 'N/A'),
                                'event_id': event_id  # Adicionar event_id para mapeamento correto
                            }
                            
                            # Salvar no cache
                            self.cache_odds[cache_key] = (agora, odds_result)
                            
                            logger_prod.log('DEBUG', f"✅ Odd Casa: {odds_result['jogador1_odd']}")
                            logger_prod.log('DEBUG', f"✅ Odd Visitante: {odds_result['jogador2_odd']}")
                            return odds_result
            
            # Fallback - salvar no cache também para evitar requisições repetidas
            fallback_result = {'jogador1_odd': 'N/A', 'jogador2_odd': 'N/A', 'event_id': event_id}
            self.cache_odds[cache_key] = (agora, fallback_result)
            return fallback_result
            
        except requests.exceptions.RequestException as e:
            if "429" in str(e):
                api_rate_limiter.register_429_error()
                logger_prod.error(f"Erro ao buscar odds do evento {event_id}: {e}")
            else:
                logger_prod.warning(f"Erro de rede ao buscar odds para evento {event_id}")
            return {'jogador1_odd': 'N/A', 'jogador2_odd': 'N/A', 'event_id': event_id}
        except Exception as e:
            logger_prod.warning(f"Erro inesperado ao buscar odds para evento {event_id}")
            return {'jogador1_odd': 'N/A', 'jogador2_odd': 'N/A', 'event_id': event_id}
    
    def coletar_estatisticas_reais(self, event_id):
        """Coleta estatísticas reais dos jogadores usando o extrator personalizado."""
        try:
            if not event_id:
                logger_prod.warning("Event ID não disponível para coleta de stats")
                return {
                    'stats_jogador1': {},
                    'stats_jogador2': {}
                }
            
            logger_prod.log('DEBUG', f"📊 Coletando estatísticas reais para evento {event_id}...")
            
            # O extrator já deve usar o rate limiter internamente
            stats = extrair_stats_completas(event_id, self.api_key, self.base_url)
            
            if stats and stats.get('stats_jogador1') and stats.get('stats_jogador2'):
                j1_stats = stats['stats_jogador1']
                j2_stats = stats['stats_jogador2']
                
                # Verificar se pelo menos uma estatística não é zero
                j1_total = sum(j1_stats.values())
                j2_total = sum(j2_stats.values())
                
                if j1_total > 0 or j2_total > 0:
                    logger_prod.log('DEBUG', f"✅ Estatísticas coletadas: J1 Total={j1_total}, J2 Total={j2_total}")
                    return stats
                else:
                    logger_prod.warning("Estatísticas coletadas estão vazias")
            
            return {
                'stats_jogador1': {},
                'stats_jogador2': {}
            }
            
        except Exception as e:
            logger_prod.error(f"Erro ao coletar estatísticas reais: {e}")
            return {
                'stats_jogador1': {},
                'stats_jogador2': {}
            }
    
    def calcular_odd_minima(self, odd_atual, margem_seguranca=0.15):
        """Calcula a odd mínima para apostar com base na margem de segurança."""
        try:
            odd_float = float(odd_atual)
            odd_minima = odd_float * (1 - margem_seguranca)
            return round(odd_minima, 2)
        except (ValueError, TypeError):
            return 2.00  # Valor padrão seguro
    
    def determinar_estrategia_por_oportunidade(self, oportunidade):
        """Determina qual estratégia gerou a oportunidade baseada nos dados."""
        # Verificar se tem informação de estratégia na oportunidade
        if 'estrategia' in oportunidade:
            estrategia_nome = oportunidade['estrategia'].lower()
            if 'virada_mental' in estrategia_nome:
                return 'virada_mental'
        
        # Inferir pela fase do jogo (terceiro set = virada mental)
        fase = oportunidade.get('fase', '').lower()
        if '3set' in fase or 'terceiro' in fase:
            return 'virada_mental'
        
        # Verificar por critérios específicos da virada mental
        placar = oportunidade.get('placar', '')
        if '3' in placar and ('set' in placar.lower() or '-' in placar):
            return 'virada_mental'
        
        # Default: virada_mental (única estratégia ativa)
        return 'virada_mental'
    
    def validar_filtros_odds(self, oportunidade, odds_data):
        """Valida se a aposta passa nos filtros de odds (1.8 a 2.2)."""
        try:
            # Determinar a estratégia baseada na oportunidade
            estrategia = self.determinar_estrategia_por_oportunidade(oportunidade)
            jogador = oportunidade['jogador']
            
            # Determinar a odd correta baseado no tipo (HOME ou AWAY)
            if oportunidade.get('tipo') == 'HOME':
                odd_atual = odds_data.get('jogador1_odd', 'N/A')
            else:
                odd_atual = odds_data.get('jogador2_odd', 'N/A')
            
            # Converter para float para validação
            if odd_atual == 'N/A' or odd_atual == '-':
                logger_formatado.log_estrategia(estrategia, 'rejeicao', 'Odd não disponível', jogador)
                return False, None
            
            odd_float = float(odd_atual)
            
            # FILTRO CRÍTICO: Odds entre 1.8 e 2.2 (baseado na análise)
            if not (1.8 <= odd_float <= 2.2):
                logger_formatado.log_estrategia(estrategia, 'rejeicao', f'Odd {odd_float} fora do range 1.8-2.2', jogador)
                return False, odd_float
            
            logger_formatado.log_estrategia(estrategia, 'sucesso', f'Odd {odd_float} aprovada', jogador)
            return True, odd_float
            
        except (ValueError, TypeError) as e:
            logger_formatado.log_estrategia('tradicional', 'rejeicao', f'Erro ao validar odd: {e}', oportunidade.get('jogador', 'N/A'))
            return False, None

    def gerar_sinal_tennisiq(self, oportunidade, odds_data, dados_filtros=None):
        """Gera sinal no formato TennisIQ específico com dados dos filtros."""
        # Usar horário de Brasília (UTC-3)
        agora = datetime.now(timezone(timedelta(hours=-3)))
        horario = agora.strftime("%H:%M")
        
        # O jogador da oportunidade é sempre o que tem maior EV
        jogador_alvo = oportunidade['jogador']
        oponente = oportunidade['oponente']
        
        # Determinar a odd correta baseado no tipo (HOME ou AWAY)
        if oportunidade.get('tipo') == 'HOME':
            odd_atual = odds_data.get('jogador1_odd', 'N/A')
        else:
            odd_atual = odds_data.get('jogador2_odd', 'N/A')
        
        # Se a odd não foi encontrada, usar um valor padrão
        if odd_atual == 'N/A' or odd_atual == '-':
            odd_atual = "2.50"  # Valor padrão conservador
        
        # Calcular odd mínima
        odd_minima = self.calcular_odd_minima(odd_atual)
        
        # Gerar link direto da Bet365 (sistema automático)
        event_id = oportunidade.get('partida_id', '')
        bet365_link = bet365_manager.generate_link(event_id)
        
        # Determinar tipo de estratégia
        estrategia_tipo = self.determinar_estrategia_por_oportunidade(oportunidade)
        
        # Gerar sinal específico para cada estratégia
        if estrategia_tipo == 'virada_mental':
            # Sinal específico para VIRADA MENTAL
            placar = oportunidade.get('placar', 'N/A')
            momentum = oportunidade.get('momentum', 0)
            justificativa = oportunidade.get('justificativa', 'Estratégia de comeback mental')
            
            sinal = f"""🧠 TennisIQ - Sinal - VIRADA MENTAL 🔥

{oponente} vs {jogador_alvo}
⏰ {horario}
📊 Placar: {placar}

🚀 APOSTAR EM: {jogador_alvo} 🚀
💰 Odd: {odd_atual}
⚠️ Limite Mínimo: {odd_minima} (não apostar abaixo)

🧠 VIRADA MENTAL DETECTADA:
• Perdeu 1º set, venceu 2º set
• Liderando/igualado no 3º set
• Momentum: {momentum}%
• {justificativa}

🔗 Link direto: {bet365_link}

#TennisIQ #ViradaMental"""
        
        else:
            # Sinal VIRADA_MENTAL (padrão)
            sinal = f"""🎾 TennisIQ - Sinal - Virada Mental 🧠

{oponente} vs {jogador_alvo}
⏰ {horario}

🚀 APOSTAR EM: {jogador_alvo} 🚀
💰 Odd: {odd_atual}
⚠️ Limite Mínimo: {odd_minima} (não apostar abaixo)

🧠 VIRADA MENTAL DETECTADA:
• Perdeu 1º set, venceu 2º set
• Liderando/igualado no 3º set
• Momentum: {momentum}%
• {justificativa}

🔗 Link direto: {bet365_link}

#TennisIQ #ViradaMental"""
        
        return sinal
    
    def gerar_log_oportunidades_proximas(self, todas_partidas_analisadas):
        """Gera log das oportunidades mais próximas de passar nos filtros."""
        agora = datetime.now()
        timestamp = agora.strftime("%d/%m/%Y %H:%M:%S")
        
        log_content = f"\n{'='*80}\n"
        log_content += f"📊 LOG DE OPORTUNIDADES PRÓXIMAS - {timestamp}\n"
        log_content += f"{'='*80}\n"
        
        # Se não há dados detalhados, usar análise básica
        if not todas_partidas_analisadas:
            log_content += "⚠️ Dados detalhados não disponíveis para análise de proximidade.\n"
            return log_content
        
        candidatos_proximos = []
        
        # Analisar cada partida para ver quão próxima está de passar
        for partida in todas_partidas_analisadas:
            try:
                jogadores = [
                    {'nome': partida.get('jogador_casa', ''), 'tipo': 'HOME'},
                    {'nome': partida.get('jogador_visitante', ''), 'tipo': 'AWAY'}
                ]
                
                for jogador_info in jogadores:
                    # Simular dados (em produção viria da análise real)
                    # Aqui faremos uma análise básica dos dados disponíveis
                    score_proximidade = 0
                    filtros_status = []
                    
                    # Análise básica de timing (já aprovado se chegou aqui)
                    score_proximidade += 25
                    filtros_status.append("✅ Timing: APROVADO")
                    
                    # Estimar outros filtros baseado em dados disponíveis
                    # EV: assumir valores próximos para análise
                    ev_estimado = 0.20  # Próximo do mínimo 0.15
                    if ev_estimado >= 0.15:
                        score_proximidade += 25
                        filtros_status.append(f"✅ EV: {ev_estimado:.3f} (≥0.15)")
                    else:
                        filtros_status.append(f"❌ EV: {ev_estimado:.3f} (<0.15)")
                    
                    # MS: estimar baseado em fase da partida
                    ms_estimado = 62  # Próximo do mínimo 65
                    if 65 <= ms_estimado <= 75:
                        score_proximidade += 25
                        filtros_status.append(f"✅ MS: {ms_estimado}% (65-75%)")
                    else:
                        filtros_status.append(f"❌ MS: {ms_estimado}% (precisa 65%+)")
                    
                    # DF e W1S: estimar valores próximos
                    df_estimado = 2
                    w1s_estimado = 63
                    
                    if 0 <= df_estimado <= 3:
                        score_proximidade += 12.5
                        filtros_status.append(f"✅ DF: {df_estimado} (0-3)")
                    else:
                        filtros_status.append(f"❌ DF: {df_estimado} (>3)")
                    
                    if 65 <= w1s_estimado <= 75:
                        score_proximidade += 12.5
                        filtros_status.append(f"✅ W1S: {w1s_estimado}% (65-75%)")
                    else:
                        filtros_status.append(f"❌ W1S: {w1s_estimado}% (precisa 65-75%)")
                    
                    # Se está próximo (>70% dos filtros), adicionar aos candidatos
                    if score_proximidade >= 70:
                        candidatos_proximos.append({
                            'jogador': jogador_info['nome'],
                            'partida': f"{partida.get('jogador_casa', '')} vs {partida.get('jogador_visitante', '')}",
                            'liga': partida.get('liga', 'N/A'),
                            'placar': partida.get('placar', 'N/A'),
                            'score': score_proximidade,
                            'filtros': filtros_status
                        })
            
            except Exception as e:
                continue
        
        # Ordenar por score de proximidade
        candidatos_proximos.sort(key=lambda x: x['score'], reverse=True)
        
        if candidatos_proximos:
            log_content += f"🎯 ENCONTRADOS {len(candidatos_proximos)} CANDIDATOS PRÓXIMOS:\n\n"
            
            for i, candidato in enumerate(candidatos_proximos[:10], 1):  # Top 10
                if candidato['score'] >= 95:
                    emoji = "🟢"
                    status = "MUITO PRÓXIMO"
                elif candidato['score'] >= 85:
                    emoji = "🟡"
                    status = "PRÓXIMO"
                else:
                    emoji = "🟠"
                    status = "MARGINAL"
                
                log_content += f"{emoji} {i}. {candidato['jogador']} - {status} ({candidato['score']:.1f}%)\n"
                log_content += f"   📊 Partida: {candidato['partida']}\n"
                log_content += f"   🏟️ Liga: {candidato['liga']}\n"
                log_content += f"   🎯 Placar: {candidato['placar']}\n"
                log_content += f"   📋 Filtros:\n"
                for filtro in candidato['filtros']:
                    log_content += f"      {filtro}\n"
                log_content += "\n"
        else:
            log_content += "❌ Nenhum candidato próximo encontrado neste ciclo.\n"
            log_content += "💡 Isso indica que os filtros estão sendo muito restritivos\n"
            log_content += "   ou as condições atuais não favorecem oportunidades.\n"
        
        log_content += f"\n📊 ESTATÍSTICAS DO CICLO:\n"
        log_content += f"   • Partidas analisadas: {len(todas_partidas_analisadas) if todas_partidas_analisadas else 0}\n"
        log_content += f"   • Candidatos próximos: {len(candidatos_proximos)}\n"
        log_content += f"   • Requests API neste ciclo: {self.requests_contador}\n"
        log_content += f"   • Limite API: 3.600/hora (atual: ~{(self.requests_contador * 60):.0f}/hora)\n"
        log_content += f"\n💡 OTIMIZAÇÃO DE API:\n"
        log_content += f"   • Ciclos de 1 minuto = 60 ciclos/hora\n"
        log_content += f"   • Target: ≤60 requests/ciclo para ficar seguro\n"
        log_content += f"   • Status: {'✅ SEGURO' if self.requests_contador < 40 else '⚠️ MONITORAR' if self.requests_contador < 60 else '🔴 REDUZIR'}\n"
        
        return log_content
    
    def enviar_telegram(self, mensagem, para_canal=True):
        """Envia mensagem para o Telegram (chat pessoal e canal)."""
        resultados = []
        
        try:
            if not self.telegram_token:
                erro_msg = "⚠️ Token do Telegram não encontrado"
                print(erro_msg)
                logger_prod.error(erro_msg)
                return False
            
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            logger_prod.info(f"📱 TELEGRAM: Tentando enviar mensagem (para_canal={para_canal})")
            
            # Enviar para chat pessoal
            if self.chat_id:
                data_chat = {
                    'chat_id': self.chat_id,
                    'text': mensagem,
                    'parse_mode': 'HTML'
                }
                
                try:
                    response_chat = requests.post(url, data=data_chat, timeout=10)
                    
                    if response_chat.status_code == 200:
                        print("✅ Mensagem enviada para chat pessoal")
                        logger_prod.success("TELEGRAM: Mensagem enviada para chat pessoal")
                        resultados.append(True)
                    else:
                        erro_msg = f"❌ Falha ao enviar para chat pessoal - Status: {response_chat.status_code}, Resposta: {response_chat.text}"
                        print(erro_msg)
                        logger_prod.error(erro_msg)
                        resultados.append(False)
                        
                except requests.exceptions.Timeout:
                    erro_msg = "⏰ TIMEOUT: Falha ao enviar para chat pessoal - timeout de 10s"
                    print(erro_msg)
                    logger_prod.error(erro_msg)
                    resultados.append(False)
                except requests.exceptions.RequestException as e:
                    erro_msg = f"🌐 REDE: Erro de conexão para chat pessoal - {str(e)}"
                    print(erro_msg)
                    logger_prod.error(erro_msg)
                    resultados.append(False)
            else:
                logger_prod.warning("TELEGRAM: Chat ID não configurado")
            
            # Enviar para canal (se solicitado e configurado)
            if para_canal and self.channel_id:
                data_canal = {
                    'chat_id': self.channel_id,
                    'text': mensagem,
                    'parse_mode': 'HTML'
                }
                
                try:
                    response_canal = requests.post(url, data=data_canal, timeout=10)
                    
                    if response_canal.status_code == 200:
                        print("✅ Mensagem enviada para canal")
                        logger_prod.success("TELEGRAM: Mensagem enviada para canal")
                        resultados.append(True)
                    else:
                        erro_msg = f"❌ Falha ao enviar para canal - Status: {response_canal.status_code}, Resposta: {response_canal.text}"
                        print(erro_msg)
                        logger_prod.error(erro_msg)
                        resultados.append(False)
                        
                except requests.exceptions.Timeout:
                    erro_msg = "⏰ TIMEOUT: Falha ao enviar para canal - timeout de 10s"
                    print(erro_msg)
                    logger_prod.error(erro_msg)
                    resultados.append(False)
                except requests.exceptions.RequestException as e:
                    erro_msg = f"🌐 REDE: Erro de conexão para canal - {str(e)}"
                    print(erro_msg)
                    logger_prod.error(erro_msg)
                    resultados.append(False)
            elif para_canal and not self.channel_id:
                logger_prod.warning("TELEGRAM: Canal solicitado mas Channel ID não configurado")
            
            sucesso = any(resultados) if resultados else False
            if sucesso:
                logger_prod.success("TELEGRAM: Pelo menos um envio foi bem-sucedido")
            else:
                logger_prod.error("TELEGRAM: Todos os envios falharam")
                
            return sucesso
            
        except Exception as e:
            erro_msg = f"❌ ERRO CRÍTICO ao enviar mensagem no Telegram: {str(e)}"
            print(erro_msg)
            logger_prod.error(erro_msg)
            import traceback
            logger_prod.error(f"📋 TRACEBACK: {traceback.format_exc()}")
            return False
    
    def enviar_resultado_aposta(self, aposta_data, resultado_data):
        """Envia resultado de uma aposta específica no Telegram com estatísticas."""
        try:
            # Atualizar estatísticas antes de enviar
            self.atualizar_estatisticas(resultado_data['status'])
            
            # Gerar mensagens baseadas na sequência
            mensagem_sequencia = self.gerar_mensagem_sequencia(resultado_data['status'])
            estatisticas_resumo = self.gerar_estatisticas_resumo()
            
            # Determinar emoji e status baseado no resultado
            if resultado_data['status'] == 'GREEN':
                # Mensagem GREEN - Vitória! 🎉
                emoji_titulo = "🎾�"
                status_emoji = "🔥"
                reacao = ["🚀", "💸", "🎯", "💎", "⚡"][hash(aposta_data['id']) % 5]
                frase_motivacional = [
                    "BINGO! Acertamos na mosca! 🎯",
                    "SHOW! O palpite foi certeiro! 🔥", 
                    "TOP! Essa foi de primeira! ⚡",
                    "SUCESSO! Mandamos bem! 💎",
                    "PERFEITO! Era isso aí! �"
                ][hash(aposta_data['id']) % 5]
                
                mensagem = f"""{emoji_titulo} TennisIQ {emoji_titulo}

{status_emoji} <b>GREEN CONFIRMADO!</b> {reacao}

👑 <b>{mensagem_sequencia}</b>

🎾 {aposta_data['jogador_apostado']} vs {aposta_data['oponente']}

💚 <b>VITÓRIA CONFIRMADA!</b> 💚"""

            elif resultado_data['status'] == 'RED':
                # Mensagem RED - Derrota 😔
                emoji_titulo = "🎾❤️"
                status_emoji = "😤"
                reacao = ["💪", "🔄", "⚡", "🎯", "🚀"][hash(aposta_data['id']) % 5]
                frase_motivacional = [
                    "Dessa vez não rolou, mas vamos na próxima! 💪",
                    "Red hoje, Green amanhã! Bora lá! 🔄",
                    "Não foi dessa vez, mas seguimos firmes! ⚡",
                    "Tênis é imprevisível, próxima vem! 🎯",
                    "Faz parte do jogo! Vamos buscar o Green! 🚀"
                ][hash(aposta_data['id']) % 5]
                
                mensagem = f"""{emoji_titulo} TennisIQ {emoji_titulo}

{status_emoji} <b>RED</b> {reacao}

💪 <b>{mensagem_sequencia}</b>

🎾 {aposta_data['jogador_apostado']} vs {aposta_data['oponente']}

❤️ <b>PRÓXIMA SERÁ NOSSA!</b> ❤️"""

            else:  # VOID
                # Mensagem VOID - Empate/Cancelada 🤷‍♂️
                emoji_titulo = "🎾⚪"
                status_emoji = "🤷‍♂️"
                reacao = "💫"
                
                mensagem = f"""{emoji_titulo} TennisIQ {emoji_titulo}

{status_emoji} <b>VOID</b> {reacao}

Partida teve algum problema, aposta anulada! 🤷‍♂️

🎾 {aposta_data['jogador_apostado']} vs {aposta_data['oponente']}

⚪ <b>APOSTA ANULADA</b> ⚪"""

            # Enviar a mensagem
            sucesso = self.enviar_telegram(mensagem, para_canal=True)
            
            if sucesso:
                print(f"✅ Resultado {resultado_data['status']} enviado: {aposta_data['jogador_apostado']} vs {aposta_data['oponente']}")
                print(f"📊 Sequência atual: {self.greens_seguidos} greens seguidos")
            else:
                print(f"❌ Falha ao enviar resultado: {aposta_data['jogador_apostado']} vs {aposta_data['oponente']}")
            
            return sucesso
            
        except Exception as e:
            print(f"❌ Erro ao enviar resultado da aposta: {e}")
            return False
    
    def verificar_resultados_automatico(self):
        """Verifica automaticamente os resultados das apostas pendentes usando somente IDs."""
        if not self.verificador_resultados:
            return
        
        try:
            # Buscar apostas pendentes que têm ID válido
            apostas_pendentes = []
            for aposta in self.verificador_resultados.historico_apostas:
                if (aposta.get('status') == 'PENDENTE' and 
                    aposta.get('partida_id') and 
                    str(aposta['partida_id']).isdigit()):
                    apostas_pendentes.append(aposta)
            
            if not apostas_pendentes:
                print("📊 Nenhuma aposta pendente com ID encontrada")
                return
            
            print(f"📊 {len(apostas_pendentes)} aposta(s) pendente(s) com ID encontrada(s)")
            
            # Verificar cada aposta pendente usando ID
            novos_resultados = 0
            for aposta in apostas_pendentes:
                try:
                    partida_id = str(aposta['partida_id'])
                    jogador = aposta.get('jogador_apostado', 'N/A')
                    oponente = aposta.get('oponente', 'N/A')
                    
                    print(f"🔍 Verificando ID {partida_id}: {jogador} vs {oponente}")
                    
                    resultado = self.verificador_resultados.verificar_resultado_aposta(aposta)
                    
                    if resultado and resultado.get('status') in ['GREEN', 'RED', 'VOID']:
                        # Atualizar o status da aposta
                        aposta['status'] = resultado['status']
                        aposta['resultado_verificacao'] = resultado
                        aposta['motivo'] = resultado['motivo']
                        aposta['vencedor'] = resultado.get('jogador_winner', 'N/A')
                        aposta['data_verificacao'] = resultado['data_verificacao']
                        
                        # Adicionar aos resultados verificados
                        self.verificador_resultados.resultados_verificados.append(aposta.copy())
                        
                        # Enviar resultado no Telegram
                        self.enviar_resultado_aposta(aposta, resultado)
                        
                        novos_resultados += 1
                        status_emoji = "✅" if resultado['status'] == 'GREEN' else "❌" if resultado['status'] == 'RED' else "⚠️"
                        print(f"{status_emoji} ID {partida_id}: {resultado['status']} - {resultado['motivo']}")
                    
                    elif resultado and resultado.get('status') == 'PENDENTE':
                        print(f"⏳ ID {partida_id}: Ainda em andamento")
                    
                    elif resultado and resultado.get('status') == 'ERRO':
                        if 'não foi encontrada na API de dados' in resultado.get('motivo', ''):
                            print(f"❌ ID {partida_id}: Não foi encontrado resultado na API de dados")
                        else:
                            print(f"🔴 ID {partida_id}: {resultado.get('motivo', 'Erro desconhecido')}")
                    
                except Exception as e:
                    print(f"❌ Erro ao verificar ID {aposta.get('partida_id', 'N/A')}: {e}")
            
            # Salvar os arquivos atualizados se houve novos resultados
            if novos_resultados > 0:
                self.verificador_resultados.salvar_historico_apostas()
                self.verificador_resultados.salvar_resultados_verificados()
                print(f"💾 {novos_resultados} novo(s) resultado(s) salvos automaticamente")
            
        except Exception as e:
            print(f"❌ Erro na verificação automática: {e}")
        except Exception as e:
            print(f"❌ Erro na verificação automática de resultados: {e}")
    
    def notificar_ativacao(self):
        """Envia notificação de ativação do sistema."""
        agora = datetime.now()
        data_formatada = agora.strftime("%d/%m/%Y às %H:%M:%S")
        
        mensagem = f"""🟢 SISTEMA ATIVADO 🟢

✅ Status: Sistema Online
🕐 Horário: {data_formatada}
🤖 Bot: ATIVADO
🎾 Modalidade: Monitoramento de apostas

🚀 TennisIQ está funcionando!"""
        
        if self.enviar_telegram(mensagem):
            print("✅ Notificação de ativação enviada")
        else:
            print("❌ Falha ao enviar notificação de ativação")
    
    def notificar_desativacao(self):
        """Envia notificação de desativação do sistema."""
        agora = datetime.now()
        data_formatada = agora.strftime("%d/%m/%Y às %H:%M:%S")
        
        mensagem = f"""🔴 SISTEMA DESATIVADO 🔴

❌ Status: Sistema Offline
🕐 Horário: {data_formatada}
🤖 Bot: DESATIVADO
🎾 Modalidade: Monitoramento parado

⏹️ TennisIQ foi finalizado!"""
        
        if self.enviar_telegram(mensagem):
            print("✅ Notificação de desativação enviada")
        else:
            print("❌ Falha ao enviar notificação de desativação")
    
    def notificar_oportunidade(self, oportunidades):
        """Envia sinal TennisIQ para cada oportunidade encontrada."""
        if not oportunidades:
            return
        
        contador_sinais = 0
        
        for oportunidade in oportunidades:
            try:
                # Criar identificador único baseado na PARTIDA para evitar sinais duplicados
                partida_id = oportunidade.get('partida_id', '')
                jogador1 = oportunidade['jogador']
                jogador2 = oportunidade['oponente']
                
                # Criar ID único da partida independente da ordem dos jogadores
                jogadores_ordenados = sorted([jogador1, jogador2])
                partida_unica_id = f"{partida_id}-{jogadores_ordenados[0]}-{jogadores_ordenados[1]}"
                sinal_id = f"{partida_unica_id}-{jogador1}"  # ID do sinal específico do jogador
                
                # ID específico para VIRADA MENTAL
                sinal_id_virada_mental = f"{sinal_id}-VIRADA_MENTAL"
                
                # Verificar se esta PARTIDA já foi processada
                if partida_unica_id in self.partidas_processadas:
                    print(f"⏭️ Partida já processada: {jogador1} vs {jogador2}")
                    continue
                
                # Verificar se sinal já foi enviado para esta partida
                if sinal_id_virada_mental in self.sinais_enviados:
                    print(f"⏭️ Sinal já enviado para {jogador1} vs {jogador2}")
                    continue
                
                # Buscar odds atuais
                event_id = oportunidade.get('partida_id')
                if event_id:
                    odds_data = self.buscar_odds_evento(event_id)
                else:
                    odds_data = {'jogador1_odd': 'N/A', 'jogador2_odd': 'N/A'}
                
                # EXECUTAR ESTRATÉGIA VIRADA MENTAL
                jogador_analise = oportunidade.get('jogador', 'N/A')
                
                # Determinar estratégia para escolher o ID correto
                estrategia_tipo = self.determinar_estrategia_por_oportunidade(oportunidade)
                
                # Processar apenas VIRADA_MENTAL
                if estrategia_tipo == 'virada_mental':
                    sinal_id_atual = sinal_id_virada_mental
                    tipo_sinal = 'VIRADA_MENTAL'
                    
                    # Coletar dados dos filtros para armazenamento
                    dados_filtros = {
                        'timestamp_entrada': datetime.now().isoformat(),
                        'ev': oportunidade.get('ev', 0),
                        'momentum_score': oportunidade.get('momentum', 0),
                        'double_faults': oportunidade.get('double_faults', 0),
                        'win_1st_serve': oportunidade.get('win_1st_serve', 0),
                        'odd_final': odds_data.get('jogador1_odd', 0),
                        'filtros_aplicados': {
                            'timing_aprovado': oportunidade.get('prioridade_timing', 0) >= 3,
                            'ev_range': f"{oportunidade.get('ev', 0):.3f}",
                            'ms_range': f"{oportunidade.get('momentum', 0):.1f}%",
                            'df_range': oportunidade.get('double_faults', 0),
                            'w1s_range': f"{oportunidade.get('win_1st_serve', 0):.1f}%",
                            'odd_range': f"VIRADA_MENTAL"
                        },
                        'fase_timing': oportunidade.get('fase_timing', 'N/A'),
                        'placar_momento': oportunidade.get('placar', 'N/A'),
                        'liga': oportunidade.get('liga', 'N/A')
                    }
                    # Gerar sinal no formato TennisIQ com dados dos filtros
                    sinal = self.gerar_sinal_tennisiq(oportunidade, odds_data, dados_filtros)
                    
                    # Enviar sinal
                    if self.enviar_telegram(sinal):
                        # Usar ID específico da estratégia VIRADA_MENTAL
                        self.sinais_enviados.add(sinal_id_atual)
                        self.partidas_processadas.add(partida_unica_id)
                        contador_sinais += 1
                        print(f"🎯 Sinal {tipo_sinal} enviado: {oportunidade['jogador']} vs {oportunidade['oponente']}")
                        print(f"🔒 Partida bloqueada para futuras duplicatas: {partida_unica_id}")
                        
                        # Calcular EV se não estiver disponível para log de sinal
                        ev_partida = oportunidade.get('ev', 0)
                        odd_valor_sinal = odds_data.get('jogador1_odd', 0)
                        
                        if ev_partida == 0:
                            # Calcular EV usando momentum e odds disponíveis
                            momentum = oportunidade.get('momentum', 0)
                            odd_valor_raw = odds_data.get('jogador1_odd', 0)
                            
                            # Verificar se a odd é válida (não é "-", "N/A", etc.)
                            try:
                                odd_valor_calc = float(odd_valor_raw) if odd_valor_raw not in ['-', 'N/A', None, ''] else 0
                            except (ValueError, TypeError):
                                odd_valor_calc = 0
                                
                            if momentum > 0 and odd_valor_calc > 1:
                                try:
                                    probabilidade = momentum / 100
                                    ev_partida = (probabilidade * odd_valor_calc) - 1
                                except:
                                    ev_partida = 0
                        
                        # Log sinal gerado para VIRADA_MENTAL
                        dashboard_logger.log_sinal_gerado(
                            tipo=tipo_sinal,
                            target=oportunidade['jogador'],
                            odd=odd_valor_sinal,
                            ev=ev_partida,
                            confianca=80.0,
                            mental_score=oportunidade.get('momentum', 0),
                            fatores_mentais=[oportunidade.get('justificativa', '')]
                        )
                        
                        # Coletar estatísticas reais para o dashboard
                        stats_reais = self.coletar_estatisticas_reais(event_id)
                        
                        # Log partida analisada com sucesso
                        dashboard_logger.log_partida_analisada(
                            jogador1=jogador1,
                            jogador2=oportunidade.get('oponente', 'N/A'),
                            placar=oportunidade.get('placar', 'N/A'),
                            odds1=odds_data.get('jogador1_odd', 0),
                            odds2=odds_data.get('jogador2_odd', 0),
                            ev=ev_partida,
                            momentum_score=oportunidade.get('momentum', 0),
                            timing_priority=oportunidade.get('prioridade_timing', 0),
                            mental_score=oportunidade.get('momentum', 0),
                            decisao=f'SINAL_{tipo_sinal}',
                            motivo=f'Aprovado pela estratégia {tipo_sinal}',
                            stats_jogador1=stats_reais.get('stats_jogador1', {}),
                            stats_jogador2=stats_reais.get('stats_jogador2', {})
                        )
                        
                        # Registrar aposta automaticamente no sistema de resultados
                        if RESULTADOS_DISPONIVEL and integrador_resultados:
                            try:
                                aposta_id = integrador_resultados.registrar_aposta_automatica(oportunidade, odds_data, dados_filtros)
                                if aposta_id:
                                    print(f"📊 Aposta registrada para verificação: {aposta_id}")
                                    print(f"🔍 Dados dos filtros armazenados: EV={dados_filtros['ev']:.3f}, MS={dados_filtros['momentum_score']:.1f}%, DF={dados_filtros['double_faults']}, W1S={dados_filtros['win_1st_serve']:.1f}%")
                            except Exception as e:
                                print(f"⚠️ Erro ao registrar aposta: {e}")
                    else:
                        print(f"❌ Falha ao enviar sinal: {oportunidade['jogador']} vs {oportunidade['oponente']}")
                else:
                    # Estratégia não reconhecida - pular
                    print(f"⚠️ Estratégia não reconhecida para: {oportunidade['jogador']} vs {oportunidade['oponente']}")
                
                # Pequena pausa entre sinais
                time.sleep(1)  # Reduzido de 2 para 1 segundo
                
            except Exception as e:
                print(f"⚠️ Erro ao processar oportunidade: {e}")
        
        if contador_sinais > 0:
            print(f"✅ {contador_sinais} sinal(is) TennisIQ enviado(s) com sucesso!")
        else:
            print("📭 Nenhum sinal novo para enviar neste ciclo")
    
    def validar_timing_inteligente(self, oportunidade, estrategia_tipo, score_mental=0):
        """
        Validação de timing adaptada por tipo de estratégia - LIBERADO 24H
        """
        # SISTEMA LIBERADO 24 HORAS - SEM RESTRIÇÕES DE HORÁRIO
        print(f"� Timing liberado 24h para estratégia {estrategia_tipo}")
        return True
    
    def extrair_odd_jogador(self, odds_data, jogador):
        """Extrai a odd do jogador principal baseado no seu nome real"""
        if not isinstance(odds_data, dict):
            return 1.8
            
        try:
            # Primeiro verificar se temos o event_id e os nomes dos jogadores
            event_id = odds_data.get('event_id')
            if not event_id:
                logger_prod.warning("Event ID não disponível para mapear odds corretamente")
                return odds_data.get('jogador1_odd', 1.8)
            
            # Buscar nomes reais dos jogadores HOME e AWAY
            nomes_reais = self.buscar_nomes_jogadores_reais(event_id)
            if not nomes_reais:
                logger_prod.warning(f"Não foi possível obter nomes reais para evento {event_id}")
                return odds_data.get('jogador1_odd', 1.8)
            
            jogador_home = nomes_reais.get('home', '')
            jogador_away = nomes_reais.get('away', '')
            
            # 🔍 LOG DETALHADO PARA DEBUG
            logger_ultra.info(f"🔍 MAPEAMENTO ODDS - Jogador Buscado: '{jogador}'")
            logger_ultra.info(f"🏠 HOME da API: '{jogador_home}' → Odd: {odds_data.get('jogador1_odd', 'N/A')}")
            logger_ultra.info(f"✈️ AWAY da API: '{jogador_away}' → Odd: {odds_data.get('jogador2_odd', 'N/A')}")
            
            # Verificar se o jogador é HOME ou AWAY usando similaridade de nomes
            if self.nomes_similares(jogador, jogador_home):
                resultado_odd = odds_data.get('jogador1_odd', 1.8)
                logger_ultra.info(f"✅ '{jogador}' = HOME '{jogador_home}' → Odd: {resultado_odd}")
                return resultado_odd
            elif self.nomes_similares(jogador, jogador_away):
                resultado_odd = odds_data.get('jogador2_odd', 2.1)
                logger_ultra.info(f"✅ '{jogador}' = AWAY '{jogador_away}' → Odd: {resultado_odd}")
                return resultado_odd
            else:
                logger_ultra.warning(f"⚠️ Jogador '{jogador}' NÃO encontrado entre HOME '{jogador_home}' e AWAY '{jogador_away}'")
                resultado_odd = odds_data.get('jogador1_odd', 1.8)
                logger_ultra.info(f"🔄 Usando odd padrão: {resultado_odd}")
                return resultado_odd
                
        except Exception as e:
            logger_prod.error(f"Erro ao extrair odd do jogador '{jogador}': {e}")
            return odds_data.get('jogador1_odd', 1.8)
    
    def extrair_odd_oponente(self, odds_data, oponente):
        """Extrai a odd do oponente baseado no seu nome real"""
        if not isinstance(odds_data, dict):
            return 2.1
            
        try:
            # Primeiro verificar se temos o event_id e os nomes dos jogadores
            event_id = odds_data.get('event_id')
            if not event_id:
                logger_prod.warning("Event ID não disponível para mapear odds do oponente corretamente")
                return odds_data.get('jogador2_odd', 2.1)
            
            # Buscar nomes reais dos jogadores HOME e AWAY
            nomes_reais = self.buscar_nomes_jogadores_reais(event_id)
            if not nomes_reais:
                logger_prod.warning(f"Não foi possível obter nomes reais do oponente para evento {event_id}")
                return odds_data.get('jogador2_odd', 2.1)
            
            jogador_home = nomes_reais.get('home', '')
            jogador_away = nomes_reais.get('away', '')
            
            # Verificar se o oponente é HOME ou AWAY usando similaridade de nomes
            if self.nomes_similares(oponente, jogador_home):
                # Oponente é HOME - retornar jogador1_odd (que vem de home_od)
                return odds_data.get('jogador1_odd', 1.8)
            elif self.nomes_similares(oponente, jogador_away):
                # Oponente é AWAY - retornar jogador2_odd (que vem de away_od)
                return odds_data.get('jogador2_odd', 2.1)
            else:
                logger_prod.warning(f"Oponente '{oponente}' não encontrado entre HOME '{jogador_home}' e AWAY '{jogador_away}'")
                return odds_data.get('jogador2_odd', 2.1)
                
        except Exception as e:
            logger_prod.error(f"Erro ao extrair odd do oponente '{oponente}': {e}")
            return odds_data.get('jogador2_odd', 2.1)
    
    def buscar_nomes_jogadores_reais(self, event_id):
        """Busca os nomes reais dos jogadores HOME e AWAY da API"""
        try:
            # Verificar cache primeiro
            cache_key = f"nomes_{event_id}"
            agora = time.time()
            
            if hasattr(self, 'cache_nomes'):
                if cache_key in self.cache_nomes:
                    timestamp, nomes = self.cache_nomes[cache_key]
                    if agora - timestamp < 300:  # Cache por 5 minutos
                        return nomes
            else:
                self.cache_nomes = {}
            
            # Buscar na API
            url = f"{self.base_url}/v3/events/inplay"
            params = {
                'token': self.api_key,
                'sport_id': 13  # Tênis
            }
            
            # Registrar requisição
            api_rate_limiter.register_request()
            self.requests_contador += 1
            
            response = requests.get(url, params=params, timeout=3)
            
            if response.status_code == 429:
                api_rate_limiter.register_429_error()
                logger_prod.rate_limit_429(url)
                return None
            
            response.raise_for_status()
            data = response.json()
            
            if data.get('success') == 1 and 'results' in data:
                for evento in data['results']:
                    if str(evento.get('id')) == str(event_id):
                        nomes = {
                            'home': evento.get('home', {}).get('name', ''),
                            'away': evento.get('away', {}).get('name', '')
                        }
                        
                        # Salvar no cache
                        self.cache_nomes[cache_key] = (agora, nomes)
                        
                        logger_prod.log('DEBUG', f"✅ Nomes obtidos para evento {event_id}: HOME={nomes['home']}, AWAY={nomes['away']}")
                        return nomes
            
            return None
            
        except Exception as e:
            logger_prod.error(f"Erro ao buscar nomes dos jogadores para evento {event_id}: {e}")
            return None
    
    def nomes_similares(self, nome1, nome2):
        """Verifica se dois nomes são similares o suficiente para serem considerados o mesmo jogador"""
        if not nome1 or not nome2:
            return False
        
        # Normalizar nomes (remover acentos, converter para minúsculas, remover espaços extras)
        def normalizar_nome(nome):
            import unicodedata
            nome = unicodedata.normalize('NFD', nome.lower())
            nome = ''.join(c for c in nome if not unicodedata.combining(c))
            return ' '.join(nome.split())
        
        nome1_norm = normalizar_nome(nome1)
        nome2_norm = normalizar_nome(nome2)
        
        # Verificar se são exatamente iguais após normalização
        if nome1_norm == nome2_norm:
            return True
        
        # Verificar se um nome está contido no outro (para casos como "J. Smith" vs "John Smith")
        if nome1_norm in nome2_norm or nome2_norm in nome1_norm:
            return True
        
        # Verificar similaridade de palavras (útil para nomes com variações)
        palavras1 = set(nome1_norm.split())
        palavras2 = set(nome2_norm.split())
        
        # Se tem palavras em comum e pelo menos 50% de overlap
        intersecao = palavras1.intersection(palavras2)
        uniao = palavras1.union(palavras2)
        
        if intersecao and len(intersecao) / len(uniao) >= 0.5:
            return True
        
        return False
    
    def identificar_contexto_partida(self, oportunidade):
        """Identifica o contexto da partida para análise mental e timing"""
        placar = oportunidade.get('placar', '')
        fase = oportunidade.get('fase_timing', '')
        
        contexto = []
        
        # Detectar qual set está sendo jogado baseado no placar
        if placar:
            # Analisar estrutura do placar para identificar sets
            sets_jogados = placar.count('-') + placar.count(':')
            
            # 1º set em andamento (sem sets finalizados)
            if sets_jogados <= 1 and not any(x in placar for x in ['6-', '7-']):
                contexto.append('1º set')
            
            # 2º set em andamento (1 set finalizado)
            elif '6-' in placar or '7-' in placar:
                # Verificar se há 2 sets completos (seria 3º set)
                sets_completos = placar.count('6-') + placar.count('7-')
                if sets_completos == 1:
                    contexto.append('2º set')
                elif sets_completos >= 2:
                    contexto.append('3º set')
        
        # Detectar 3º set por outros indicadores
        if '0-0' in placar and len(placar.split(',')) == 3:
            contexto.append('3º set')
        
        # Detectar tie-break
        if '7-6' in placar or '6-7' in placar or 'tie-break' in fase.lower():
            contexto.append('tie-break')
        
        # Detectar sets empatados
        if '1-1' in placar or 'empatado' in fase.lower():
            contexto.append('sets empatados')
        
        return ', '.join(contexto) if contexto else 'início da partida'
    
    def aplicar_filtros_rigidos(self, oportunidade):
        """
        Aplica filtros rigorosos de produção - ADAPTADO PARA VIRADA_MENTAL
        """
        try:
            # Para VIRADA_MENTAL, usamos critérios mais flexíveis
            # Momentum Score mínimo para virada mental é menor (50%)
            momentum = oportunidade.get('momentum', 0)
            if momentum < 50:
                return False
            
            return True
            
        except Exception as e:
            print(f"⚠️ Erro nos filtros rígidos: {e}")
            return False
            
            # Usar horário de Brasília (UTC-3)
            agora = datetime.now(timezone(timedelta(hours=-3)))
            horario = agora.strftime("%H:%M")
            
            # Gerar link direto da Bet365 (se disponível)
            event_id = sinal.get('event_id', '')
            bet365_link = bet365_manager.generate_link(event_id) if event_id else "Link não disponível"
            
            # Montar sinal no formato padrão TennisIQ
            mensagem = f"""🎾 TennisIQ - Sinal - Invertida 🔁

{oponente} vs {jogador_alvo}
⏰ {horario}

� APOSTAR EM: {jogador_alvo} 🚀
� Odd: {odd_alvo}
⚠️ Limite Mínimo: {odd_minima} (não apostar abaixo)

🔗 Link direto: https://www.bet365.bet.br/?_h=LKUUnzn5idsD_NCCi9iyvQ%3D%3D&btsffd=1#/IP/EV10459378C13

#TennisIQ"""
            
            # Salvar log da aposta invertida
            self.log_aposta_invertida(sinal)
            
            # Enviar via Telegram
            return self.enviar_telegram(mensagem)
            
        except Exception as e:
            print(f"❌ Erro ao enviar sinal invertido: {e}")
            return False
    
    def log_aposta_invertida(self, sinal):
        """Log específico para apostas invertidas"""
        try:
            log_entry = {
                'timestamp': sinal['timestamp'],
                'tipo': 'APOSTA_INVERTIDA',
                'partida_original': sinal['partida_original'],
                'target_invertido': sinal['jogador_alvo'],
                'odd_invertida': sinal['odd_alvo'],
                'score_mental': sinal['score_mental'],
                'fatores': sinal['fatores_mentais'],
                'ev_estimado': sinal['ev_estimado'],
                'confianca': sinal['confianca']
            }
            
            self.apostas_invertidas.append(log_entry)
            
            # Salvar em arquivo separado
            with open('apostas_invertidas.json', 'w', encoding='utf-8') as f:
                json.dump(self.apostas_invertidas, f, ensure_ascii=False, indent=2)
            
            print(f"📝 Log da aposta invertida salvo: {sinal['jogador_alvo']}")
            
        except Exception as e:
            print(f"⚠️ Erro ao salvar log da aposta invertida: {e}")
    
    def aplicar_filtros_rigidos(self, oportunidade):
        """
        Aplica filtros rigorosos de produção - SINCRONIZADO COM SELEÇÃO_FINAL
        """
        try:
            # EV mínimo ajustado para 0.15 (sincronizado)
            ev = oportunidade.get('ev', 0)
            if ev < 0.15:
                logger_formatado.log_estrategia('tradicional', 'rejeicao', f'EV {ev:.3f} < 0.15 (mínimo)', oportunidade.get('jogador'))
                return False
            
            # Momentum Score mínimo mantido em 65%
            momentum = oportunidade.get('momentum', 0)
            if momentum < 65:
                logger_formatado.log_estrategia('tradicional', 'rejeicao', f'Momentum {momentum:.1f}% < 65% (mínimo)', oportunidade.get('jogador'))
                return False
            
            # Win 1st Serve mínimo ajustado para 65% (sincronizado)
            win_1st = oportunidade.get('win_1st_serve', 0)
            if win_1st < 65:
                logger_formatado.log_estrategia('tradicional', 'rejeicao', f'Win 1st Serve {win_1st:.1f}% < 65% (mínimo)', oportunidade.get('jogador'))
                return False
            
            # Double Faults máximo ajustado para 4 (sincronizado)
            double_faults = oportunidade.get('double_faults', 0)
            if double_faults > 4:
                logger_formatado.log_estrategia('tradicional', 'rejeicao', f'Double faults {double_faults} > 4 (máximo)', oportunidade.get('jogador'))
                return False
            
            # NOVO: Validação de timing inteligente para tradicional
            timing_aprovado = self.validar_timing_inteligente(oportunidade, 'TRADICIONAL')
            if not timing_aprovado:
                logger_formatado.log_estrategia('tradicional', 'rejeicao', 'Horário inadequado para estratégia tradicional', oportunidade.get('jogador'))
                return False
            
            # BLOQUEIOS CONTEXTUAIS
            contexto = self.identificar_contexto_partida(oportunidade)
            
            if '3º set' in contexto:
                logger_formatado.log_estrategia('tradicional', 'rejeicao', '3º set detectado (bloqueio contextual)', oportunidade.get('jogador'))
                return False
            
            if 'pós tie-break' in contexto:
                logger_formatado.log_estrategia('tradicional', 'rejeicao', 'Pós tie-break detectado (bloqueio contextual)', oportunidade.get('jogador'))
                return False
            
            if 'sets empatados' in contexto:
                logger_formatado.log_estrategia('tradicional', 'rejeicao', 'Sets empatados detectado (bloqueio contextual)', oportunidade.get('jogador'))
                return False
            
            logger_formatado.log_estrategia('tradicional', 'sucesso', 'Todos os filtros rígidos aprovados', oportunidade.get('jogador'))
            return True
            
        except Exception as e:
            print(f"⚠️ Erro ao aplicar filtros rígidos: {e}")
            return False

    def signal_handler(self, signum, frame):
        """Handler para o sinal Ctrl+C."""
        print("\n🔴 Recebido sinal de interrupção...")
        self.running = False
        self.notificar_desativacao()
        print("🔴 Sistema finalizado!")
        sys.exit(0)
    
    def executar_monitoramento(self):
        """Executa o ciclo principal de monitoramento 24h."""
        logger_prod.success("TennisIQ Bot - Iniciando Monitoramento 24h...")
        logger_ultra.success("🚀 TENNISIQ BOT INICIADO - ALAVANCAGEM OTIMIZADA ATIVA")
        
        # Configurar verbosidade baseada no ambiente
        if LOGGER_FORMATADO_DISPONIVEL:
            logger_formatado.set_verbosidade("MINIMAL" if logger_prod.is_production else "NORMAL")
        
        # Enviar notificação de ativação
        self.notificar_ativacao()
        
        logger_prod.info("Bot ativo - Monitorando oportunidades 24/7")
        logger_prod.info("Verificações a cada 45 segundos")
        logger_prod.info("Rate limiting aplicado para API")
        logger_ultra.info("🎯 Sistema de alavancagem otimizado carregado (odds 1.15-1.60)")
        
        contador_ciclos = 0
        contador_oportunidades_total = 0
        
        while self.running:
            try:
                contador_ciclos += 1
                agora = datetime.now()
                agora_timestamp = time.time()  # Para operações de cache que precisam de float
                
                # Limpar cache antigo a cada ciclo
                self.limpar_cache_antigo()
                
                # Resetar contador de requests a cada hora
                if agora.hour != self.hora_atual:
                    stats = api_rate_limiter.get_stats()
                    logger_prod.info(f"Nova hora - Requests última hora: {stats['requests_last_hour']}")
                    self.requests_contador = 0
                    self.hora_atual = agora.hour
                
                # === INÍCIO DO CICLO ===
                logger_prod.ciclo_inicio(contador_ciclos)
                logger_ultra.novo_ciclo()  # Reset para novo ciclo
                logger_ultra.info(f"🔄 CICLO {contador_ciclos} - Verificando alavancagem")
                
                # Reset cache de estratégias para novo ciclo
                self._estrategias_testadas_cache = {}
                
                # Limpar cache de odds antigo (> 45s)
                cache_keys_para_remover = []
                for key, (timestamp, _) in self.cache_odds.items():
                    if agora_timestamp - timestamp > self.cache_odds_timeout:
                        cache_keys_para_remover.append(key)
                
                for key in cache_keys_para_remover:
                    del self.cache_odds[key]
                
                if cache_keys_para_remover:
                    logger_ultra.info(f"🧹 Cache limpo: {len(cache_keys_para_remover)} odds antigas removidas")
                
                # Rate limiting stats
                rate_stats = api_rate_limiter.get_stats()
                
                # Atualizar status do bot no dashboard
                dashboard_logger.atualizar_status_bot(
                    ativo=True,
                    requests_restantes=3600 - rate_stats['requests_last_hour'],
                    proxima_verificacao=(agora + timedelta(seconds=45)).isoformat()
                )
                
                # Reset contador de requests do ciclo
                requests_inicio_ciclo = self.requests_contador
                
                # Limpar dados das partidas para novo ciclo
                try:
                    from ..data.opportunities.seleção_final import limpar_dados_partidas
                    limpar_dados_partidas()
                except ImportError:
                    pass
                
                # Executar análise de oportunidades
                oportunidades = analisar_ev_partidas()
                
                # Buscar dados reais das partidas para o logger
                try:
                    from ..data.opportunities.seleção_final import get_dados_partidas_para_logger
                    dados_partidas = get_dados_partidas_para_logger()
                    total_partidas_real = dados_partidas['total_partidas']
                    aprovadas_timing_real = dados_partidas['aprovadas_timing']
                    partidas_timing = dados_partidas['partidas_timing']
                except ImportError:
                    # Fallback se não conseguir importar
                    total_partidas_real = 0
                    aprovadas_timing_real = 0
                    partidas_timing = []
                
                # Corrigir estatísticas se há oportunidades mas dados zerados
                if oportunidades and len(oportunidades) > 0:
                    if total_partidas_real == 0:
                        # Estimar baseado nas oportunidades encontradas
                        total_partidas_real = len(oportunidades) * 2  # Estimativa: cada oportunidade vem de ~2 partidas analisadas
                        aprovadas_timing_real = len(oportunidades)  # No mínimo as oportunidades passaram no timing
                
                # Log da coleta de dados
                requests_usados = self.requests_contador - requests_inicio_ciclo
                logger_formatado.log_coleta_dados(
                    total_partidas=total_partidas_real,
                    aprovadas_timing=aprovadas_timing_real,
                    requests_usados=requests_usados
                )
                
                # Log das partidas prioritárias
                if partidas_timing:
                    logger_formatado.log_partidas_prioritarias(partidas_timing)
                
                # Log das oportunidades encontradas
                if oportunidades:
                    total_oportunidades = len(oportunidades)
                    contador_oportunidades_total += total_oportunidades
                    
                    # Log otimizado de oportunidades
                    for op in oportunidades:
                        ev = op.get('ev', 0)
                        jogador = op.get('jogador', 'N/A')
                        logger_prod.oportunidade_encontrada(jogador, ev)
                    
                    if LOGGER_FORMATADO_DISPONIVEL:
                        # Converter oportunidades para formato do logger formatado
                        oportunidades_formatadas = []
                        for op in oportunidades:
                            ev = op.get('ev', 0)
                            momentum = op.get('momentum', 70)
                            
                            # Estimativa de odd baseada no EV e momentum
                            if ev > 0.3:
                                odd_estimada = 2.0 + (ev * 0.5)
                            elif ev > 0.15:
                                odd_estimada = 1.8 + (ev * 1.0)
                            else:
                                odd_estimada = 1.5 + (momentum / 50)
                            
                            odd_estimada = max(1.2, min(3.0, odd_estimada))
                            
                            oportunidades_formatadas.append({
                                'jogador': op.get('jogador', 'N/A'),
                                'odd': round(odd_estimada, 2),
                                'estrategia': 'RIGOROSA',
                                'confianca': min(90, max(60, int(momentum)))
                            })
                        
                        logger_formatado.log_oportunidades_encontradas(oportunidades_formatadas)
                    
                    self.notificar_oportunidade(oportunidades)
                else:
                    if LOGGER_FORMATADO_DISPONIVEL:
                        logger_formatado.log_oportunidades_encontradas([])
                
                # Verificar resultados das apostas (reduzido)
                if contador_ciclos % 2 == 0:
                    logger_prod.log('DEBUG', "Verificando resultados automaticamente...")
                    self.verificar_resultados_automatico()
                
                # Verificar se é hora de enviar relatórios
                self.verificar_horario_relatorios()
                
                # === RESUMO DO CICLO ===
                requests_usados = self.requests_contador - requests_inicio_ciclo
                rate_stats = api_rate_limiter.get_stats()
                
                # Log resumo das estratégias (NOVO)
                logger_estrategias.log_resumo_ciclo()
                
                # Log de estatísticas do ciclo
                logger_prod.stats_ciclo(
                    total_partidas_real if 'total_partidas_real' in locals() else 0,
                    aprovadas_timing_real if 'aprovadas_timing_real' in locals() else 0,
                    len(oportunidades) if oportunidades else 0,
                    rate_stats['requests_last_hour']
                )
                
                if LOGGER_FORMATADO_DISPONIVEL:
                    stats_ciclo = {
                        'partidas_analisadas': total_partidas_real if 'total_partidas_real' in locals() else 0,
                        'timing_aprovadas': aprovadas_timing_real if 'aprovadas_timing_real' in locals() else 0,
                        'taxa_timing': (aprovadas_timing_real / total_partidas_real * 100) if 'total_partidas_real' in locals() and total_partidas_real > 0 else 0,
                        'oportunidades_encontradas': len(oportunidades) if oportunidades else 0,
                        'taxa_conversao': (len(oportunidades) / aprovadas_timing_real * 100) if 'aprovadas_timing_real' in locals() and aprovadas_timing_real > 0 else 0,
                        'requests_usados': requests_usados,
                        'proximo_ciclo': 45,
                        'sistema_ativo': True
                    }
                    logger_formatado.log_resumo_ciclo(stats_ciclo)
                
                # Rate limiting inteligente CORRIGIDO (mais conservador)
                requests_hora = rate_stats['requests_last_hour']
                
                # Log de monitoramento detalhado
                if requests_hora > 1200:  # 33% do limite (3600) - CORRIGIDO
                    logger_ultra.warning(f"⚠️ API Usage: {requests_hora}/3600 ({(requests_hora/3600)*100:.1f}%)")
                
                if requests_hora > 2800:  # 78% do limite (3600) - CORRIGIDO
                    logger_prod.warning("CRÍTICO: Muito próximo do limite da API!")
                    logger_ultra.warning(f"🚨 CRÍTICO: {requests_hora}/3600 requests")
                    tempo_espera = 120  # 2 minutos - AUMENTADO
                elif requests_hora > 2200:  # 61% do limite - CORRIGIDO
                    logger_prod.warning("ATENÇÃO: Aproximando do limite da API")
                    logger_ultra.warning(f"⚠️ ALTO: {requests_hora}/3600 requests")
                    tempo_espera = 90   # 1.5 minutos - AUMENTADO
                elif requests_hora > 1600:   # 44% do limite - CORRIGIDO
                    logger_prod.warning("MODERADO: Monitorando uso da API")
                    tempo_espera = 75   # 1.25 minutos
                elif requests_hora > 1200:   # 33% do limite - CORRIGIDO
                    tempo_espera = 65   # Anteriormente era padrão
                else:
                    tempo_espera = 55   # Padrão mantido
                
                # Sleep para próximo ciclo
                time.sleep(tempo_espera)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger_prod.error(f"Erro durante monitoramento: {e}")
                logger_prod.warning("Tentando novamente em 15 segundos...")
                time.sleep(15)
        
        # Finalizar logger
        logger_prod.finalizar()

def main():
    """Função principal do bot."""
    try:
        bot = TennisIQBot()
        bot.executar_monitoramento()
    except Exception as e:
        print(f"❌ Erro crítico: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
