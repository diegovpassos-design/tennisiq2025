"""
Cálculo de probabilidades implícitas das odds
"""

def calculate_implied_probability(odds):
    """Calcula a probabilidade implícita de uma odd"""
    return 1 / odds

def calculate_probabilities_from_odds():
    print("🧮 CÁLCULO DE PROBABILIDADES IMPLÍCITAS")
    print("=" * 50)
    
    # Odds fornecidas
    odds_jogador_a = 1.665
    odds_jogador_b = 2.10
    
    print(f"📊 ODDS FORNECIDAS:")
    print(f"🏠 Jogador A: {odds_jogador_a}")
    print(f"✈️ Jogador B: {odds_jogador_b}")
    
    # Calcula probabilidades implícitas
    prob_a = calculate_implied_probability(odds_jogador_a)
    prob_b = calculate_implied_probability(odds_jogador_b)
    
    print(f"\n🔢 CÁLCULO DAS PROBABILIDADES:")
    print(f"P(Jogador A ganha) = 1 / {odds_jogador_a} = {prob_a:.3f}")
    print(f"P(Jogador B ganha) = 1 / {odds_jogador_b} = {prob_b:.3f}")
    
    print(f"\n📊 PROBABILIDADES EM PERCENTUAL:")
    print(f"🏠 Jogador A: {prob_a * 100:.1f}%")
    print(f"✈️ Jogador B: {prob_b * 100:.1f}%")
    
    # Soma das probabilidades (overround)
    soma_prob = prob_a + prob_b
    overround = soma_prob - 1.0
    margem_casa = overround * 100
    
    print(f"\n🏠 ANÁLISE DA MARGEM DA CASA:")
    print(f"Soma das probabilidades: {soma_prob:.3f} ({soma_prob * 100:.1f}%)")
    print(f"Overround (margem): {overround:.3f} ({margem_casa:.1f}%)")
    
    if soma_prob > 1:
        print(f"📈 A casa tem margem de {margem_casa:.1f}%")
    else:
        print(f"⚠️ Probabilidades somam menos que 100% - odds inconsistentes")
    
    # Probabilidades "justas" (sem margem da casa)
    if soma_prob > 1:
        prob_a_justa = prob_a / soma_prob
        prob_b_justa = prob_b / soma_prob
        
        print(f"\n⚖️ PROBABILIDADES 'JUSTAS' (sem margem da casa):")
        print(f"🏠 Jogador A: {prob_a_justa:.3f} ({prob_a_justa * 100:.1f}%)")
        print(f"✈️ Jogador B: {prob_b_justa:.3f} ({prob_b_justa * 100:.1f}%)")
        print(f"✅ Soma: {prob_a_justa + prob_b_justa:.3f} (100.0%)")
    
    # Análise do favoritismo
    print(f"\n🎯 ANÁLISE DO FAVORITISMO:")
    if odds_jogador_a < odds_jogador_b:
        print(f"🏆 Jogador A é FAVORITO (odd menor: {odds_jogador_a} vs {odds_jogador_b})")
        diferenca = prob_a - prob_b
        print(f"📊 Diferença de probabilidade: {diferenca * 100:+.1f} pontos percentuais")
    else:
        print(f"🏆 Jogador B é FAVORITO (odd menor: {odds_jogador_b} vs {odds_jogador_a})")
        diferenca = prob_b - prob_a
        print(f"📊 Diferença de probabilidade: {diferenca * 100:+.1f} pontos percentuais")
    
    # Classificação do jogo
    max_prob = max(prob_a, prob_b)
    if max_prob > 0.65:
        tipo_jogo = "DESIGUAL (favorito claro)"
    elif max_prob > 0.55:
        tipo_jogo = "LIGEIRAMENTE DESIGUAL"
    else:
        tipo_jogo = "EQUILIBRADO"
    
    print(f"🎾 Tipo do jogo: {tipo_jogo}")
    
    return prob_a, prob_b, prob_a_justa if soma_prob > 1 else prob_a, prob_b_justa if soma_prob > 1 else prob_b

def calculate_ev_examples(prob_a, prob_b):
    """Mostra exemplos de EV para diferentes cenários de modelo"""
    print(f"\n" + "=" * 60)
    print("🎯 EXEMPLOS DE EV COM DIFERENTES MODELOS")
    print("=" * 60)
    
    odds_a = 1.665
    odds_b = 2.10
    
    print(f"Se nosso modelo discordar das odds do mercado:")
    print(f"Odds: A={odds_a} | B={odds_b}")
    print(f"Mercado: A={prob_a*100:.1f}% | B={prob_b*100:.1f}%")
    print()
    
    # Cenários de modelo
    cenarios = [
        (0.50, 0.50, "Modelo vê jogo equilibrado (50/50)"),
        (0.55, 0.45, "Modelo favorece ligeiramente A"),
        (0.65, 0.35, "Modelo favorece claramente A"),
        (0.45, 0.55, "Modelo favorece ligeiramente B"),
        (0.40, 0.60, "Modelo favorece claramente B"),
    ]
    
    def calc_ev(odds, p_model):
        return p_model * (odds - 1.0) - (1.0 - p_model)
    
    for p_model_a, p_model_b, descricao in cenarios:
        ev_a = calc_ev(odds_a, p_model_a)
        ev_b = calc_ev(odds_b, p_model_b)
        
        print(f"📊 {descricao}")
        print(f"   Modelo: A={p_model_a*100:.0f}% | B={p_model_b*100:.0f}%")
        
        melhor_aposta = ""
        if ev_a > 0.02:
            melhor_aposta += f" A: EV={ev_a*100:+.1f}%"
        if ev_b > 0.02:
            melhor_aposta += f" B: EV={ev_b*100:+.1f}%"
        
        if melhor_aposta:
            print(f"   ✅ OPORTUNIDADE:{melhor_aposta}")
        else:
            print(f"   ❌ Sem oportunidades (EV A={ev_a*100:+.1f}% | EV B={ev_b*100:+.1f}%)")
        print()

if __name__ == "__main__":
    prob_a, prob_b, prob_a_justa, prob_b_justa = calculate_probabilities_from_odds()
    calculate_ev_examples(prob_a, prob_b)
