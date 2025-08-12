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

# Importar logger formatado
try:
    from ..utils.logger_formatado import logger_formatado
    LOGGER_FORMATADO_DISPONIVEL = True
    print("✅ Logger formatado carregado - Logs organizados ativados")
except ImportError:
    # Fallback caso não consiga importar
    class LoggerFallback:
        def set_verbosidade(self, nivel): pass
        def log_inicio_ciclo(self, ciclo): print(f"🔄 Ciclo {ciclo}")
        def log_coleta_dados(self, total, aprovadas, requests=0): print(f"📡 {total} partidas • {aprovadas} timing OK")
        def log_partidas_prioritarias(self, partidas): pass
        def log_analise_filtros(self, resultados): pass
        def log_oportunidades_encontradas(self, oportunidades): pass
        def log_resumo_ciclo(self, stats): print(f"📈 Ciclo finalizado")
        def log_erro(self, msg, detalhes=None): print(f"🚨 {msg}")
        def log_aviso(self, msg): print(f"⚠️ {msg}")
        def log_debug(self, msg): pass
    
    logger_formatado = LoggerFallback()
    LOGGER_FORMATADO_DISPONIVEL = False
    print("⚠️ Logger formatado não disponível - usando fallback")

# Importações condicionais baseadas no contexto de execução
try:
    from .extrair_stats_jogadores import extrair_stats_completas
    from .detector_vantagem_mental import DetectorVantagemMental
    from .detector_alavancagem import DetectorAlavancagem
    from ..services.dashboard_logger import dashboard_logger
