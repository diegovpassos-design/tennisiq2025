#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LOGGER DE PRODUÇÃO ULTRA-OTIMIZADO - TennisIQ Bot
=================================================
Versão extremamente agressiva para eliminar totalmente o rate limiting
"""

import os
import time
from datetime import datetime, timezone, timedelta
from collections import defaultdict, deque

class LoggerProducaoUltra:
    """Logger ultra-otimizado para Railway com supressão máxima"""
    
    def __init__(self):
        self.ambiente = self._detectar_ambiente()
        self.ativo = self.ambiente == "railway"
        
        if not self.ativo:
            print("🔧 Logger Ultra em modo LOCAL - Logging normal")
            return
        
        # CONFIGURAÇÕES ULTRA-RESTRITIVAS para Railway
        self.max_logs_por_minuto = 10  # EXTREMAMENTE baixo
        self.max_logs_por_ciclo = 3    # Máximo 3 logs por ciclo
        self.logs_enviados_minuto = deque(maxlen=10)
        self.logs_ciclo_atual = 0
        
        # Buffer ultra-conservador
        self.buffer_importante = []
        self.max_buffer = 3
        
        # Supressão máxima
        self.logs_suprimidos_total = 0
        self.ultimo_resumo = time.time()
        self.intervalo_resumo = 60  # Resumo a cada minuto
        
        # Apenas logs CRÍTICOS passam
        self.tipos_permitidos = {
            'sinal_enviado', 'error', 'critical', 'alavancagem_aprovada',
            'strategy_success', 'telegram_sent', 'oportunidade_encontrada'
        }
        
        # Filtro de conteúdo ultra-agressivo
        self.palavras_bloqueadas = {
            'stats', 'odds', 'coletado', 'calculado', 'analisando',
            'salvando', 'dashboard', 'ev_', 'ms_', 'verificando',
            'carregando', 'processando', 'gerando', 'atualizando',
            'inicializando', 'configurando', 'preparando'
        }
        
        print("🚨 Logger Ultra ativado - SUPRESSÃO MÁXIMA para Railway")
    
    def _detectar_ambiente(self):
        """Detecta se está rodando no Railway"""
        return "railway" if os.environ.get("RAILWAY_ENVIRONMENT") else "local"
    
    def _eh_log_critico(self, mensagem):
        """Verifica se o log é realmente crítico"""
        mensagem_lower = mensagem.lower()
        
        # Logs críticos que SEMPRE passam
        if any(palavra in mensagem_lower for palavra in [
            'sinal enviado', 'telegram', 'error', 'critical', 'falha',
            'alavancagem aprovada', '🎯 sinal', '📨', '❌ erro'
        ]):
            return True
        
        # Bloquear logs com palavras proibidas
        if any(palavra in mensagem_lower for palavra in self.palavras_bloqueadas):
            return False
        
        # Logs de estratégias importantes
        if any(palavra in mensagem_lower for palavra in [
            '🚀 alavancagem:', '✅ aprovado', 'oportunidade encontrada'
        ]):
            return True
        
        return False
    
    def _pode_enviar_log(self):
        """Verifica se pode enviar mais logs"""
        if not self.ativo:
            return True
        
        agora = time.time()
        
        # Limpar logs antigos (> 1 minuto)
        while self.logs_enviados_minuto and (agora - self.logs_enviados_minuto[0]) > 60:
            self.logs_enviados_minuto.popleft()
        
        # Verificar limites
        if len(self.logs_enviados_minuto) >= self.max_logs_por_minuto:
            return False
        
        if self.logs_ciclo_atual >= self.max_logs_por_ciclo:
            return False
        
        return True
    
    def log(self, nivel, mensagem):
        """Log principal com supressão ultra-agressiva"""
        if not self.ativo:
            print(f"[{nivel}] {mensagem}")
            return
        
        # Filtro 1: Só logs críticos
        if not self._eh_log_critico(mensagem):
            self.logs_suprimidos_total += 1
            return
        
        # Filtro 2: Rate limiting
        if not self._pode_enviar_log():
            self.logs_suprimidos_total += 1
            self._adicionar_buffer(mensagem)
            return
        
        # Log aprovado
        timestamp = datetime.now(timezone.utc).strftime("%H:%M")
        log_formatado = f"[{timestamp}] {mensagem}"
        
        print(log_formatado)
        
        # Registrar envio
        self.logs_enviados_minuto.append(time.time())
        self.logs_ciclo_atual += 1
        
        # Enviar resumo se necessário
        self._verificar_resumo()
    
    def _adicionar_buffer(self, mensagem):
        """Adiciona mensagem ao buffer de emergência"""
        if len(self.buffer_importante) < self.max_buffer:
            self.buffer_importante.append(mensagem)
    
    def _verificar_resumo(self):
        """Envia resumo de logs suprimidos periodicamente"""
        agora = time.time()
        
        if (agora - self.ultimo_resumo) > self.intervalo_resumo and self.logs_suprimidos_total > 0:
            print(f"📊 {self.logs_suprimidos_total} logs suprimidos no último minuto")
            
            # Enviar logs importantes do buffer
            if self.buffer_importante:
                print(f"📋 Buffer: {len(self.buffer_importante)} logs importantes pendentes")
                self.buffer_importante.clear()
            
            self.logs_suprimidos_total = 0
            self.ultimo_resumo = agora
    
    def novo_ciclo(self):
        """Reset para novo ciclo de análise"""
        if self.ativo:
            self.logs_ciclo_atual = 0
            self._verificar_resumo()
    
    def info(self, mensagem):
        """Log de informação"""
        self.log("INFO", mensagem)
    
    def warning(self, mensagem):
        """Log de aviso"""
        self.log("WARNING", mensagem)
    
    def error(self, mensagem):
        """Log de erro - sempre passa"""
        if self.ativo:
            print(f"❌ ERROR: {mensagem}")
        else:
            print(f"[ERROR] {mensagem}")
    
    def success(self, mensagem):
        """Log de sucesso - sempre passa"""
        if self.ativo:
            print(f"✅ SUCCESS: {mensagem}")
        else:
            print(f"[SUCCESS] {mensagem}")
    
    def strategy_log(self, estrategia, resultado, mensagem):
        """Log específico de estratégias"""
        if estrategia.lower() == "alavancagem" or resultado == "aprovado":
            emoji = "🚀" if estrategia.lower() == "alavancagem" else "🎯"
            self.log("STRATEGY", f"{emoji} {estrategia.upper()}: {mensagem}")

# Instância global ultra-otimizada
logger_ultra = LoggerProducaoUltra()

# Função de compatibilidade
def log_info(mensagem):
    """Função de compatibilidade para logs de info"""
    logger_ultra.info(mensagem)

def log_strategy(estrategia, resultado, mensagem):
    """Função de compatibilidade para logs de estratégia"""
    logger_ultra.strategy_log(estrategia, resultado, mensagem)
