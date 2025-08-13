#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LOGGER PRODUÇÃO - TennisIQ Bot
=============================
Sistema de logging otimizado para produção com controle de verbosidade
"""

import os
import time
from datetime import datetime, timezone, timedelta
from collections import defaultdict

class LoggerProducao:
    """Logger otimizado para produção com controle rigoroso de rate"""
    
    def __init__(self):
        # Detectar ambiente
        self.ambiente = os.getenv('RAILWAY_ENVIRONMENT', 'local').lower()
        self.is_production = self.ambiente in ['production', 'railway']
        
        # Configurar verbosidade baseada no ambiente
        if self.is_production:
            self.nivel = 'MINIMAL'
        else:
            self.nivel = 'NORMAL'
        
        # Controle de rate de logs
        self.log_buffer = []
        self.last_flush = time.time()
        self.flush_interval = 5  # Flush a cada 5 segundos
        self.max_logs_per_flush = 10  # Máximo de 10 logs por flush
        
        # Agrupamento de logs similares
        self.log_counts = defaultdict(int)
        self.suppressed_logs = 0
        
        # Estatísticas
        self.total_logs = 0
        self.logs_suppressed = 0
        
        print(f"🔧 Logger Produção ativado - Ambiente: {self.ambiente} - Nível: {self.nivel}")
    
    def get_timestamp(self):
        """Timestamp otimizado"""
        if self.is_production:
            return datetime.now(timezone.utc).strftime("%H:%M")
        else:
            return datetime.now(timezone(timedelta(hours=-3))).strftime("%H:%M:%S")
    
    def should_log(self, categoria, mensagem):
        """Determina se deve fazer log baseado em rate limiting"""
        # Sempre logar erros críticos
        if categoria in ['ERROR', 'CRITICAL', 'SINAL_VERDE']:
            return True
        
        # Em produção, ser muito seletivo
        if self.is_production:
            # Só logar eventos importantes
            if categoria in ['CICLO', 'OPORTUNIDADE', 'RESUMO', 'STATS']:
                return True
            
            # Rate limit para outros logs
            key = f"{categoria}:{mensagem[:50]}"
            self.log_counts[key] += 1
            
            # Primeira vez ou a cada 10 ocorrências
            if self.log_counts[key] == 1 or self.log_counts[key] % 10 == 0:
                return True
            
            self.logs_suppressed += 1
            return False
        
        return True
    
    def add_to_buffer(self, mensagem):
        """Adiciona mensagem ao buffer"""
        self.log_buffer.append({
            'timestamp': time.time(),
            'mensagem': mensagem
        })
        self.total_logs += 1
        
        # Flush se buffer estiver cheio ou muito tempo passou
        now = time.time()
        if (len(self.log_buffer) >= self.max_logs_per_flush or 
            (now - self.last_flush) >= self.flush_interval):
            self.flush_buffer()
    
    def flush_buffer(self):
        """Flush do buffer de logs"""
        if not self.log_buffer:
            return
        
        # Imprimir logs em batch
        for log_item in self.log_buffer:
            print(log_item['mensagem'])
        
        # Mostrar estatísticas de supressão se houver
        if self.logs_suppressed > 0:
            print(f"📊 {self.logs_suppressed} logs similares suprimidos")
            self.logs_suppressed = 0
        
        # Limpar buffer
        self.log_buffer.clear()
        self.last_flush = time.time()
    
    def log(self, categoria, mensagem, force=False):
        """Log principal com controle de rate"""
        if not force and not self.should_log(categoria, mensagem):
            return
        
        timestamp = self.get_timestamp()
        log_msg = f"[{timestamp}] {mensagem}"
        
        if self.is_production:
            # Em produção, usar buffer
            self.add_to_buffer(log_msg)
        else:
            # Em desenvolvimento, log direto
            print(log_msg)
    
    def error(self, mensagem, detalhes=None):
        """Log de erro - sempre mostrado"""
        msg = f"🚨 ERRO: {mensagem}"
        if detalhes and not self.is_production:
            msg += f" | {detalhes}"
        self.log('ERROR', msg, force=True)
    
    def warning(self, mensagem):
        """Log de aviso"""
        self.log('WARNING', f"⚠️ {mensagem}")
    
    def info(self, mensagem):
        """Log de informação"""
        self.log('INFO', f"ℹ️ {mensagem}")
    
    def success(self, mensagem):
        """Log de sucesso"""
        self.log('SUCCESS', f"✅ {mensagem}", force=True)
    
    def ciclo_inicio(self, numero):
        """Log de início de ciclo"""
        msg = f"🔄 CICLO {numero} - {self.get_timestamp()}"
        self.log('CICLO', msg, force=True)
    
    def oportunidade_encontrada(self, jogadores, ev_valor):
        """Log de oportunidade - sempre mostrar"""
        msg = f"🎯 OPORTUNIDADE: {jogadores} (EV: {ev_valor})"
        self.log('OPORTUNIDADE', msg, force=True)
    
    def stats_ciclo(self, partidas, aprovadas, oportunidades, requests):
        """Log de estatísticas do ciclo"""
        msg = f"📊 {partidas} partidas | {aprovadas} timing OK | {oportunidades} oportunidades | {requests} requests"
        self.log('STATS', msg, force=True)
    
    def rate_limit_429(self, url):
        """Log de rate limit da API"""
        msg = f"🚨 Rate Limit API: {url.split('/')[-1] if '/' in url else url}"
        self.log('ERROR', msg, force=True)
    
    def finalizar(self):
        """Finaliza o logger e flush final"""
        self.flush_buffer()
        if self.total_logs > 0:
            print(f"📊 Logger Stats: {self.total_logs} logs totais, {self.suppressed_logs} suprimidos")

# Instância global
logger_prod = LoggerProducao()
