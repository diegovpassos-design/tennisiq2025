"""
Demonstração do cálculo de EV usado no sistema TennisQ
"""

def calculate_ev(odds, p_model):
    """Calcula o valor esperado de uma aposta"""
    return p_model * (odds - 1.0) - (1.0 - p_model)

def demonstrate_ev_calculation():
    print("🧮 FÓRMULA EV UTILIZADA NO TENNISQ\n")
    print("EV = P(win) × (Odds - 1) - (1 - P(win))")
    print("=" * 50)
    
    # Caso real: Britt Du Pree vs Alice Gillan
    print("\n📊 EXEMPLO: Britt Du Pree vs Alice Gillan")
    print("🎯 Odd: 2.20")
    print("🧠 Modelo: 50% de chance (0.500)")
    
    odds = 2.20
    p_model = 0.500
    
    print(f"\n🔢 CÁLCULO PASSO A PASSO:")
    print(f"P(win) = {p_model}")
    print(f"P(lose) = {1 - p_model}")
    print(f"Odds = {odds}")
    print(f"Lucro se ganhar = {odds - 1.0}")
    
    print(f"\n📈 APLICANDO A FÓRMULA:")
    print(f"EV = {p_model} × ({odds} - 1) - ({1 - p_model})")
    print(f"EV = {p_model} × {odds - 1.0} - {1 - p_model}")
    print(f"EV = {p_model * (odds - 1.0)} - {1 - p_model}")
    
    ev = calculate_ev(odds, p_model)
    print(f"EV = {ev:.3f}")
    print(f"EV = {ev * 100:.1f}%")
    
    print(f"\n💡 INTERPRETAÇÃO:")
    if ev > 0:
        print(f"✅ EV POSITIVO = {ev * 100:.1f}%")
        print(f"🎯 OPORTUNIDADE: A aposta tem valor esperado positivo")
        print(f"💰 A longo prazo, esta aposta é lucrativa")
    else:
        print(f"❌ EV NEGATIVO = {ev * 100:.1f}%")
        print(f"📉 NÃO APOSTAR: A aposta tem valor esperado negativo")
    
    # Comparação com probabilidade implícita do mercado
    p_market = 1 / odds
    print(f"\n🏠 PROBABILIDADE IMPLÍCITA DO MERCADO:")
    print(f"P(market) = 1 / {odds} = {p_market:.3f} ({p_market * 100:.1f}%)")
    print(f"🧠 P(modelo) = {p_model:.3f} ({p_model * 100:.1f}%)")
    
    if p_model > p_market:
        print(f"✅ NOSSO MODELO VÊ MAIOR CHANCE = OPORTUNIDADE")
    else:
        print(f"❌ MERCADO VÊ MAIOR CHANCE = SEM VALOR")

def test_different_scenarios():
    print("\n" + "=" * 60)
    print("🧪 TESTANDO DIFERENTES CENÁRIOS")
    print("=" * 60)
    
    scenarios = [
        (2.20, 0.500, "Britt Du Pree (caso real)"),
        (2.10, 0.500, "Rio Wakayama (caso real)"),
        (1.83, 0.500, "Odds equilibradas"),
        (2.00, 0.600, "Modelo favorece jogador"),
        (2.00, 0.400, "Modelo desfavorece jogador"),
    ]
    
    for odds, p_model, description in scenarios:
        ev = calculate_ev(odds, p_model)
        p_market = 1 / odds
        
        print(f"\n📊 {description}")
        print(f"   Odds: {odds} | Modelo: {p_model * 100:.0f}% | Mercado: {p_market * 100:.1f}%")
        print(f"   EV: {ev:.3f} ({ev * 100:+.1f}%)", end="")
        
        if ev > 0.02:  # Filtro mínimo do sistema
            print(" ✅ OPORTUNIDADE")
        elif ev > 0:
            print(" 🟡 VALOR BAIXO")
        else:
            print(" ❌ SEM VALOR")

if __name__ == "__main__":
    demonstrate_ev_calculation()
    test_different_scenarios()
