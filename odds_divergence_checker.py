"""
Configuração de alertas para divergências de odds significativas
"""

def should_alert_odds_divergence(api_odds, detected_odds, threshold=0.15):
    """
    Verifica se a divergência entre odds é significativa o suficiente para alertar
    
    Args:
        api_odds: Tuple (home_od, away_od) da API atual
        detected_odds: Tuple (home_od, away_od) detectadas pelo sistema
        threshold: Limite de divergência percentual (padrão 15%)
    
    Returns:
        bool: True se deve alertar sobre divergência
    """
    home_diff = abs(api_odds[0] - detected_odds[0]) / detected_odds[0]
    away_diff = abs(api_odds[1] - detected_odds[1]) / detected_odds[1]
    
    return home_diff > threshold or away_diff > threshold

def format_divergence_alert(match_name, api_odds, system_odds, ev):
    """Formatar alerta de divergência para Telegram"""
    
    return f"""
⚠️ DIVERGÊNCIA DETECTADA

🎾 {match_name}
📊 Sistema: {system_odds[0]:.2f} | {system_odds[1]:.2f}
🔄 API Atual: {api_odds[0]:.2f} | {api_odds[1]:.2f}
💰 EV Original: {ev:.1%}

⏰ Verificar odds manualmente antes de apostar
🎯 Odds podem ter mudado desde a detecção
"""

# Exemplo de uso:
if __name__ == "__main__":
    # Caso atual
    api_odds = (2.20, 1.615)
    system_odds = (2.20, 1.61)
    
    if should_alert_odds_divergence(api_odds, system_odds):
        print("🚨 Divergência significativa detectada!")
    else:
        print("✅ Odds dentro da margem normal")
        
    # Teste com divergência real (Bet365 vs Sistema)
    bet365_odds = (1.90, 1.80)
    system_odds = (2.20, 1.61)
    
    if should_alert_odds_divergence(bet365_odds, system_odds):
        print("🚨 Bet365 tem odds muito diferentes!")
        print(format_divergence_alert("Britt Du Pree vs Alice Gillan", bet365_odds, system_odds, 0.10))
