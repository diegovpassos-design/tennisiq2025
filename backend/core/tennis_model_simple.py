"""
TennisQ - Modelo SIMPLIFICADO baseado apenas em odds
Remove dependência de ranking, form, elo e dados de jogadores
"""

import logging
from typing import Tuple

logger = logging.getLogger(__name__)

class SophisticatedTennisModel:
    """
    Modelo ULTRA SIMPLIFICADO para o TennisQ
    Usa apenas odds do mercado para calcular probabilidades
    Remove toda complexidade de dados de jogadores
    """
    
    def __init__(self, use_real_data: bool = False, api_token: str = None, api_base: str = None):
        """Inicializa modelo simplificado - ignora todos os parâmetros"""
        logger.info("🎯 Modelo SIMPLIFICADO inicializado - usando apenas odds")
        logger.info("❌ Removida toda lógica de ranking, form, elo e dados de jogadores")
    
    def calculate_match_probability(self, player1: str, player2: str, 
                                  surface: str = "hard", 
                                  league: str = "", 
                                  home_odds: float = None, 
                                  away_odds: float = None) -> Tuple[float, float, float]:
        """
        Calcula probabilidades usando APENAS as odds do mercado
        Ignora completamente dados dos jogadores
        
        Returns:
            (prob_home, prob_away, confidence) 
            confidence sempre 1.0 pois usa apenas odds reais
        """
        try:
            if home_odds is None or away_odds is None:
                logger.warning("Odds não fornecidas - usando probabilidades padrão 50/50")
                return 0.5, 0.5, 0.5
            
            # Converte odds para probabilidades implícitas
            prob_home_market = 1.0 / home_odds
            prob_away_market = 1.0 / away_odds
            
            # Normaliza para somar 1.0 (remove a margem da casa)
            total_prob = prob_home_market + prob_away_market
            prob_home_normalized = prob_home_market / total_prob
            prob_away_normalized = prob_away_market / total_prob
            
            logger.info(f"🎯 Probabilidades baseadas APENAS em odds:")
            logger.info(f"   {player1}: {prob_home_normalized:.3f} (odds {home_odds:.2f})")
            logger.info(f"   {player2}: {prob_away_normalized:.3f} (odds {away_odds:.2f})")
            
            # Confidence sempre máxima pois usa dados reais do mercado
            confidence = 1.0
            
            return prob_home_normalized, prob_away_normalized, confidence
            
        except Exception as e:
            logger.error(f"Erro no cálculo simplificado: {e}")
            return 0.5, 0.5, 0.5
    
    def _assess_data_confidence(self, player1_name: str, player2_name: str) -> float:
        """
        Método de compatibilidade - sempre retorna confidence máxima
        pois não depende mais de dados de jogadores
        """
        return 1.0

# Classe de compatibilidade vazia
class PlayerDatabase:
    """Classe vazia para compatibilidade"""
    def __init__(self, *args, **kwargs):
        pass
