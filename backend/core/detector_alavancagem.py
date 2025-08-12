#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MÓDULO: DETECTOR DE ALAVANCAGEM
===============================
Sistema para identificar oportunidades de alavancagem baseado em critérios específicos:
- Primeiro set terminado
- Jogador da oportunidade ganhou o primeiro set
- Está ganhando o segundo set
- É melhor nas estatísticas que o adversário
- Odd entre 1.20 e 1.40
"""

import re
import json
from datetime import datetime

class DetectorAlavancagem:
    def __init__(self):
        # Critérios específicos para alavancagem
        self.odd_minima = 1.20
        self.odd_maxima = 1.40
        self.momentum_minimo = 65  # Para confirmar que é melhor estatisticamente
        
    def _converter_odd_float(self, odd_value):
        """Converte odd para float de forma segura"""
        try:
            return float(odd_value) if odd_value else 0.0
        except (ValueError, TypeError):
            return 0.0
    
    def analisar_oportunidade_alavancagem(self, oportunidade_data, placar, odds_data):
        """
        Analisa se uma oportunidade atende aos critérios de alavancagem
        """
        try:
            jogador_oportunidade = oportunidade_data.get('jogador', '')
            oponente = oportunidade_data.get('oponente', '')
            tipo_oportunidade = oportunidade_data.get('tipo', '')  # HOME ou AWAY
            
            # Obter odd do jogador da oportunidade
            if tipo_oportunidade == 'HOME':
                odd_jogador = self._converter_odd_float(odds_data.get('jogador1_odd', 0))
            else:
                odd_jogador = self._converter_odd_float(odds_data.get('jogador2_odd', 0))
            
            # 1. Verificar se a odd está no range correto (1.20 - 1.40)
            if not (self.odd_minima <= odd_jogador <= self.odd_maxima):
                return {
                    'alavancagem_aprovada': False,
                    'motivo': f"Odd {odd_jogador} fora do range 1.20-1.40"
                }
            
            # 2. Verificar se o primeiro set terminou
            if not self._primeiro_set_terminou(placar):
                return {
                    'alavancagem_aprovada': False,
                    'motivo': "Primeiro set ainda não terminou"
                }
            
            # 3. Verificar se o jogador da oportunidade ganhou o primeiro set
            if not self._jogador_ganhou_primeiro_set(placar, tipo_oportunidade):
                return {
                    'alavancagem_aprovada': False,
                    'motivo': "Jogador não ganhou o primeiro set"
                }
            
            # 4. Verificar se está ganhando o segundo set
            if not self._esta_ganhando_segundo_set(placar, tipo_oportunidade):
                return {
                    'alavancagem_aprovada': False,
                    'motivo': "Não está ganhando o segundo set"
                }
            
            # 5. Verificar se é melhor estatisticamente (usando momentum da oportunidade)
            momentum_jogador = oportunidade_data.get('momentum_score', 0)
            if momentum_jogador < self.momentum_minimo:
                return {
                    'alavancagem_aprovada': False,
                    'motivo': f"Momentum {momentum_jogador}% < {self.momentum_minimo}% (não é estatisticamente superior)"
                }
            
            # Se passou em todos os critérios
            return {
                'alavancagem_aprovada': True,
                'jogador_alvo': jogador_oportunidade,
                'odd_alvo': odd_jogador,
                'ev_estimado': oportunidade_data.get('ev', 0),
                'momentum_score': momentum_jogador,
                'justificativa': f"Alavancagem: {jogador_oportunidade} ganhou 1º set, liderando 2º set, momentum {momentum_jogador}%, odd {odd_jogador}",
                'confianca': 'ALTA',
                'estrategia': 'ALAVANCAGEM'
            }
            
        except Exception as e:
            print(f"Erro na análise de alavancagem: {e}")
            return {
                'alavancagem_aprovada': False,
                'erro': str(e)
            }
    
    def _primeiro_set_terminou(self, placar):
        """
        Verifica se o primeiro set já terminou
        Formato esperado: "6-4, 3-2" (primeiro set 6-4, segundo set 3-2)
        """
        if not placar or ',' not in placar:
            return False
        
        try:
            sets = placar.split(',')
            if len(sets) < 2:
                return False
            
            primeiro_set = sets[0].strip()
            if '-' in primeiro_set:
                home_score, away_score = primeiro_set.split('-')
                home_score = int(home_score.strip())
                away_score = int(away_score.strip())
                
                # Verifica se o set terminou (6+ games para o vencedor e diferença adequada)
                if (home_score >= 6 or away_score >= 6):
                    # Vitória normal (6-4, 6-3, etc.) ou tie-break (7-6)
                    if abs(home_score - away_score) >= 2 or max(home_score, away_score) == 7:
                        return True
        except:
            return False
        
        return False
    
    def _jogador_ganhou_primeiro_set(self, placar, tipo_oportunidade):
        """
        Verifica se o jogador da oportunidade ganhou o primeiro set
        tipo_oportunidade: 'HOME' ou 'AWAY'
        """
        if not placar or ',' not in placar:
            return False
        
        try:
            sets = placar.split(',')
            primeiro_set = sets[0].strip()
            
            if '-' in primeiro_set:
                home_score, away_score = primeiro_set.split('-')
                home_score = int(home_score.strip())
                away_score = int(away_score.strip())
                
                if tipo_oportunidade == 'HOME':
                    # Jogador HOME ganhou o primeiro set?
                    return home_score > away_score
                else:
                    # Jogador AWAY ganhou o primeiro set?
                    return away_score > home_score
        except:
            return False
        
        return False
    
    def _esta_ganhando_segundo_set(self, placar, tipo_oportunidade):
        """
        Verifica se o jogador está ganhando o segundo set
        """
        if not placar or ',' not in placar:
            return False
        
        try:
            sets = placar.split(',')
            if len(sets) < 2:
                return False
            
            segundo_set = sets[1].strip()
            
            if '-' in segundo_set:
                home_score, away_score = segundo_set.split('-')
                home_score = int(home_score.strip())
                away_score = int(away_score.strip())
                
                if tipo_oportunidade == 'HOME':
                    # Jogador HOME está ganhando o segundo set?
                    return home_score > away_score
                else:
                    # Jogador AWAY está ganhando o segundo set?
                    return away_score > home_score
        except:
            return False
        
        return False

def teste_detector_alavancagem():
    """
    Testa o detector de alavancagem com casos exemplo
    """
    detector = DetectorAlavancagem()
    
    casos_teste = [
        {
            'nome': 'Caso Aprovado - Alavancagem Perfeita',
            'oportunidade': {
                'jogador': 'João Silva',
                'oponente': 'Pedro Santos',
                'tipo': 'HOME',
                'momentum_score': 75,
                'ev': 0.18
            },
            'placar': '6-4, 3-1',  # Ganhou 1º set 6-4, ganhando 2º set 3-1
            'odds': {
                'jogador1_odd': '1.35',  # João (HOME)
                'jogador2_odd': '2.50'   # Pedro (AWAY)
            }
        },
        {
            'nome': 'Caso Rejeitado - Odd muito alta',
            'oportunidade': {
                'jogador': 'Maria Costa',
                'oponente': 'Ana Lima',
                'tipo': 'AWAY',
                'momentum_score': 80,
                'ev': 0.20
            },
            'placar': '4-6, 2-1',  # Perdeu 1º set, ganhando 2º set
            'odds': {
                'jogador1_odd': '1.25',  # Ana (HOME)
                'jogador2_odd': '1.55'   # Maria (AWAY) - odd muito alta
            }
        },
        {
            'nome': 'Caso Rejeitado - Não ganhou 1º set',
            'oportunidade': {
                'jogador': 'Carlos Mendes',
                'oponente': 'Roberto Filho',
                'tipo': 'HOME',
                'momentum_score': 70,
                'ev': 0.16
            },
            'placar': '4-6, 3-1',  # Perdeu 1º set 4-6, ganhando 2º set 3-1
            'odds': {
                'jogador1_odd': '1.30',  # Carlos (HOME)
                'jogador2_odd': '2.80'   # Roberto (AWAY)
            }
        }
    ]
    
    print("🧪 TESTE DO DETECTOR DE ALAVANCAGEM")
    print("=" * 50)
    
    for caso in casos_teste:
        print(f"\n📋 {caso['nome']}")
        print(f"   Jogador: {caso['oportunidade']['jogador']} (odd: {caso['odds'].get('jogador1_odd' if caso['oportunidade']['tipo'] == 'HOME' else 'jogador2_odd')})")
        print(f"   Placar: {caso['placar']}")
        print(f"   Momentum: {caso['oportunidade']['momentum_score']}%")
        
        resultado = detector.analisar_oportunidade_alavancagem(
            caso['oportunidade'], 
            caso['placar'], 
            caso['odds']
        )
        
        if resultado['alavancagem_aprovada']:
            print(f"   ✅ APROVADO: {resultado['justificativa']}")
        else:
            print(f"   ❌ REJEITADO: {resultado['motivo']}")

if __name__ == "__main__":
    teste_detector_alavancagem()
