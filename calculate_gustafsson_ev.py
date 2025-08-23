"""
Cálculo detalhado do EV para Filip Gustafsson vs Nikola Slavic
"""

def calculate_ev(odds, p_model):
    """Calcula o valor esperado de uma aposta"""
    return p_model * (odds - 1.0) - (1.0 - p_model)

def calculate_gustafsson_vs_slavic():
    print("🎾 CÁLCULO DETALHADO: Filip Gustafsson vs Nikola Slavic")
    print("=" * 60)
    
    # Dados do jogo enviado
    odds_gustafsson = 2.10
    ev_resultado = 0.05  # 5.0%
    
    print(f"📊 DADOS DO JOGO:")
    print(f"🎯 Jogador: Filip Gustafsson")
    print(f"💰 Odd: {odds_gustafsson}")
    print(f"📈 EV enviado: {ev_resultado * 100:.1f}%")
    
    # Para descobrir a probabilidade do modelo, vamos reverter a fórmula
    # EV = p_model * (odds - 1) - (1 - p_model)
    # EV = p_model * (odds - 1) - 1 + p_model
    # EV = p_model * odds - p_model - 1 + p_model
    # EV = p_model * odds - 1
    # p_model = (EV + 1) / odds
    
    p_model = (ev_resultado + 1) / odds_gustafsson
    
    print(f"\n🧠 PROBABILIDADE DO MODELO:")
    print(f"P(Gustafsson ganha) = {p_model:.3f} ({p_model * 100:.1f}%)")
    
    # Verificação: recalcular EV com essa probabilidade
    ev_verificacao = calculate_ev(odds_gustafsson, p_model)
    
    print(f"\n🔢 CÁLCULO STEP-BY-STEP:")
    print(f"EV = P(win) × (Odds - 1) - P(lose)")
    print(f"EV = {p_model:.3f} × ({odds_gustafsson} - 1) - (1 - {p_model:.3f})")
    print(f"EV = {p_model:.3f} × {odds_gustafsson - 1:.1f} - {1 - p_model:.3f}")
    print(f"EV = {p_model * (odds_gustafsson - 1):.3f} - {1 - p_model:.3f}")
    print(f"EV = {ev_verificacao:.3f}")
    print(f"EV = {ev_verificacao * 100:.1f}%")
    
    # Comparação com mercado
    p_market = 1 / odds_gustafsson
    
    print(f"\n📊 COMPARAÇÃO MODELO vs MERCADO:")
    print(f"🏠 Probabilidade implícita do mercado: {p_market:.3f} ({p_market * 100:.1f}%)")
    print(f"🧠 Probabilidade do nosso modelo: {p_model:.3f} ({p_model * 100:.1f}%)")
    print(f"📈 Diferença a nosso favor: {(p_model - p_market) * 100:.1f} pontos percentuais")
    
    print(f"\n💡 INTERPRETAÇÃO:")
    print(f"✅ O mercado vê {p_market * 100:.1f}% de chance para Gustafsson")
    print(f"🎯 Nosso modelo vê {p_model * 100:.1f}% de chance")
    print(f"📊 Essa diferença de {(p_model - p_market) * 100:.1f}pp gera EV de {ev_resultado * 100:.1f}%")
    
    # Explicação do resultado
    if p_model > 0.500:
        modelo_favorece = "Gustafsson"
    else:
        modelo_favorece = "Slavic"
        
    print(f"\n🎾 ANÁLISE DO MODELO:")
    if abs(p_model - 0.5) < 0.01:  # Muito próximo de 50%
        print(f"⚖️ Modelo vê jogo EQUILIBRADO (~50% cada)")
        print(f"💰 EV vem da diferença sutil com odds do mercado")
    else:
        print(f"🎯 Modelo favorece ligeiramente: {modelo_favorece}")
        print(f"📊 Mas ainda considera jogo competitivo")

def show_sensitivity_analysis():
    """Mostra como pequenas mudanças na probabilidade afetam o EV"""
    print(f"\n" + "=" * 60)
    print("📈 ANÁLISE DE SENSIBILIDADE")
    print("=" * 60)
    
    odds = 2.10
    
    probabilities = [0.48, 0.49, 0.50, 0.51, 0.52]
    
    print(f"Odd fixa: {odds}")
    print("Prob.Modelo | EV      | Interpretação")
    print("-" * 40)
    
    for p in probabilities:
        ev = calculate_ev(odds, p)
        if ev >= 0.02:
            status = "✅ OPORTUNIDADE"
        elif ev > 0:
            status = "🟡 VALOR BAIXO"
        else:
            status = "❌ SEM VALOR"
            
        print(f"{p * 100:8.0f}%     | {ev * 100:+5.1f}% | {status}")

if __name__ == "__main__":
    calculate_gustafsson_vs_slavic()
    show_sensitivity_analysis()
