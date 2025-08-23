"""
Cálculo das probabilidades corretas: Ashley Lahey 1.478 vs Alice Gillan 2.10
"""

def calculate_correct_probabilities():
    print("🧮 CÁLCULO CORRETO: Ashley Lahey 1.478 vs Alice Gillan 2.10")
    print("=" * 60)
    
    # Odds corretas da primeira imagem
    odd_ashley = 1.478
    odd_alice = 2.10
    
    print(f"📊 ODDS CORRETAS:")
    print(f"🏠 Ashley Lahey: {odd_ashley}")
    print(f"✈️ Alice Gillan: {odd_alice}")
    
    # Calcula probabilidades implícitas
    prob_ashley = 1 / odd_ashley
    prob_alice = 1 / odd_alice
    
    print(f"\n🔢 CÁLCULO DAS PROBABILIDADES IMPLÍCITAS:")
    print(f"P(Ashley) = 1 / {odd_ashley} = {prob_ashley:.3f} = {prob_ashley * 100:.1f}%")
    print(f"P(Alice) = 1 / {odd_alice} = {prob_alice:.3f} = {prob_alice * 100:.1f}%")
    
    # Soma das probabilidades (overround)
    soma_prob = prob_ashley + prob_alice
    overround = soma_prob - 1.0
    margem_casa = overround * 100
    
    print(f"\n🏠 ANÁLISE DA MARGEM DA CASA:")
    print(f"Soma das probabilidades: {soma_prob:.3f} ({soma_prob * 100:.1f}%)")
    print(f"Overround (margem): {overround:.3f} ({margem_casa:.1f}%)")
    
    # Probabilidades "justas" (sem margem da casa)
    prob_ashley_justa = prob_ashley / soma_prob
    prob_alice_justa = prob_alice / soma_prob
    
    print(f"\n⚖️ PROBABILIDADES 'JUSTAS' (sem margem da casa):")
    print(f"🏠 Ashley: {prob_ashley_justa:.3f} ({prob_ashley_justa * 100:.1f}%)")
    print(f"✈️ Alice: {prob_alice_justa:.3f} ({prob_alice_justa * 100:.1f}%)")
    print(f"✅ Soma: {prob_ashley_justa + prob_alice_justa:.3f} (100.0%)")
    
    # Comparação com o robô que mostrou 81.2%
    print(f"\n🤖 COMPARAÇÃO COM ROBÔ:")
    print(f"Robô mostrou: 81.2% para Ashley")
    print(f"Cálculo real: {prob_ashley * 100:.1f}% para Ashley")
    print(f"Diferença: {abs(81.2 - prob_ashley * 100):.1f} pontos percentuais")
    
    if abs(81.2 - prob_ashley * 100) > 10:
        print(f"🚨 DIFERENÇA MUITO ALTA - Robô usa modelo muito diferente!")
    else:
        print(f"✅ Diferença razoável")
    
    # Análise do favoritismo
    print(f"\n🎯 ANÁLISE DO FAVORITISMO:")
    if odd_ashley < odd_alice:
        print(f"🏆 Ashley é FAVORITA (odd menor: {odd_ashley} vs {odd_alice})")
        diferenca = prob_ashley - prob_alice
        print(f"📊 Diferença de probabilidade: {diferenca * 100:+.1f} pontos percentuais")
    else:
        print(f"🏆 Alice é FAVORITA (odd menor)")
    
    # Classificação do jogo
    max_prob = max(prob_ashley, prob_alice)
    if max_prob > 0.70:
        tipo_jogo = "MUITO DESIGUAL (favorita clara)"
    elif max_prob > 0.60:
        tipo_jogo = "DESIGUAL (favorita moderada)"
    elif max_prob > 0.55:
        tipo_jogo = "LIGEIRAMENTE DESIGUAL"
    else:
        tipo_jogo = "EQUILIBRADO"
    
    print(f"🎾 Tipo do jogo: {tipo_jogo}")
    
    return prob_ashley, prob_alice, prob_ashley_justa, prob_alice_justa