except ImportError:
    # Execução direta - ajustar imports
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from core.extrair_stats_jogadores import extrair_stats_completas
    from core.detector_vantagem_mental import DetectorVantagemMental
    from core.detector_alavancagem import DetectorAlavancagem
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
        self.apostas_invertidas = []  # Track separado para apostas invertidas
        
        # NOVO: Sistema de Alavancagem
        self.detector_alavancagem = DetectorAlavancagem()
        self.apostas_alavancagem = []  # Track separado para apostas de alavancagem
        
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
        """Busca as odds de um evento específico usando a mesma estrutura do partidas.py."""
        url = f"{self.base_url}/v3/event/odds"
        params = {
            'event_id': event_id,
            'token': self.api_key
        }
        
        try:
            self.requests_contador += 1  # Incrementar contador de requests
            response = requests.get(url, params=params, timeout=3)  # Reduzido de 5 para 3 segundos
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
                            return {
                                'jogador1_odd': latest_odds.get('home_od', 'N/A'),
                                'jogador2_odd': latest_odds.get('away_od', 'N/A')
                            }
            
            return {'jogador1_odd': 'N/A', 'jogador2_odd': 'N/A'}
            
        except Exception as e:
            print(f"⚠️ Erro ao buscar odds para evento {event_id}: {e}")
            return {'jogador1_odd': 'N/A', 'jogador2_odd': 'N/A'}
    
    def coletar_estatisticas_reais(self, event_id):
        """Coleta estatísticas reais dos jogadores usando o extrator personalizado."""
        try:
            if not event_id:
                print("⚠️ Event ID não disponível para coleta de stats")
                return {
                    'stats_jogador1': {},
                    'stats_jogador2': {}
                }
            
            print(f"📊 Coletando estatísticas reais para evento {event_id}...")
            stats = extrair_stats_completas(event_id, self.api_key, self.base_url)
            
            if stats and stats.get('stats_jogador1') and stats.get('stats_jogador2'):
                j1_stats = stats['stats_jogador1']
                j2_stats = stats['stats_jogador2']
                
                # Verificar se pelo menos uma estatística não é zero
                j1_total = sum(j1_stats.values())
                j2_total = sum(j2_stats.values())
                
                if j1_total > 0 or j2_total > 0:
                    print(f"✅ Estatísticas coletadas: J1 Total={j1_total}, J2 Total={j2_total}")
                    return stats
                else:
                    print("⚠️ Estatísticas coletadas estão vazias")
            
            return {
                'stats_jogador1': {},
                'stats_jogador2': {}
            }
            
        except Exception as e:
            print(f"❌ Erro ao coletar estatísticas reais: {e}")
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
    
    def validar_filtros_odds(self, oportunidade, odds_data):
        """Valida se a aposta passa nos filtros de odds (1.8 a 2.2)."""
        try:
            # Determinar a odd correta baseado no tipo (HOME ou AWAY)
            if oportunidade.get('tipo') == 'HOME':
                odd_atual = odds_data.get('jogador1_odd', 'N/A')
            else:
                odd_atual = odds_data.get('jogador2_odd', 'N/A')
            
            # Converter para float para validação
            if odd_atual == 'N/A' or odd_atual == '-':
                print(f"❌ Odd não disponível para {oportunidade['jogador']}")
                return False, None
            
            odd_float = float(odd_atual)
            
            # FILTRO CRÍTICO: Odds entre 1.8 e 2.2 (baseado na análise)
            if not (1.8 <= odd_float <= 2.2):
                print(f"❌ Odd {odd_float} fora do range 1.8-2.2 para {oportunidade['jogador']}")
                return False, odd_float
            
            print(f"✅ Odd {odd_float} aprovada para {oportunidade['jogador']}")
            return True, odd_float
            
        except (ValueError, TypeError) as e:
            print(f"❌ Erro ao validar odd para {oportunidade['jogador']}: {e}")
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
        
        # Montar sinal básico
        sinal = f"""🎾 TennisIQ - Sinal - Tradicional 🔥

{oponente} vs {jogador_alvo}
⏰ {horario}

🚀 APOSTAR EM: {jogador_alvo} 🚀
💰 Odd: {odd_atual}
⚠️ Limite Mínimo: {odd_minima} (não apostar abaixo)

🔗 Link direto: {bet365_link}

#TennisIQ"""
        
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
                print("⚠️ Token do Telegram não encontrado")
                return False
            
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            
            # Enviar para chat pessoal
            if self.chat_id:
                data_chat = {
                    'chat_id': self.chat_id,
                    'text': mensagem,
                    'parse_mode': 'HTML'
                }
                
                response_chat = requests.post(url, data=data_chat, timeout=5)  # Reduzido de 10 para 5 segundos
                resultados.append(response_chat.status_code == 200)
                
                if response_chat.status_code == 200:
                    print("✅ Mensagem enviada para chat pessoal")
                else:
                    print("❌ Falha ao enviar para chat pessoal")
            
            # Enviar para canal (se solicitado e configurado)
            if para_canal and self.channel_id:
                data_canal = {
                    'chat_id': self.channel_id,
                    'text': mensagem,
                    'parse_mode': 'HTML'
                }
                
                response_canal = requests.post(url, data=data_canal, timeout=5)  # Reduzido de 10 para 5 segundos
                resultados.append(response_canal.status_code == 200)
                
                if response_canal.status_code == 200:
                    print("✅ Mensagem enviada para canal")
                else:
                    print("❌ Falha ao enviar para canal")
            
            return any(resultados) if resultados else False
            
        except Exception as e:
            print(f"❌ Erro ao enviar mensagem no Telegram: {e}")
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
                
                # Verificar se esta PARTIDA já foi processada (independente do jogador)
                if partida_unica_id in self.partidas_processadas:
                    print(f"⏭️ Partida já processada: {jogador1} vs {jogador2}")
                    continue
                
                # Verificar se este sinal específico já foi enviado
                if sinal_id in self.sinais_enviados:
                    print(f"⏭️ Sinal específico já enviado para {jogador1} vs {jogador2}")
                    continue
                
                # Buscar odds atuais
                event_id = oportunidade.get('partida_id')
                if event_id:
                    odds_data = self.buscar_odds_evento(event_id)
                else:
                    odds_data = {'jogador1_odd': 'N/A', 'jogador2_odd': 'N/A'}
                
                # NOVA ANÁLISE: Vantagem Mental (Estratégia Invertida) - ANTES da validação de odds
                analise_mental = self.analisar_vantagem_mental(oportunidade, odds_data)
                
                # NOVA ANÁLISE: Alavancagem (Estratégia de Alavancagem)
                analise_alavancagem = self.analisar_alavancagem(oportunidade, odds_data)
                
                # FILTRO CRÍTICO: Validar odds entre 1.8 e 2.2
                odds_valida, odd_valor = self.validar_filtros_odds(oportunidade, odds_data)
                if not odds_valida:
                    print(f"❌ Oportunidade rejeitada pelo filtro de odds: {jogador1}")
                    
                    # Coletar estatísticas reais para o dashboard
                    stats_reais = self.coletar_estatisticas_reais(event_id)
                    
                    # Calcular EV se não estiver disponível
                    ev_partida = oportunidade.get('ev', 0)
                    if ev_partida == 0:
                        # Calcular EV usando momentum e odds disponíveis
                        momentum = oportunidade.get('momentum', 0)
                        odd_valor_raw = odds_data.get('jogador1_odd', 0)
                        
                        # Verificar se a odd é válida (não é "-", "N/A", etc.)
                        try:
                            odd_valor = float(odd_valor_raw) if odd_valor_raw not in ['-', 'N/A', None, ''] else 0
                        except (ValueError, TypeError):
                            odd_valor = 0
                            
                        if momentum > 0 and odd_valor > 1:
                            try:
                                probabilidade = momentum / 100
                                ev_partida = (probabilidade * odd_valor) - 1
                                # Debug suprimido: print(f"🧮 EV calculado: MS={momentum}%, Odd={odd_valor} → EV={ev_partida:.3f}")
                            except:
                                ev_partida = 0
                                # Debug suprimido: print(f"⚠️ Erro no cálculo EV: MS={momentum}, Odd={odd_valor_raw}")
                        else:
                            # Debug suprimido: print(f"⚠️ EV não calculado: MS={momentum}, Odd={odd_valor_raw} (inválida)")
                            ev_partida = 0
                    
                    # Log partida rejeitada por odds
                    dashboard_logger.log_partida_analisada(
                        jogador1=jogador1,
                        jogador2=oportunidade.get('oponente', 'N/A'),
                        placar=oportunidade.get('placar', 'N/A'),
                        odds1=odds_data.get('jogador1_odd', 0),
                        odds2=odds_data.get('jogador2_odd', 0),
                        ev=ev_partida,
                        momentum_score=oportunidade.get('momentum', 0),
                        timing_priority=oportunidade.get('prioridade_timing', 0),
                        mental_score=analise_mental.get('score_mental', 0),
                        decisao='REJEITADO',
                        motivo='Odds fora do range 1.8-2.2',
                        stats_jogador1=stats_reais.get('stats_jogador1', {}),
                        stats_jogador2=stats_reais.get('stats_jogador2', {})
                    )
                    continue
                
                if analise_mental['inverter_aposta']:
                    # ESTRATÉGIA INVERTIDA: Apostar no adversário
                    sinal_invertido = self.preparar_sinal_invertido(analise_mental, oportunidade, odds_data)
                    if self.enviar_sinal_invertido(sinal_invertido):
                        self.sinais_enviados.add(sinal_id)
                        self.partidas_processadas.add(partida_unica_id)
                        contador_sinais += 1
                        print(f"🧠 Sinal INVERTIDO enviado: {analise_mental['target_final']}")
                        
                        # Log sinal invertido gerado
                        dashboard_logger.log_sinal_gerado(
                            tipo='INVERTIDO',
                            target=analise_mental['target_final'],
                            odd=analise_mental['odd_alvo'],
                            ev=analise_mental['ev_estimado'],
                            confianca=analise_mental['confianca'],
                            mental_score=analise_mental['score_mental'],
                            fatores_mentais=analise_mental['fatores_detectados']
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
                            ev=analise_mental['ev_estimado'],
                            momentum_score=oportunidade.get('momentum', 0),
                            timing_priority=oportunidade.get('prioridade_timing', 0),
                            mental_score=analise_mental['score_mental'],
                            decisao='SINAL_INVERTIDO',
                            motivo=f"Vantagem mental detectada: {analise_mental['score_mental']} pontos",
                            stats_jogador1=stats_reais.get('stats_jogador1', {}),
                            stats_jogador2=stats_reais.get('stats_jogador2', {})
                        )
                        continue
                
                # ESTRATÉGIA DE ALAVANCAGEM: Verificar se atende aos critérios
                if analise_alavancagem['alavancagem_aprovada']:
                    # Validar timing específico para alavancagem
                    timing_aprovado = self.validar_timing_inteligente(
                        oportunidade, 
                        'ALAVANCAGEM', 
                        momentum_score=analise_alavancagem.get('momentum_score', 0)
                    )
                    
                    if not timing_aprovado:
                        print(f"❌ Alavancagem rejeitada por timing inadequado")
                        continue
                    
                    # ESTRATÉGIA ALAVANCAGEM: Apostar no jogador da oportunidade
                    sinal_alavancagem = self.preparar_sinal_alavancagem(analise_alavancagem, oportunidade, odds_data)
                    if self.enviar_sinal_alavancagem(sinal_alavancagem):
                        self.sinais_enviados.add(sinal_id)
                        self.partidas_processadas.add(partida_unica_id)
                        contador_sinais += 1
                        print(f"🚀 Sinal ALAVANCAGEM enviado: {analise_alavancagem['jogador_alvo']}")
                        
                        # Log sinal alavancagem gerado
                        dashboard_logger.log_sinal_gerado(
                            tipo='ALAVANCAGEM',
                            target=analise_alavancagem['jogador_alvo'],
                            odd=analise_alavancagem['odd_alvo'],
                            ev=analise_alavancagem['ev_estimado'],
                            confianca=analise_alavancagem['confianca'],
                            mental_score=0,  # Alavancagem não usa score mental
                            fatores_mentais=f"Momentum: {analise_alavancagem['momentum_score']}%"
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
                            ev=analise_alavancagem['ev_estimado'],
                            momentum_score=analise_alavancagem['momentum_score'],
                            timing_priority=oportunidade.get('prioridade_timing', 0),
                            mental_score=0,
                            decisao='SINAL_ALAVANCAGEM',
                            motivo=f"Critérios de alavancagem atendidos: {analise_alavancagem['justificativa']}",
                            stats_jogador1=stats_reais.get('stats_jogador1', {}),
                            stats_jogador2=stats_reais.get('stats_jogador2', {})
                        )
                        continue
                
                # ESTRATÉGIA TRADICIONAL: Aplicar novos filtros rígidos
                if not self.aplicar_filtros_rigidos(oportunidade):
                    print(f"❌ Oportunidade rejeitada pelos filtros rígidos: {jogador1}")
                    
                    # Coletar estatísticas reais para o dashboard
                    stats_reais = self.coletar_estatisticas_reais(event_id)
                    
                    # Calcular EV se não estiver disponível
                    ev_partida = oportunidade.get('ev', 0)
                    if ev_partida == 0:
                        # Calcular EV usando momentum e odds disponíveis
                        momentum = oportunidade.get('momentum', 0)
                        odd_valor_raw = odds_data.get('jogador1_odd', 0)
                        
                        # Verificar se a odd é válida (não é "-", "N/A", etc.)
                        try:
                            odd_valor = float(odd_valor_raw) if odd_valor_raw not in ['-', 'N/A', None, ''] else 0
                        except (ValueError, TypeError):
                            odd_valor = 0
                            
                        if momentum > 0 and odd_valor > 1:
                            try:
                                probabilidade = momentum / 100
                                ev_partida = (probabilidade * odd_valor) - 1
                                # Debug suprimido: print(f"🧮 EV calculado (filtros rígidos): MS={momentum}%, Odd={odd_valor} → EV={ev_partida:.3f}")
                            except:
                                ev_partida = 0
                                # Debug suprimido: print(f"⚠️ Erro no cálculo EV (filtros rígidos): MS={momentum}, Odd={odd_valor_raw}")
                        else:
                            # Debug suprimido: print(f"⚠️ EV não calculado (filtros rígidos): MS={momentum}, Odd={odd_valor_raw} (inválida)")
                            ev_partida = 0
                    
                    # Log partida rejeitada por filtros rígidos
                    dashboard_logger.log_partida_analisada(
                        jogador1=jogador1,
                        jogador2=oportunidade.get('oponente', 'N/A'),
                        placar=oportunidade.get('placar', 'N/A'),
                        odds1=odds_data.get('jogador1_odd', 0),
                        odds2=odds_data.get('jogador2_odd', 0),
                        ev=ev_partida,
                        momentum_score=oportunidade.get('momentum', 0),
                        timing_priority=oportunidade.get('prioridade_timing', 0),
                        mental_score=analise_mental.get('score_mental', 0),
                        decisao='REJEITADO',
                        motivo='Não passou nos filtros rígidos (EV/MS/W1S)',
                        stats_jogador1=stats_reais.get('stats_jogador1', {}),
                        stats_jogador2=stats_reais.get('stats_jogador2', {})
                    )
                    continue
                
                # Coletar dados dos filtros para armazenamento
                dados_filtros = {
                    'timestamp_entrada': datetime.now().isoformat(),
                    'ev': oportunidade.get('ev', 0),
                    'momentum_score': oportunidade.get('momentum', 0),
                    'double_faults': oportunidade.get('double_faults', 0),
                    'win_1st_serve': oportunidade.get('win_1st_serve', 0),
                    'odd_final': odd_valor,
                    'filtros_aplicados': {
                        'timing_aprovado': oportunidade.get('prioridade_timing', 0) >= 3,
                        'ev_range': f"{oportunidade.get('ev', 0):.3f}",
                        'ms_range': f"{oportunidade.get('momentum', 0):.1f}%",
                        'df_range': oportunidade.get('double_faults', 0),
                        'w1s_range': f"{oportunidade.get('win_1st_serve', 0):.1f}%",
                        'odd_range': f"{odd_valor:.2f} (1.8-2.2)"
                    },
                    'fase_timing': oportunidade.get('fase_timing', 'N/A'),
                    'placar_momento': oportunidade.get('placar', 'N/A'),
                    'liga': oportunidade.get('liga', 'N/A')
                }
                
                # Gerar sinal no formato TennisIQ com dados dos filtros
                sinal = self.gerar_sinal_tennisiq(oportunidade, odds_data, dados_filtros)
                
                # Enviar sinal
                if self.enviar_telegram(sinal):
                    self.sinais_enviados.add(sinal_id)
                    self.partidas_processadas.add(partida_unica_id)  # Marcar partida como processada
                    contador_sinais += 1
                    print(f"🎯 Sinal TennisIQ enviado: {oportunidade['jogador']} vs {oportunidade['oponente']}")
                    print(f"🔒 Partida bloqueada para futuras duplicatas: {partida_unica_id}")
                    
                    # Calcular EV se não estiver disponível para log de sinal
                    ev_partida = oportunidade.get('ev', 0)
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
                                # Debug suprimido: print(f"🧮 EV calculado (sinal gerado): MS={momentum}%, Odd={odd_valor_calc} → EV={ev_partida:.3f}")
                            except:
                                ev_partida = 0
                                # Debug suprimido: print(f"⚠️ Erro no cálculo EV (sinal gerado): MS={momentum}, Odd={odd_valor_raw}")
                        else:
                            # Debug suprimido: print(f"⚠️ EV não calculado (sinal gerado): MS={momentum}, Odd={odd_valor_raw} (inválida)")
                            ev_partida = 0
                    
                    # Log sinal tradicional gerado
                    dashboard_logger.log_sinal_gerado(
                        tipo='TRADICIONAL',
                        target=oportunidade['jogador'],
                        odd=odd_valor,
                        ev=ev_partida,
                        confianca=70.0  # Confiança base para sinais tradicionais
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
                        mental_score=analise_mental.get('score_mental', 0),
                        decisao='SINAL_TRADICIONAL',
                        motivo='Aprovado por todos os filtros rígidos',
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
                
                # Pequena pausa entre sinais
                time.sleep(1)  # Reduzido de 2 para 1 segundo
                
            except Exception as e:
                print(f"⚠️ Erro ao processar oportunidade: {e}")
        
        if contador_sinais > 0:
            print(f"✅ {contador_sinais} sinal(is) TennisIQ enviado(s) com sucesso!")
        else:
            print("📭 Nenhum sinal novo para enviar neste ciclo")
    
    def analisar_vantagem_mental(self, oportunidade, odds_data):
        """
        Analisa se o adversário tem vantagem mental para inverter a aposta
        """
        try:
            # Preparar dados para o detector
            partida_data = {
                'favorito': {
                    'nome': oportunidade.get('jogador'),
                    'odd': self.extrair_odd_jogador(odds_data, oportunidade.get('jogador'))
                },
                'adversario': {
                    'nome': oportunidade.get('oponente'),
                    'odd': self.extrair_odd_oponente(odds_data, oportunidade.get('oponente'))
                },
                'score': oportunidade.get('placar', ''),
                'contexto': self.identificar_contexto_partida(oportunidade)
            }
            
            # Usar o detector de vantagem mental
            analise = self.detector_mental.analisar_partida(partida_data)
            
            # NOVO: Validar timing inteligente para estratégia invertida
            if analise.get('inverter_aposta'):
                timing_aprovado = self.validar_timing_inteligente(
                    oportunidade, 
                    'INVERTIDA', 
                    analise.get('score_mental', 0)
                )
                if not timing_aprovado:
                    print(f"❌ Aposta invertida rejeitada por timing")
                    analise['inverter_aposta'] = False
                    analise['motivo_rejeicao'] = 'Timing inadequado para estratégia invertida'
            
            return analise
            
        except Exception as e:
            print(f"⚠️ Erro na análise de vantagem mental: {e}")
            return {'inverter_aposta': False, 'erro': str(e)}
    
    def validar_timing_inteligente(self, oportunidade, estrategia_tipo, score_mental=0):
        """
        Validação de timing adaptada por tipo de estratégia
        """
        # Usar horário de Brasília (UTC-3)
        agora = datetime.now(timezone(timedelta(hours=-3)))
        hora_atual = agora.hour
        
        # ESTRATÉGIA ALAVANCAGEM: Timing otimizado para 2º set
        if estrategia_tipo == 'ALAVANCAGEM':
            contexto = self.identificar_contexto_partida(oportunidade)
            momentum_score = oportunidade.get('momentum', 0)
            
            # Alavancagem é mais eficaz no início/meio do 2º set
            # Timing muito flexível devido à especificidade da situação
            
            # Situação ideal: início/meio do 2º set (timing override)
            if '2º set' in contexto and momentum_score >= 65:
                print(f"🚀 Alavancagem 2º set: Momentum {momentum_score}% - Timing override")
                return True
            
            # 1º set quase terminando também é válido
            if '1º set' in contexto and momentum_score >= 70:
                print(f"🎾 Alavancagem 1º set final: Momentum {momentum_score}% aprovado")
                return True
            
            # Horário normal sempre liberado
            if 6 <= hora_atual <= 23:
                return True
            
            # Madrugada liberada se momentum alto (situação específica)
            if 0 <= hora_atual <= 6 and momentum_score >= 70:
                print(f"🌙 Alavancagem madrugada: Momentum {momentum_score}% suficiente")
                return True
            
            # Madrugada com momentum baixo
            print(f"❌ Alavancagem madrugada bloqueada: Momentum {momentum_score}% < 70%")
            return False

        # ESTRATÉGIA INVERTIDA: Timing mais flexível
        elif estrategia_tipo == 'INVERTIDA':
            contexto = self.identificar_contexto_partida(oportunidade)
            
            # Situações críticas ignoram timing
            if score_mental >= 300:  # Score muito alto
                print(f"⚡ Score mental {score_mental}: Timing override ativado")
                return True
                
            if '3º set' in contexto or 'tie-break' in contexto:
                print(f"🚨 Situação crítica: {contexto} - Timing override")
                return True
            
            # Madrugada liberada para invertidas com score alto
            if 0 <= hora_atual <= 6 and score_mental >= 250:
                print(f"🌙 Madrugada liberada: Score {score_mental} suficiente")
                return True
            
            # Horário normal mais flexível
            if 6 <= hora_atual <= 23:
                return True
                
            # Madrugada com score baixo
            print(f"❌ Madrugada bloqueada: Score {score_mental} < 250")
            return False
        
        # ESTRATÉGIA TRADICIONAL: Timing rígido
        elif estrategia_tipo == 'TRADICIONAL':
            prioridade = oportunidade.get('prioridade_timing', 0)
            
            # Exigir prioridade 3+ sempre
            if prioridade < 3:
                print(f"❌ Timing tradicional: Prioridade {prioridade} < 3")
                return False
            
            # Bloquear madrugada sempre
            if 0 <= hora_atual <= 6:
                print(f"❌ Timing tradicional: Madrugada bloqueada")
                return False
            
            # Horário comercial preferido
            if 8 <= hora_atual <= 22:
                return True
            
            # Horário marginal
            print(f"⚠️ Timing tradicional: Horário marginal {hora_atual}h")
            return prioridade >= 3  # Prioridade mínima 3
        
        return False
    
    def extrair_odd_jogador(self, odds_data, jogador):
        """Extrai a odd do jogador principal"""
        if isinstance(odds_data, dict):
            return odds_data.get('jogador1_odd', 1.8)
        return 1.8
    
    def extrair_odd_oponente(self, odds_data, oponente):
        """Extrai a odd do oponente"""
        if isinstance(odds_data, dict):
            return odds_data.get('jogador2_odd', 2.1)
        return 2.1
    
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
    
    def analisar_alavancagem(self, oportunidade, odds_data):
        """
        Analisa se a oportunidade atende aos critérios de alavancagem
        """
        try:
            # Obter placar da partida
            placar = oportunidade.get('placar', '')
            
            # Usar o detector de alavancagem
            analise = self.detector_alavancagem.analisar_oportunidade_alavancagem(
                oportunidade, placar, odds_data
            )
            
            return analise
            
        except Exception as e:
            print(f"⚠️ Erro na análise de alavancagem: {e}")
            return {'alavancagem_aprovada': False, 'erro': str(e)}
    
    def preparar_sinal_invertido(self, analise_mental, oportunidade, odds_data):
        """Prepara sinal para aposta invertida"""
        return {
            'tipo': 'INVERTIDA',
            'jogador_alvo': analise_mental['target_final'],
            'odd_alvo': analise_mental['odd_alvo'],
            'ev_estimado': analise_mental['ev_estimado'],
            'score_mental': analise_mental['score_mental'],
            'fatores_mentais': analise_mental['fatores_detectados'],
            'confianca': analise_mental['confianca'],
            'justificativa': analise_mental['justificativa'],
            'partida_original': f"{oportunidade.get('jogador')} vs {oportunidade.get('oponente')}",
            'prioridade': 5,
            'estrategia': 'VANTAGEM_MENTAL',
            'timestamp': datetime.now().isoformat()
        }
    
    def enviar_sinal_invertido(self, sinal):
        """Envia sinal de aposta invertida no formato padrão TennisIQ"""
        try:
            # Extrair dados básicos
            jogador_alvo = sinal['jogador_alvo']
            odd_alvo = sinal['odd_alvo']
            partida_original = sinal['partida_original']
            
            # Determinar oponente (extrair do formato "Jogador vs Oponente")
            if ' vs ' in partida_original:
                jogadores = partida_original.split(' vs ')
                # O oponente é quem não é o jogador alvo
                oponente = jogadores[1] if jogadores[0] == jogador_alvo else jogadores[0]
            else:
                oponente = "Oponente"
            
            # Calcular odd mínima
            odd_minima = self.calcular_odd_minima(odd_alvo)
            
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
    
    def preparar_sinal_alavancagem(self, analise_alavancagem, oportunidade, odds_data):
        """Prepara sinal para aposta de alavancagem"""
        return {
            'tipo': 'ALAVANCAGEM',
            'jogador_alvo': analise_alavancagem['jogador_alvo'],
            'odd_alvo': analise_alavancagem['odd_alvo'],
            'ev_estimado': analise_alavancagem['ev_estimado'],
            'momentum_score': analise_alavancagem['momentum_score'],
            'confianca': analise_alavancagem['confianca'],
            'justificativa': analise_alavancagem['justificativa'],
            'partida_original': f"{oportunidade.get('jogador')} vs {oportunidade.get('oponente')}",
            'prioridade': 5,
            'estrategia': 'ALAVANCAGEM',
            'timestamp': datetime.now().isoformat()
        }
    
    def enviar_sinal_alavancagem(self, sinal):
        """Envia sinal de aposta de alavancagem no formato padrão TennisIQ"""
        try:
            # Extrair dados básicos
            jogador_alvo = sinal['jogador_alvo']
            odd_alvo = sinal['odd_alvo']
            partida_original = sinal['partida_original']
            
            # Determinar oponente (extrair do formato "Jogador vs Oponente")
            if ' vs ' in partida_original:
                jogadores = partida_original.split(' vs ')
                # O oponente é quem não é o jogador alvo
                oponente = jogadores[1] if jogadores[0] == jogador_alvo else jogadores[0]
            else:
                oponente = "Oponente"
            
            # Calcular odd mínima
            odd_minima = self.calcular_odd_minima(odd_alvo)
            
            # Usar horário de Brasília (UTC-3)
            agora = datetime.now(timezone(timedelta(hours=-3)))
            horario = agora.strftime("%H:%M")
            
            # Gerar link direto da Bet365 (se disponível)
            event_id = sinal.get('event_id', '')
            bet365_link = bet365_manager.generate_link(event_id) if event_id else "Link não disponível"
            
            # Montar sinal no formato padrão TennisIQ
            mensagem = f"""🎾 TennisIQ - Sinal - Alavancagem 🚀

{oponente} vs {jogador_alvo}
⏰ {horario}

🚀 APOSTAR EM: {jogador_alvo} 🚀
💰 Odd: {odd_alvo}
⚠️ Limite Mínimo: {odd_minima} (não apostar abaixo)

🔗 Link direto: https://www.bet365.bet.br/?_h=LKUUnzn5idsD_NCCi9iyvQ%3D%3D&btsffd=1#/IP/EV10459378C13

#TennisIQ"""
            
            # Salvar log da aposta de alavancagem
            self.log_aposta_alavancagem(sinal)
            
            # Enviar via Telegram
            return self.enviar_telegram(mensagem)
            
        except Exception as e:
            print(f"❌ Erro ao enviar sinal alavancagem: {e}")
            return False
    
    def log_aposta_alavancagem(self, sinal):
        """Log específico para apostas de alavancagem"""
        try:
            log_entry = {
                'timestamp': sinal['timestamp'],
                'tipo': 'APOSTA_ALAVANCAGEM',
                'partida_original': sinal['partida_original'],
                'jogador_alvo': sinal['jogador_alvo'],
                'odd_alvo': sinal['odd_alvo'],
                'momentum_score': sinal['momentum_score'],
                'ev_estimado': sinal['ev_estimado'],
                'confianca': sinal['confianca'],
                'justificativa': sinal['justificativa']
            }
            
            self.apostas_alavancagem.append(log_entry)
            
            # Salvar em arquivo separado
            with open('apostas_alavancagem.json', 'w', encoding='utf-8') as f:
                json.dump(self.apostas_alavancagem, f, ensure_ascii=False, indent=2)
            
            print(f"📝 Log da aposta de alavancagem salvo: {sinal['jogador_alvo']}")
            
        except Exception as e:
            print(f"⚠️ Erro ao salvar log da aposta de alavancagem: {e}")
    
    def aplicar_filtros_rigidos(self, oportunidade):
        """
        Aplica filtros rigorosos de produção - SINCRONIZADO COM SELEÇÃO_FINAL
        """
        try:
            # EV mínimo ajustado para 0.15 (sincronizado)
            ev = oportunidade.get('ev', 0)
            if ev < 0.15:
                print(f"❌ Filtro EV: {ev:.3f} < 0.15 (mínimo)")
                return False
            
            # Momentum Score mínimo mantido em 65%
            momentum = oportunidade.get('momentum', 0)
            if momentum < 65:
                print(f"❌ Filtro MS: {momentum:.1f}% < 65% (mínimo)")
                return False
            
            # Win 1st Serve mínimo ajustado para 65% (sincronizado)
            win_1st = oportunidade.get('win_1st_serve', 0)
            if win_1st < 65:
                print(f"❌ Filtro W1S: {win_1st:.1f}% < 65% (mínimo)")
                return False
            
            # Double Faults máximo ajustado para 4 (sincronizado)
            double_faults = oportunidade.get('double_faults', 0)
            if double_faults > 4:
                print(f"❌ Filtro DF: {double_faults} > 4 (máximo)")
                return False
            
            # NOVO: Validação de timing inteligente para tradicional
            timing_aprovado = self.validar_timing_inteligente(oportunidade, 'TRADICIONAL')
            if not timing_aprovado:
                print(f"❌ Filtro Timing: Horário inadequado para estratégia tradicional")
                return False
            
            # BLOQUEIOS CONTEXTUAIS
            contexto = self.identificar_contexto_partida(oportunidade)
            
            if '3º set' in contexto:
                print(f"❌ Bloqueio Contextual: 3º set detectado")
                return False
            
            if 'pós tie-break' in contexto:
                print(f"❌ Bloqueio Contextual: pós tie-break detectado")
                return False
            
            if 'sets empatados' in contexto:
                print(f"❌ Bloqueio Contextual: sets empatados detectado")
                return False
            
            print(f"✅ Todos os filtros rígidos aprovados para {oportunidade.get('jogador')}")
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
        print("🎾 TennisIQ Bot - Iniciando Monitoramento 24h...")
        print("=" * 60)
        
        # Configurar verbosidade do logger (MINIMAL, NORMAL, DEBUG)
        logger_formatado.set_verbosidade("NORMAL")  # Mude para MINIMAL se quiser menos info
        
        # Enviar notificação de ativação
        self.notificar_ativacao()
        
        print("🤖 Bot ativo - Monitorando oportunidades 24/7")
        print("💡 Pressione Ctrl+C para parar o bot")
        print("🔄 Verificações a cada 45 segundos")  # Acelerado de 1 minuto para 45s
        print("⚠️ Rate limiting: 3.600 requests/hora (60/minuto)")
        print("📊 Estratégia: Análise otimizada para economizar API")
        print("=" * 60)
        
        contador_ciclos = 0
        contador_oportunidades_total = 0
        
        while self.running:
            try:
                contador_ciclos += 1
                agora = datetime.now()
                agora_str = agora.strftime("%H:%M:%S")
                data_str = agora.strftime("%d/%m/%Y")
                
                # Limpar cache antigo a cada ciclo
                self.limpar_cache_antigo()
                
                # Resetar contador de requests a cada hora
                if agora.hour != self.hora_atual:
                    logger_formatado.log_aviso(f"Nova hora detectada - Resetando contador API (anterior: {self.requests_contador})")
                    self.requests_contador = 0
                    self.hora_atual = agora.hour
                
                # === INÍCIO DO CICLO COM LOGGER FORMATADO ===
                logger_formatado.log_inicio_ciclo(contador_ciclos)
                
                # Atualizar status do bot no dashboard
                dashboard_logger.atualizar_status_bot(
                    ativo=True,
                    requests_restantes=3600 - self.requests_contador,
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
                    
                    # Converter oportunidades para formato do logger
                    oportunidades_formatadas = []
                    for op in oportunidades:
                        oportunidades_formatadas.append({
                            'jogador': op.get('jogador', 'N/A'),
                            'odd': op.get('odd', 0),
                            'estrategia': op.get('estrategia', 'RIGOROSA'),
                            'confianca': op.get('confianca', 85)
                        })
                    
                    logger_formatado.log_oportunidades_encontradas(oportunidades_formatadas)
                    self.notificar_oportunidade(oportunidades)
                else:
                    logger_formatado.log_oportunidades_encontradas([])
                
                # Verificar resultados das apostas a cada 2 ciclos (~1.5 minutos) - AUTOMÁTICO E RÁPIDO
                if contador_ciclos % 2 == 0:  # Mudado de 3 para 2 ciclos
                    logger_formatado.log_debug("Verificando resultados automaticamente (somente por ID)...")
                    self.verificar_resultados_automatico()
                
                # Verificar se é hora de enviar relatórios (a cada ciclo)
                self.verificar_horario_relatorios()
                
                # === RESUMO DO CICLO ===
                stats_ciclo = {
                    'partidas_analisadas': total_partidas_real,
                    'timing_aprovadas': aprovadas_timing_real,
                    'taxa_timing': (aprovadas_timing_real / total_partidas_real * 100) if total_partidas_real > 0 else 0,
                    'oportunidades_encontradas': len(oportunidades) if oportunidades else 0,
                    'taxa_conversao': (len(oportunidades) / aprovadas_timing_real * 100) if aprovadas_timing_real > 0 else 0,
                    'requests_usados': requests_usados,
                    'proximo_ciclo': 45,
                    'sistema_ativo': True
                }
                
                logger_formatado.log_resumo_ciclo(stats_ciclo)
                
                # Rate limiting inteligente baseado no limite real - OTIMIZADO
                requests_por_hora = self.requests_contador * (3600 / ((contador_ciclos * 5 * 60) if contador_ciclos > 0 else 1))
                
                if requests_por_hora > 3000:  # 83% do limite
                    logger_formatado.log_aviso("CRÍTICO: Muito próximo do limite da API!")
                    tempo_espera = 90  # Reduzido de 120 para 90 segundos
                elif requests_por_hora > 2500:  # 69% do limite
                    logger_formatado.log_aviso("ATENÇÃO: Aproximando do limite da API")
                    tempo_espera = 60  # Reduzido de 90 para 60 segundos
                elif requests_por_hora > 2000:  # 56% do limite
                    logger_formatado.log_debug("MODERADO: Monitorando uso da API")
                    tempo_espera = 50  # Reduzido de 75 para 50 segundos
                else:
                    tempo_espera = 45  # Reduzido de 60 para 45 segundos - MAIS RÁPIDO!
                
                logger_formatado.log_debug(f"Próxima verificação em {tempo_espera}s...")
                
                for i in range(tempo_espera):
                    if not self.running:
                        break
                    time.sleep(1)
                
            except KeyboardInterrupt:
                # Ctrl+C já é tratado pelo signal_handler
                break
            except Exception as e:
                logger_formatado.log_erro(f"Erro durante monitoramento: {e}")
                logger_formatado.log_aviso("Tentando novamente em 15 segundos...")
                time.sleep(15)  # Reduzido de 30 para 15 segundos para recuperação mais rápida

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
