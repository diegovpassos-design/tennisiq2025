#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LOGGER ESTRATÉGIAS RESUMIDO - TennisIQ Bot
==========================================
Versão intermediária que mantém visibilidade das estratégias sem rate limiting
"""

import os
import time
from datetime import datetime, timezone
from collections import defaultdict, deque

class LoggerEstrategias:
    """Logger para estratégias com resumos inteligentes"""
    
    def __init__(self):
        self.ambiente = self._detectar_ambiente()
        self.ativo = self.ambiente == "railway"
        
        if not self.ativo:
            print("🔧 Logger Estratégias em modo LOCAL - Logging normal")
            return
        
        # Cache por partida para evitar logs repetidos
        self.cache_partidas = {}
        self.ultimo_reset = time.time()
        self.tempo_reset = 300  # Reset cache a cada 5 minutos
        
        # Contadores globais
        self.stats_ciclo = {
            'alavancagem_analisadas': 0,
            'alavancagem_rejeitadas': 0,
            'alavancagem_aprovadas': 0,
            'tradicional_analisadas': 0,
            'tradicional_rejeitadas': 0,
            'tradicional_aprovadas': 0,
            'invertida_analisadas': 0,
            'invertida_rejeitadas': 0,
            'invertida_aprovadas': 0
        }
        
        print("📊 Logger Estratégias ativo - Resumos por partida")
    
    def _detectar_ambiente(self):
        """Detecta se está rodando no Railway"""
        return "railway" if os.environ.get("RAILWAY_ENVIRONMENT") else "local"
    
    def _reset_cache_se_necessario(self):
        """Reset cache periodicamente"""
        agora = time.time()
        if agora - self.ultimo_reset > self.tempo_reset:
            self.cache_partidas.clear()
            self.ultimo_reset = agora
    
    def log_analise_partida(self, jogador, estrategias_testadas):
        """Log resumido da análise de uma partida"""
        if not self.ativo:
            return
        
        self._reset_cache_se_necessario()
        
        # Cache key única por partida
        partida_key = jogador.replace(' vs ', '_').replace(' ', '_')
        
        if partida_key in self.cache_partidas:
            return  # Já logou esta partida
        
        # Marcar como processada
        self.cache_partidas[partida_key] = time.time()
        
        # Contar estratégias
        resumo = []
        for estrategia, resultado, motivo in estrategias_testadas:
            self.stats_ciclo[f'{estrategia}_{resultado}s'] += 1
            
            if resultado == 'aprovada':
                resumo.append(f"✅ {estrategia.upper()}")
            elif resultado == 'rejeitada' and estrategia == 'alavancagem':
                # Mostrar rejeição de alavancagem (é importante)
                resumo.append(f"❌ ALAVANCAGEM: {motivo}")
            elif resultado == 'rejeitada' and motivo in ['Timing inadequado', 'Odds fora do range']:
                # Mostrar rejeições importantes
                resumo.append(f"⚠️ {estrategia}: {motivo}")
        
        if resumo:
            print(f"🔍 {jogador}: {' | '.join(resumo)}")
    
    def log_aprovacao_alavancagem(self, jogador, justificativa):
        """Log específico para aprovação de alavancagem"""
        if not self.ativo:
            return
        
        print(f"🚀 ALAVANCAGEM APROVADA: {jogador}")
        print(f"📊 Justificativa: {justificativa}")
    
    def log_resumo_ciclo(self):
        """Log resumo do ciclo completo"""
        if not self.ativo:
            return
        
        total_analisadas = (self.stats_ciclo['alavancagem_analisadas'] + 
                           self.stats_ciclo['tradicional_analisadas'] + 
                           self.stats_ciclo['invertida_analisadas'])
        
        total_aprovadas = (self.stats_ciclo['alavancagem_aprovadas'] + 
                          self.stats_ciclo['tradicional_aprovadas'] + 
                          self.stats_ciclo['invertida_aprovadas'])
        
        if total_analisadas > 0:
            print(f"📈 Ciclo: {total_analisadas} analisadas • {total_aprovadas} aprovadas")
            
            # Reset stats para próximo ciclo
            for key in self.stats_ciclo:
                self.stats_ciclo[key] = 0

# Instância global
logger_estrategias = LoggerEstrategias()