def calculate_ev_scenarios(prob_ashley, prob_alice):
    """Calcula EV para diferentes cenários de modelo"""
    print(f"\n" + "=" * 60)
    print("🎯 CENÁRIOS DE EV COM DIFERENTES MODELOS")
    print("=" * 60)
    
    odd_ashley = 1.478
    odd_alice = 2.10
    
    print(f"Odds: Ashley={odd_ashley} | Alice={odd_alice}")
    print(f"Mercado: Ashley={prob_ashley*100:.1f}% | Alice={prob_alice*100:.1f}%")
    print()
    
    def calc_ev(odds, p_model):
        return p_model * (odds - 1.0) - (1.0 - p_model)
    
    # Cenários de modelo
    cenarios = [
        (0.50, 0.50, "Modelo vê jogo equilibrado (50/50)"),
        (0.60, 0.40, "Modelo favorece ligeiramente Ashley"),
        (0.70, 0.30, "Modelo favorece moderadamente Ashley"),
        (0.80, 0.20, "Modelo favorece muito Ashley"),
        (0.812, 0.188, "Modelo do robô (81.2% Ashley)"),
        (0.65, 0.35, "Modelo favorece Ashley (65%)"),
        (0.55, 0.45, "Modelo favorece pouco Ashley"),
    ]
    
    for p_model_ashley, p_model_alice, descricao in cenarios:
        ev_ashley = calc_ev(odd_ashley, p_model_ashley)
        ev_alice = calc_ev(odd_alice, p_model_alice)
        
        print(f"📊 {descricao}")
        print(f"   Modelo: Ashley={p_model_ashley*100:.0f}% | Alice={p_model_alice*100:.0f}%")
        
        melhor_aposta = ""
        if ev_ashley > 0.02:
            melhor_aposta += f" Ashley: EV={ev_ashley*100:+.1f}%"
        if ev_alice > 0.02:
            melhor_aposta += f" Alice: EV={ev_alice*100:+.1f}%"
        
        if melhor_aposta:
            print(f"   ✅ OPORTUNIDADE:{melhor_aposta}")
        else:
            print(f"   ❌ Sem oportunidades (Ashley={ev_ashley*100:+.1f}% | Alice={ev_alice*100:+.1f}%)")
        print()

def analyze_robot_vs_market():
    """Analisa a diferença entre robô e mercado"""
    print(f"\n" + "=" * 60)
    print("🤖 ANÁLISE: ROBÔ vs MERCADO")
    print("=" * 60)
    
    odd_ashley = 1.478
    prob_mercado = 1 / odd_ashley  # 67.7%
    prob_robo = 0.812  # 81.2%
    
    print(f"💰 Odd Ashley: {odd_ashley}")
    print(f"🏠 Mercado: {prob_mercado * 100:.1f}%")
    print(f"🤖 Robô: {prob_robo * 100:.1f}%")
    print(f"📊 Diferença: {(prob_robo - prob_mercado) * 100:+.1f} pontos percentuais")
    
    # EV se seguirmos o robô
    ev_robo = prob_robo * (odd_ashley - 1) - (1 - prob_robo)
    print(f"\n💡 SE O ROBÔ ESTIVER CORRETO:")
    print(f"EV apostando em Ashley = {ev_robo * 100:+.1f}%")
    
    if ev_robo > 0.20:
        print(f"🚨 EV EXTREMO - Oportunidade excepcional!")
    elif ev_robo > 0.10:
        print(f"✅ EV ALTO - Ótima oportunidade")
    elif ev_robo > 0.05:
        print(f"🟡 EV MODERADO - Boa oportunidade")
    else:
        print(f"❌ EV BAIXO - Oportunidade questionável")
    
    # Qual seria a odd "justa" segundo o robô
    odd_justa_robo = 1 / prob_robo
    print(f"\n🎯 SEGUNDO O ROBÔ:")
    print(f"Odd justa para Ashley seria: {odd_justa_robo:.3f}")
    print(f"Odd atual do mercado: {odd_ashley}")
    print(f"Desconto do mercado: {((odd_ashley / odd_justa_robo) - 1) * 100:+.1f}%")

if __name__ == "__main__":
    prob_ashley, prob_alice, prob_ashley_justa, prob_alice_justa = calculate_correct_probabilities()
    calculate_ev_scenarios(prob_ashley, prob_alice)
    analyze_robot_vs_market()
