#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
INTEGRAÇÃO DASHBOARD - TennisIQ Bot
==================================
Sistema para gerar dados para o dashboard web
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any

# Configurar caminhos para nova estrutura
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

class DashboardLogger:
    def __init__(self):
        self.arquivo_status = os.path.join(PROJECT_ROOT, 'storage', 'database', 'bot_status.json')
        self.arquivo_partidas = os.path.join(PROJECT_ROOT, 'storage', 'database', 'partidas_analisadas.json')
        self.arquivo_sinais = os.path.join(PROJECT_ROOT, 'storage', 'database', 'sinais_gerados.json')
        self.partidas_cache = []
        self.sinais_cache = []
        
        # Carrega dados existentes
        self.carregar_dados_existentes()
    
    def carregar_dados_existentes(self):
        """Carrega dados existentes dos arquivos"""
        try:
            if os.path.exists(self.arquivo_partidas):
                with open(self.arquivo_partidas, 'r', encoding='utf-8') as f:
                    self.partidas_cache = json.load(f)
        except:
            self.partidas_cache = []
        
        try:
            if os.path.exists(self.arquivo_sinais):
                with open(self.arquivo_sinais, 'r', encoding='utf-8') as f:
                    self.sinais_cache = json.load(f)
        except:
            self.sinais_cache = []
    
    def atualizar_status_bot(self, ativo: bool, requests_restantes: int, proxima_verificacao: str = None):
        """Atualiza status do bot"""
        status = {
            'ativo': ativo,
            'ultimo_update': datetime.now().isoformat(),
            'requests_restantes': requests_restantes,
            'proxima_verificacao': proxima_verificacao
        }
        
        with open(self.arquivo_status, 'w', encoding='utf-8') as f:
            json.dump(status, f, ensure_ascii=False, indent=2)
    
    def log_partida_analisada(self, 
                            jogador1: str, 
                            jogador2: str,
                            placar: str,
                            odds1: float,
                            odds2: float,
                            ev: float,
                            momentum_score: float,
                            timing_priority: int,
                            mental_score: int,
                            decisao: str,
                            motivo: str,
                            stats_jogador1: dict = None,
                            stats_jogador2: dict = None):
        """Registra uma partida analisada com dados completos dos jogadores"""
        
        # Processar stats dos jogadores para adicionar valores calculados
        stats_j1 = stats_jogador1.copy() if stats_jogador1 else {}
        stats_j2 = stats_jogador2.copy() if stats_jogador2 else {}
        
        # Calcular momentum score individual baseado no placar
        momentum_j1, momentum_j2 = self._calcular_momentum_individual(placar)
        stats_j1['momentum_score'] = momentum_j1
        stats_j2['momentum_score'] = momentum_j2
        
        # Calcular EV individual baseado nas odds
        ev_j1 = self._calcular_ev_individual(momentum_j1, odds1)
        ev_j2 = self._calcular_ev_individual(momentum_j2, odds2)
        stats_j1['ev'] = ev_j1
        stats_j2['ev'] = ev_j2
        
        # Calcular mental score individual (baseado no placar e contexto)
        mental_j1, mental_j2 = self._calcular_mental_score_individual(placar, odds1, odds2)
        stats_j1['mental_score'] = mental_j1
        stats_j2['mental_score'] = mental_j2
        
        partida = {
            'timestamp': datetime.now().isoformat(),
            'jogador1': jogador1,
            'jogador2': jogador2,
            'placar': placar,
            'odds1': odds1,
            'odds2': odds2,
            'ev': ev,
            'momentum_score': momentum_score,
            'timing_priority': timing_priority,
            'mental_score': mental_score,
            'decisao': decisao,
            'motivo': motivo,
            'stats_jogador1': stats_j1,
            'stats_jogador2': stats_j2
        }
        
        self.partidas_cache.append(partida)
        
        # Mantém apenas últimas 100 partidas
        if len(self.partidas_cache) > 100:
            self.partidas_cache = self.partidas_cache[-100:]
        
        # Salva no arquivo
        with open(self.arquivo_partidas, 'w', encoding='utf-8') as f:
            json.dump(self.partidas_cache, f, ensure_ascii=False, indent=2)
    
    def log_sinal_gerado(self,
                        tipo: str,
                        target: str,
                        odd: float,
                        ev: float,
                        confianca: float,
                        mental_score: int = None,
                        fatores_mentais: List[str] = None):
        """Registra um sinal gerado"""
        
        sinal = {
            'timestamp': datetime.now().isoformat(),
            'tipo': tipo,
            'target': target,
            'odd': odd,
            'ev': ev,
            'confianca': confianca,
            'mental_score': mental_score,
            'fatores_mentais': ','.join(fatores_mentais) if fatores_mentais else None,
            'resultado': 'PENDING'  # Será atualizado depois
        }
        
        self.sinais_cache.append(sinal)
        
        # Mantém apenas últimos 50 sinais
        if len(self.sinais_cache) > 50:
            self.sinais_cache = self.sinais_cache[-50:]
        
        # Salva no arquivo
        with open(self.arquivo_sinais, 'w', encoding='utf-8') as f:
            json.dump(self.sinais_cache, f, ensure_ascii=False, indent=2)
    
    def _calcular_momentum_individual(self, placar):
        """Calcula momentum score individual baseado no placar"""
        try:
            # Parse do placar: "6-3,4-5" ou "2-6,5-4"
            sets = placar.split(',')
            score_j1 = 0
            score_j2 = 0
            
            for set_score in sets:
                if '-' in set_score:
                    games = set_score.split('-')
                    if len(games) == 2:
                        g1, g2 = int(games[0]), int(games[1])
                        score_j1 += g1
                        score_j2 += g2
            
            total = score_j1 + score_j2
            if total > 0:
                momentum_j1 = round((score_j1 / total) * 100, 1)
                momentum_j2 = round((score_j2 / total) * 100, 1)
                return momentum_j1, momentum_j2
            else:
                return 50.0, 50.0
        except:
            return 50.0, 50.0
    
    def _calcular_ev_individual(self, momentum, odd):
        """Calcula EV individual baseado no momentum e odd"""
        try:
            # Calcular EV independente do momentum (remover condição > 50)
            probability = momentum / 100
            implied_prob = 1 / odd
            ev = (probability * (odd - 1)) - (1 - probability)
            return round(ev, 3)
        except:
            return 0.0
    
    def _calcular_mental_score_individual(self, placar, odds1, odds2):
        """Calcula mental score individual baseado no contexto"""
        try:
            mental_j1 = 0
            mental_j2 = 0
            
            # Análise do placar para detectar situações mentais
            sets = placar.split(',')
            
            # Se está no 3º set (+100 pontos para ambos - experiência > stats)
            if len(sets) >= 3:
                mental_j1 += 100
                mental_j2 += 100
            
            # Se veio de desvantagem (recuperação = +120 pontos)
            if len(sets) >= 2:
                set1 = sets[0].split('-')
                set2 = sets[1].split('-')
                if len(set1) == 2 and len(set2) == 2:
                    # J1 perdeu 1º set mas ganhou 2º
                    if int(set1[0]) < int(set1[1]) and int(set2[0]) > int(set2[1]):
                        mental_j1 += 120
                    # J2 perdeu 1º set mas ganhou 2º
                    elif int(set1[1]) < int(set1[0]) and int(set2[1]) > int(set2[0]):
                        mental_j2 += 120
            
            # Pressure baseada nas odds 
            if odds1 < odds2:  # J1 é favorito
                if odds1 <= 1.6:  # Favorito com muita pressão
                    mental_j1 += 80  # Pressão no favorito
                if odds2 >= 2.0:  # J2 azarão "nada a perder"
                    mental_j2 += 100  # Situação "nada a perder"
            elif odds2 < odds1:  # J2 é favorito
                if odds2 <= 1.6:  # Favorito com muita pressão
                    mental_j2 += 80  # Pressão no favorito
                if odds1 >= 2.0:  # J1 azarão "nada a perder"
                    mental_j1 += 100  # Situação "nada a perder"
            
            # Detectar tie-breaks no placar (score 7-6 = tie-break)
            for set_score in sets:
                if '-' in set_score:
                    games = set_score.split('-')
                    if len(games) == 2:
                        g1, g2 = int(games[0]), int(games[1])
                        # Tie-break vencido (+150 pontos)
                        if (g1 == 7 and g2 == 6):
                            mental_j1 += 150  # J1 venceu tie-break
                        elif (g1 == 6 and g2 == 7):
                            mental_j2 += 150  # J2 venceu tie-break
            
            return mental_j1, mental_j2
        except:
            return 0, 0
    
    def atualizar_resultado_sinal(self, target: str, timestamp: str, resultado: str, roi: float = None):
        """Atualiza resultado de um sinal"""
        for sinal in self.sinais_cache:
            if sinal['target'] == target and sinal['timestamp'].startswith(timestamp[:16]):
                sinal['resultado'] = resultado
                if roi is not None:
                    sinal['roi'] = roi
                break
        
        # Salva no arquivo
        with open(self.arquivo_sinais, 'w', encoding='utf-8') as f:
            json.dump(self.sinais_cache, f, ensure_ascii=False, indent=2)
    
    def obter_dados_dashboard(self):
        """Obtém todos os dados processados para o dashboard"""
        # Recarrega dados mais recentes
        self.carregar_dados_existentes()
        
        # Filtra partidas reais (não dados de teste)
        partidas_reais = [p for p in self.partidas_cache if p.get('jogador1') not in ['Jogador 1', 'Jogador 2']]
        
        # Calcula estatísticas
        total_partidas = len(partidas_reais)
        total_sinais = len(self.sinais_cache)
        
        # Taxa de sucesso baseada em sinais com resultado
        sinais_com_resultado = [s for s in self.sinais_cache if s.get('resultado') in ['GREEN', 'RED']]
        taxa_sucesso = 0.0
        if sinais_com_resultado:
            greens = len([s for s in sinais_com_resultado if s.get('resultado') == 'GREEN'])
            taxa_sucesso = (greens / len(sinais_com_resultado)) * 100
        
        # EV médio das partidas analisadas (usando cálculo corrigido)
        evs_validos = []
        for partida in partidas_reais:
            # Recalcular EV com a lógica corrigida para ambos os jogadores
            momentum1 = partida.get('momentum1', 50)
            momentum2 = partida.get('momentum2', 50)
            odds1 = partida.get('odds1', 2.0)
            odds2 = partida.get('odds2', 2.0)
            
            ev1 = self._calcular_ev_individual(momentum1, odds1)
            ev2 = self._calcular_ev_individual(momentum2, odds2)
            
            if ev1 != 0:
                evs_validos.append(ev1)
            if ev2 != 0:
                evs_validos.append(ev2)
        
        ev_medio = sum(evs_validos) / len(evs_validos) if evs_validos else 0.0
        
        # Tipos de sinais
        sinais_invertidos = len([s for s in self.sinais_cache if s.get('tipo') == 'INVERTIDO'])
        sinais_tradicionais = len([s for s in self.sinais_cache if s.get('tipo') == 'TRADICIONAL'])
        
        return {
            'partidas_analisadas': partidas_reais[-20:],  # Últimas 20 para lista
            'sinais_gerados': self.sinais_cache,
            'estatisticas': {
                'total_partidas': total_partidas,
                'total_sinais': total_sinais,
                'taxa_sucesso': taxa_sucesso,
                'ev_medio': ev_medio,
                'sinais_invertidos': sinais_invertidos,
                'sinais_tradicionais': sinais_tradicionais
            }
        }

# Instância global para usar no bot
dashboard_logger = DashboardLogger()
