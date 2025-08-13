#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RATE LIMITER - TennisIQ Bot
===========================
Sistema de controle de rate limiting para APIs
"""

import time
from datetime import datetime, timedelta
from collections import deque

class RateLimiter:
    """Controla rate limiting para requisições de API"""
    
    def __init__(self, max_requests_per_minute=30, max_requests_per_hour=1800):
        self.max_per_minute = max_requests_per_minute
        self.max_per_hour = max_requests_per_hour
        
        # Filas para controlar requisições
        self.requests_minute = deque()
        self.requests_hour = deque()
        
        # Controle de 429 errors
        self.last_429_time = None
        self.backoff_time = 60  # Segundos para wait após 429
        
        # Estatísticas
        self.total_requests = 0
        self.total_429_errors = 0
        self.total_waits = 0
    
    def can_make_request(self):
        """Verifica se pode fazer uma requisição"""
        now = time.time()
        
        # Verificar se estamos em backoff por 429
        if self.last_429_time and (now - self.last_429_time) < self.backoff_time:
            return False
        
        # Limpar requisições antigas (> 1 minuto)
        while self.requests_minute and (now - self.requests_minute[0]) > 60:
            self.requests_minute.popleft()
        
        # Limpar requisições antigas (> 1 hora)
        while self.requests_hour and (now - self.requests_hour[0]) > 3600:
            self.requests_hour.popleft()
        
        # Verificar limites
        if len(self.requests_minute) >= self.max_per_minute:
            return False
        
        if len(self.requests_hour) >= self.max_per_hour:
            return False
        
        return True
    
    def register_request(self):
        """Registra uma requisição feita"""
        now = time.time()
        self.requests_minute.append(now)
        self.requests_hour.append(now)
        self.total_requests += 1
    
    def register_429_error(self):
        """Registra um erro 429 (Too Many Requests)"""
        self.last_429_time = time.time()
        self.total_429_errors += 1
        print(f"🚨 API Rate Limit atingido! Aguardando {self.backoff_time}s...")
    
    def wait_if_needed(self):
        """Aguarda se necessário para respeitar rate limits"""
        if not self.can_make_request():
            # Calcular tempo de espera
            now = time.time()
            
            # Se estamos em backoff por 429
            if self.last_429_time and (now - self.last_429_time) < self.backoff_time:
                wait_time = self.backoff_time - (now - self.last_429_time)
                print(f"⏳ Aguardando {wait_time:.0f}s por rate limit 429...")
                time.sleep(wait_time)
                self.total_waits += 1
                return
            
            # Rate limit por minuto
            if self.requests_minute and len(self.requests_minute) >= self.max_per_minute:
                oldest = self.requests_minute[0]
                wait_time = 60 - (now - oldest) + 1  # +1 para margem
                if wait_time > 0:
                    print(f"⏳ Aguardando {wait_time:.0f}s por rate limit (minuto)...")
                    time.sleep(wait_time)
                    self.total_waits += 1
                    return
            
            # Rate limit por hora
            if self.requests_hour and len(self.requests_hour) >= self.max_per_hour:
                oldest = self.requests_hour[0]
                wait_time = 3600 - (now - oldest) + 1
                if wait_time > 0:
                    print(f"⏳ Aguardando {wait_time:.0f}s por rate limit (hora)...")
                    time.sleep(wait_time)
                    self.total_waits += 1
    
    def get_stats(self):
        """Retorna estatísticas do rate limiter"""
        now = time.time()
        
        # Limpar filas antigas
        while self.requests_minute and (now - self.requests_minute[0]) > 60:
            self.requests_minute.popleft()
        while self.requests_hour and (now - self.requests_hour[0]) > 3600:
            self.requests_hour.popleft()
        
        return {
            'requests_last_minute': len(self.requests_minute),
            'requests_last_hour': len(self.requests_hour),
            'total_requests': self.total_requests,
            'total_429_errors': self.total_429_errors,
            'total_waits': self.total_waits,
            'max_per_minute': self.max_per_minute,
            'max_per_hour': self.max_per_hour,
            'in_backoff': bool(self.last_429_time and (now - self.last_429_time) < self.backoff_time)
        }

# Instância global
api_rate_limiter = RateLimiter()
