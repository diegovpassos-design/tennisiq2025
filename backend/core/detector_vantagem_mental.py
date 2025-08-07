#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MÓDULO: DETECTOR DE VANTAGEM MENTAL
==================================
Sistema para identificar e apostar em adversários com vantagem psicológica
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
            'experiencia_3_sets': 120,          # 3º set = mental > stats (aumentado)
            'momentum_crescente': 90,           # Melhorando na partida
            'superficie_favorita': 60,
            'duplas_bonus': 50                  # Bonus para duplas (mais previsível)
        }
        
        # AJUSTES BASEADOS NA ANÁLISE DE 06/08 - Estratégia invertida 43% -> Meta 65%+
        self.threshold_ativacao = 250          # Aumentado de 200 para 250
        self.threshold_duplas = 230            # Threshold menor para duplas
        self.threshold_individuais = 280       # Threshold maior para individuais
        self.odd_minima_adversario = 2.0       # Aumentado de 1.8 para 2.0
        
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
        MELHORIAS BASEADAS EM ANÁLISE 06/08: Invertida 43% -> Meta 65%+
        """
        score = 0
        fatores = []
        
        # BONUS PARA DUPLAS (melhor performance observada)
        if '/' in adversario.get('nome', ''):
            score += self.fatores_mentais['duplas_bonus']
            fatores.append('duplas_bonus')
        
        # 1. Tie-break recente vencido
        if self._detectar_tie_break_vencido(placar, adversario):
            score += self.fatores_mentais['pos_tie_break_vencedor']
            fatores.append('pos_tie_break_vencedor')
        
        # 2. Recuperação após desvantagem
        if self._detectar_recuperacao(placar, adversario):
            score += self.fatores_mentais['recuperacao_apos_desvantagem']
            fatores.append('recuperacao_apos_desvantagem')
        
        # 3. Situação "nada a perder" (odd alta) - critério mais rigoroso
        try:
            odd_adversario = float(adversario.get('odd', 0))
            if odd_adversario >= 2.5:  # Aumentado de 2.0 para 2.5
                score += self.fatores_mentais['situacao_nada_perder']
                fatores.append('situacao_nada_perder')
        except (ValueError, TypeError):
            pass
        
        # 4. Pressão no favorito (odd baixa)
        try:
            odd_favorito = float(favorito.get('odd', 0))
            if odd_favorito <= 1.55:  # Mais rigoroso: de 1.6 para 1.55
                score += self.fatores_mentais['pressao_no_favorito']
                fatores.append('pressao_no_favorito')
        except (ValueError, TypeError):
            pass
        
        # 5. 3º set (experiência > estatísticas) - FUNCIONOU BEM
        if self._detectar_terceiro_set(placar):
            score += self.fatores_mentais['experiencia_3_sets']
            fatores.append('experiencia_3_sets')
        
        # 6. Momentum crescente
        if self._detectar_momentum_crescente(placar, adversario):
            score += self.fatores_mentais['momentum_crescente']
            fatores.append('momentum_crescente')
        
        confianca = min(score / 400 * 100, 100)  # Ajustado para nova escala
        
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
            try:
                odd_adversario = float(adversario.get('odd', 0))
                return odd_adversario >= 2.0
            except (ValueError, TypeError):
                return False
        return False
    
    def _detectar_recuperacao(self, placar, adversario):
        """
        Detecta recuperação após desvantagem
        """
        sets = placar.split(',')
        if len(sets) >= 2:
            # Se há pelo menos 2 sets e adversário tem odd alta,
            # pode estar se recuperando
            try:
                odd_adversario = float(adversario.get('odd', 0))
                return odd_adversario >= 2.0
            except (ValueError, TypeError):
                return False
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
        MELHORIAS BASEADAS EM ANÁLISE 06/08: Thresholds diferenciados (SEM BLACKLIST)
        """
        score = score_mental['score']
        try:
            odd_adversario = float(adversario.get('odd', 0))
        except (ValueError, TypeError):
            odd_adversario = 0
        
        # THRESHOLD DIFERENCIADO: Duplas vs Individuais
        nome_adversario = adversario.get('nome', '')
        eh_dupla = '/' in nome_adversario
        threshold_usado = self.threshold_duplas if eh_dupla else self.threshold_individuais
        
        # Critérios para inversão (mais rigorosos)
        score_suficiente = score >= threshold_usado
        odd_atrativa = odd_adversario >= self.odd_minima_adversario
        fatores_multiplos = len(score_mental['fatores']) >= 3  # Aumentado de 2 para 3
        
        # Verificação extra para individuais
        if not eh_dupla:
            # Individuais precisam de score ainda maior
            score_suficiente = score >= self.threshold_individuais
        
        inverter = score_suficiente and odd_atrativa and fatores_multiplos
        
        if inverter:
            # Estima EV com base na odd e score mental (mais conservador)
            prob_estimada = min(score / 500, 0.75)  # Mais conservador: max 75% prob
            ev_estimado = (prob_estimada * odd_adversario) - 1
            
            tipo_partida = "dupla" if eh_dupla else "individual"
            justificativa = f"Score mental {score} pontos ({tipo_partida}), {len(score_mental['fatores'])} fatores, odd {odd_adversario}, threshold: {threshold_usado}"
            
            return {
                'inverter': True,
                'target': adversario.get('nome', 'Adversário'),
                'ev_estimado': f"+{ev_estimado:.3f}",
                'odd_alvo': odd_adversario,
                'justificativa': justificativa
            }
        else:
            motivo = []
            if not score_suficiente:
                motivo.append(f"Score {score} < {threshold_usado}")
            if not odd_atrativa:
                motivo.append(f"Odd {odd_adversario} < {self.odd_minima_adversario}")
            if not fatores_multiplos:
                motivo.append(f"Fatores {len(score_mental['fatores'])} < 3")
            
            return {
                'inverter': False,
                'target': 'Favorito Original',
                'ev_estimado': 'N/A',
                'odd_alvo': 0,
                'justificativa': f"Critérios não atendidos: {'; '.join(motivo)}"
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
