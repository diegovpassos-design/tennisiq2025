#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 RATE LIMITER AVANÇADO
============================================================
Rate limiter com controle de rajadas e múltiplas instâncias
"""

import time
import asyncio
from collections import deque
from datetime import datetime, timedelta

class RateLimiterAvancado:
    def __init__(self, 
                 max_requests_per_hour=3600,
                 max_requests_per_minute=80, 
                 max_requests_per_second=5,
                 burst_delay=0.2):
        """
        Rate limiter com controle de rajadas
        
        Args:
            max_requests_per_hour: Limite por hora
            max_requests_per_minute: Limite por minuto 
            max_requests_per_second: Limite por segundo
            burst_delay: Delay entre requisições em rajadas (segundos)
        """
        self.max_requests_per_hour = max_requests_per_hour
        self.max_requests_per_minute = max_requests_per_minute
        self.max_requests_per_second = max_requests_per_second
        self.burst_delay = burst_delay
        
        # Tracking de requests
        self.requests_hour = deque()
        self.requests_minute = deque()
        self.requests_second = deque()
        
        self.last_request_time = 0
        
    def can_make_request(self):
        """Verifica se pode fazer uma requisição"""
        now = time.time()
        
        # Limpar requests antigos
        self._clean_old_requests(now)
        
        # Verificar limites
        if len(self.requests_hour) >= self.max_requests_per_hour:
            return False, f"Limite por hora excedido: {len(self.requests_hour)}/{self.max_requests_per_hour}"
            
        if len(self.requests_minute) >= self.max_requests_per_minute:
            return False, f"Limite por minuto excedido: {len(self.requests_minute)}/{self.max_requests_per_minute}"
            
        if len(self.requests_second) >= self.max_requests_per_second:
            return False, f"Limite por segundo excedido: {len(self.requests_second)}/{self.max_requests_per_second}"
        
        # Verificar delay entre requests
        time_since_last = now - self.last_request_time
        if time_since_last < self.burst_delay:
            return False, f"Delay necessário: {self.burst_delay - time_since_last:.2f}s"
        
        return True, "OK"
    
    def make_request(self):
        """Registra uma requisição feita"""
        now = time.time()
        
        self.requests_hour.append(now)
        self.requests_minute.append(now)
        self.requests_second.append(now)
        self.last_request_time = now
        
        # Log de monitoramento
        self._log_request_stats()
    
    def wait_if_needed(self):
        """Espera se necessário antes de fazer request"""
        can_request, reason = self.can_make_request()
        
        if not can_request:
            if "Delay necessário" in reason:
                delay = float(reason.split(": ")[1].replace("s", ""))
                print(f"⏳ Aguardando {delay:.2f}s para evitar rate limit...")
                time.sleep(delay)
            else:
                print(f"🚨 Rate limit ativo: {reason}")
                return False
        
        return True
    
    async def async_wait_if_needed(self):
        """Versão async de wait_if_needed"""
        can_request, reason = self.can_make_request()
        
        if not can_request:
            if "Delay necessário" in reason:
                delay = float(reason.split(": ")[1].replace("s", ""))
                print(f"⏳ Aguardando {delay:.2f}s para evitar rate limit...")
                await asyncio.sleep(delay)
            else:
                print(f"🚨 Rate limit ativo: {reason}")
                return False
        
        return True
    
    def _clean_old_requests(self, now):
        """Remove requests antigos dos contadores"""
        # Hora (3600s)
        while self.requests_hour and now - self.requests_hour[0] > 3600:
            self.requests_hour.popleft()
            
        # Minuto (60s)
        while self.requests_minute and now - self.requests_minute[0] > 60:
            self.requests_minute.popleft()
            
        # Segundo (1s)
        while self.requests_second and now - self.requests_second[0] > 1:
            self.requests_second.popleft()
    
    def _log_request_stats(self):
        """Log das estatísticas de requests"""
        print(f"📊 Rate Stats: {len(self.requests_hour)}/3600h | "
              f"{len(self.requests_minute)}/80min | "
              f"{len(self.requests_second)}/5s")
    
    def get_stats(self):
        """Retorna estatísticas atuais"""
        now = time.time()
        self._clean_old_requests(now)
        
        return {
            'requests_hour': len(self.requests_hour),
            'requests_minute': len(self.requests_minute),
            'requests_second': len(self.requests_second),
            'limits': {
                'hour': self.max_requests_per_hour,
                'minute': self.max_requests_per_minute,
                'second': self.max_requests_per_second
            }
        }

# Instância global
rate_limiter = RateLimiterAvancado()
