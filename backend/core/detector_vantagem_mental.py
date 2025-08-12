#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MÓDULO: DETECTOR DE VANTAGEM MENTAL
==================================
Sistema para identificar e apostar em adversários com vantagem psicológica

CRITÉRIOS DE ODDS:
- Odd mínima do adversário: 1.8
- Odd máxima do adversário: 2.2
- Range alvo: 1.8 - 2.2 (odds equilibradas para vantagem mental)
"""

import re
import json
from datetime import datetime

class DetectorVantagemMental:
    def __init__(self):
        self.fatores_mentais = {
            'pos_tie_break_vencedor': 150,      # Tie-break recém vencido
            'recuperacao_apos_desvantagem': 120, # Voltou de desvantagem
            'situacao_nada_perder': 100,        # Odd alta (≥2.0)
            'pressao_no_favorito': 80,          # Favorito com pressão
            'experiencia_3_sets': 100,          # 3º set = mental > stats
            'momentum_crescente': 90,           # Melhorando na partida
            'superficie_favorita': 60
        }
        
        self.threshold_ativacao = 200  # Score mínimo para inverter aposta
        self.odd_minima_adversario = 1.8  # Odd mínima do adversário
        self.odd_maxima_adversario = 2.2  # Odd máxima do adversário (meta específica)
    
    def _converter_odd_float(self, odd_value):
        """Converte odd para float de forma segura"""
        try:
            return float(odd_value) if odd_value else 0.0
        except (ValueError, TypeError):
            return 0.0
        
    def analisar_partida(self, partida_data):
        """
        Analisa uma partida e determina se deve apostar no adversário
        """
        try:
            favorito = partida_data.get('favorito', {})
            adversario = partida_data.get('adversario', {})
            placar = partida_data.get('score', '')
            
            # Análise de vantagem mental do adversário
            score_mental_adversario = self._calcular_score_mental(
                adversario, favorito, placar
            )
            
            # Decisão de inversão
            decisao = self._decidir_inversao(score_mental_adversario, adversario)
            
            return {
                'inverter_aposta': decisao['inverter'],
                'target_final': decisao['target'],
                'score_mental': score_mental_adversario['score'],
                'fatores_detectados': score_mental_adversario['fatores'],
                'confianca': score_mental_adversario['confianca'],
                'ev_estimado': decisao['ev_estimado'],
                'odd_alvo': decisao['odd_alvo'],
                'justificativa': decisao['justificativa']
            }
            
        except Exception as e:
            print(f"Erro na análise de vantagem mental: {e}")
            return {'inverter_aposta': False, 'erro': str(e)}
    
    def _calcular_score_mental(self, adversario, favorito, placar):
        """
        Calcula score de vantagem mental do adversário
        """
        score = 0
        fatores = []
        
        # 1. Tie-break recente vencido
        if self._detectar_tie_break_vencido(placar, adversario):
            score += self.fatores_mentais['pos_tie_break_vencedor']
            fatores.append('pos_tie_break_vencedor')
        
        # 2. Recuperação após desvantagem
        if self._detectar_recuperacao(placar, adversario):
            score += self.fatores_mentais['recuperacao_apos_desvantagem']
            fatores.append('recuperacao_apos_desvantagem')
        
        # 3. Situação "nada a perder" (odd alta)
        if self._converter_odd_float(adversario.get('odd', 0)) >= 2.0:
            score += self.fatores_mentais['situacao_nada_perder']
            fatores.append('situacao_nada_perder')
        
        # 4. Pressão no favorito (odd baixa)
        if self._converter_odd_float(favorito.get('odd', 0)) <= 1.6:
            score += self.fatores_mentais['pressao_no_favorito']
            fatores.append('pressao_no_favorito')
        
        # 5. 3º set (experiência > estatísticas)
        if self._detectar_terceiro_set(placar):
            score += self.fatores_mentais['experiencia_3_sets']
            fatores.append('experiencia_3_sets')
        
        # 6. Momentum crescente
        if self._detectar_momentum_crescente(placar, adversario):
            score += self.fatores_mentais['momentum_crescente']
            fatores.append('momentum_crescente')
        
        confianca = min(score / 300 * 100, 100)
        
        return {
            'score': score,
            'fatores': fatores,
            'confianca': confianca
        }
    
    def _detectar_tie_break_vencido(self, placar, adversario):
        """
        Detecta se adversário ganhou tie-break recente
        """
        # Procura por padrões 7-6 ou menção a tie-break
        if '7-6' in placar or '6-7' in placar:
            # Lógica simplificada: se adversário tem odd alta e há tie-break,
            # assume que pode ter vencido (precisa dados mais específicos)
            return self._converter_odd_float(adversario.get('odd', 0)) >= 2.0
        return False
    
    def _detectar_recuperacao(self, placar, adversario):
        """
        Detecta recuperação após desvantagem
        """
        sets = placar.split(',')
        if len(sets) >= 2:
            # Se há pelo menos 2 sets e adversário tem odd alta,
            # pode estar se recuperando
            return self._converter_odd_float(adversario.get('odd', 0)) >= 2.0
        return False
    
    def _detectar_terceiro_set(self, placar):
        """
        Detecta se está no 3º set
        """
        sets = placar.split(',')
        return len(sets) == 3 and '0-0' in placar
    
    def _detectar_momentum_crescente(self, placar, adversario):
        """
        Detecta momentum crescente do adversário
        """
        # Lógica simplificada baseada em padrões do placar
        if 'melhorando' in str(adversario).lower():
            return True
        return False
    
    def _decidir_inversao(self, score_mental, adversario):
        """
        Decide se deve inverter a aposta
        """
        score = score_mental['score']
        odd_adversario = adversario.get('odd', 0)
        
        # Converter odd para float se for string
        try:
            odd_adversario = float(odd_adversario) if odd_adversario else 0.0
        except (ValueError, TypeError):
            odd_adversario = 0.0
        
        # Critérios para inversão
        score_suficiente = score >= self.threshold_ativacao
        odd_no_range = (self.odd_minima_adversario <= odd_adversario <= self.odd_maxima_adversario)
        fatores_multiplos = len(score_mental['fatores']) >= 2
        
        inverter = score_suficiente and odd_no_range and fatores_multiplos
        
        if not odd_no_range and odd_adversario > 0:
            print(f"❌ INVERTIDA: Odd {odd_adversario} fora do range {self.odd_minima_adversario}-{self.odd_maxima_adversario}")
        
        if inverter:
            # Estima EV com base na odd e score mental
            prob_estimada = min(score / 400, 0.8)  # Max 80% prob
            ev_estimado = (prob_estimada * odd_adversario) - 1
            
            justificativa = f"Score mental {score} pontos, {len(score_mental['fatores'])} fatores, odd {odd_adversario}"
            
            return {
                'inverter': True,
                'target': adversario.get('nome', 'Adversário'),
                'ev_estimado': f"+{ev_estimado:.3f}",
                'odd_alvo': odd_adversario,
                'justificativa': justificativa
            }
        else:
            return {
                'inverter': False,
                'target': 'Favorito Original',
                'ev_estimado': 'N/A',
                'odd_alvo': 0,
                'justificativa': f"Score insuficiente: {score}/{self.threshold_ativacao}"
            }

def teste_casos_hoje():
    """
    Testa o sistema com os casos de hoje
    """
    detector = DetectorVantagemMental()
    
    casos_teste = [
        {
            'partida': 'Joe Leather vs Paul Barbier Gazeu',
            'favorito': {'nome': 'Joe Leather', 'odd': 1.615},
            'adversario': {'nome': 'Paul Barbier Gazeu', 'odd': 2.50},
            'score': '6-1,6-7,0-0'
        },
        {
            'partida': 'Cayetana Gay vs Min Liu', 
            'favorito': {'nome': 'Cayetana Gay', 'odd': 1.909},
            'adversario': {'nome': 'Min Liu', 'odd': 2.10},
            'score': '6-7,4-1'
        },
        {
            'partida': 'Loes Ebeling Koning vs Anastasia Abbagnato',
            'favorito': {'nome': 'Loes Ebeling Koning', 'odd': 1.90},
            'adversario': {'nome': 'Anastasia Abbagnato', 'odd': 2.15},
            'score': '5-7,7-5,0-0'
        }
    ]
    
    print("🧠 TESTE DO DETECTOR DE VANTAGEM MENTAL")
    print("="*60)
    
    for i, caso in enumerate(casos_teste, 1):
        print(f"\n📋 CASO {i}: {caso['partida']}")
        resultado = detector.analisar_partida(caso)
        
        print(f"   🎯 Inverter aposta: {'✅ SIM' if resultado['inverter_aposta'] else '❌ NÃO'}")
        if resultado['inverter_aposta']:
            print(f"   🎪 Novo alvo: {resultado['target_final']}")
            print(f"   💰 Odd alvo: {resultado['odd_alvo']}")
            print(f"   📈 EV estimado: {resultado['ev_estimado']}")
            print(f"   💪 Score mental: {resultado['score_mental']} pontos")
            print(f"   🔍 Fatores: {', '.join(resultado['fatores_detectados'])}")
            print(f"   🎯 Confiança: {resultado['confianca']:.1f}%")
            print(f"   📝 Justificativa: {resultado['justificativa']}")

if __name__ == "__main__":
    teste_casos_hoje()
