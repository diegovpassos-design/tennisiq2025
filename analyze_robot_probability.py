"""
Análise de como o robô chegou a 81.2% de probabilidade para Ashley Lahey
"""

def analyze_probability_calculation():
    print("🤖 ANÁLISE: Como o robô calculou 81.2% para Ashley Lahey")
    print("=" * 60)
    
    # Dados das imagens
    print("📱 DADOS DAS IMAGENS:")
    print("🏆 Torneio: W15 Logrono")
    print("⚔️ Jogo: Ashley Lahey vs Alice Gillan")
    print("💰 Odds: Ashley 1.665 | Alice ~2.10")
    print("🎯 Probabilidade mostrada: 81.2%")
    print("📅 Data: 24/08 06:00")
    
    # Método 1: Probabilidade implícita simples
    odd_ashley = 1.665
    prob_implicita = 1 / odd_ashley
    
    print(f"\n🔢 MÉTODO 1 - Probabilidade Implícita Simples:")
    print(f"P = 1 / {odd_ashley} = {prob_implicita:.3f} = {prob_implicita * 100:.1f}%")
    print(f"❌ Resultado: {prob_implicita * 100:.1f}% ≠ 81.2%")
    
    # Método 2: Considerando odds de Alice
    odd_alice = 2.10
    prob_ashley_implicita = 1 / odd_ashley
    prob_alice_implicita = 1 / odd_alice
    
    print(f"\n🔢 MÉTODO 2 - Probabilidades Implícitas Ambas:")
    print(f"P(Ashley) = 1 / {odd_ashley} = {prob_ashley_implicita:.3f} = {prob_ashley_implicita * 100:.1f}%")
    print(f"P(Alice) = 1 / {odd_alice} = {prob_alice_implicita:.3f} = {prob_alice_implicita * 100:.1f}%")
    print(f"Soma = {(prob_ashley_implicita + prob_alice_implicita) * 100:.1f}%")
    print(f"❌ Ashley: {prob_ashley_implicita * 100:.1f}% ≠ 81.2%")
    
    # Método 3: Probabilidade "justa" (removendo margem da casa)
    soma_total = prob_ashley_implicita + prob_alice_implicita
    prob_ashley_justa = prob_ashley_implicita / soma_total
    prob_alice_justa = prob_alice_implicita / soma_total
    
    print(f"\n🔢 MÉTODO 3 - Probabilidade 'Justa' (sem margem):")
    print(f"Soma das probabilidades: {soma_total:.3f}")
    print(f"P(Ashley) justa = {prob_ashley_implicita:.3f} / {soma_total:.3f} = {prob_ashley_justa:.3f} = {prob_ashley_justa * 100:.1f}%")
    print(f"P(Alice) justa = {prob_alice_implicita:.3f} / {soma_total:.3f} = {prob_alice_justa:.3f} = {prob_alice_justa * 100:.1f}%")
    print(f"❌ Ashley: {prob_ashley_justa * 100:.1f}% ≠ 81.2%")
    
    # Método 4: Tentativa reversa - que odd geraria 81.2%?
    prob_target = 0.812
    odd_necessaria = 1 / prob_target
    
    print(f"\n🔢 MÉTODO 4 - Análise Reversa:")
    print(f"Para ter 81.2% de probabilidade, a odd deveria ser:")
    print(f"Odd = 1 / 0.812 = {odd_necessaria:.3f}")
    print(f"🎯 Mas a odd real é {odd_ashley} (muito diferente)")
    
    # Método 5: Possível modelo de ML/algoritmo personalizado
    print(f"\n🤖 MÉTODO 5 - Modelo de Machine Learning:")
    print(f"🧠 O robô pode estar usando um modelo que considera:")
    print(f"   📊 Histórico dos jogadores")
    print(f"   🎾 Performance em surface similar")
    print(f"   📈 Forma atual")
    print(f"   🏆 Estatísticas do torneio")
    print(f"   ⚖️ Head-to-head")
    print(f"   🌡️ Condições climáticas")
    print(f"   💪 Fatigue/descanso")
    
    # Possível explicação
    print(f"\n💡 HIPÓTESES MAIS PROVÁVEIS:")
    print(f"1. 🎯 Modelo proprietário que analisa dados além das odds")
    print(f"2. 📊 Algoritmo que considera múltiplas fontes de dados")
    print(f"3. 🧮 Cálculo baseado em performance histórica específica")
    print(f"4. ⚠️ Erro no display (mostrou probabilidade de outro cálculo)")
    
    # Análise da discrepância
    diferenca = abs(81.2 - prob_ashley_implicita * 100)
    print(f"\n📈 ANÁLISE DA DISCREPÂNCIA:")
    print(f"Diferença: {diferenca:.1f} pontos percentuais")
    print(f"Isso é uma diferença MUITO significativa!")
    
    if diferenca > 20:
        print(f"🚨 DIFERENÇA EXTREMA: Indica modelo muito diferente das odds de mercado")
    elif diferenca > 10:
        print(f"⚠️ DIFERENÇA ALTA: Modelo pode ter informações privilegiadas")
    else:
        print(f"✅ DIFERENÇA NORMAL: Dentro da variação esperada")

def test_possible_models():
    """Testa possíveis modelos que poderiam gerar 81.2%"""
    print(f"\n" + "=" * 60)
    print("🧪 TESTANDO POSSÍVEIS MODELOS")
    print("=" * 60)
    
    # Cenários possíveis
    cenarios = [
        ("Ranking muito superior de Ashley", 0.812),
        ("Ashley especialista em clay court", 0.812),
        ("Alice com lesão/fadiga", 0.812),
        ("Head-to-head muito favorável", 0.812),
        ("Forma atual excepcional de Ashley", 0.812),
    ]
    
    odd_ashley = 1.665
    
    for descricao, prob_modelo in cenarios:
        # Calcula EV se apostássemos em Ashley com esse modelo
        ev_ashley = prob_modelo * (odd_ashley - 1) - (1 - prob_modelo)
        
        print(f"📊 {descricao}")
        print(f"   Modelo: {prob_modelo * 100:.1f}% para Ashley")
        print(f"   EV apostando em Ashley @ {odd_ashley}: {ev_ashley * 100:+.1f}%")
        
        if ev_ashley > 0.15:  # 15%+
            print(f"   🚨 EV EXTREMO - Aposta muito valiosa")
        elif ev_ashley > 0.05:  # 5%+
            print(f"   ✅ OPORTUNIDADE - EV positivo alto")
        elif ev_ashley > 0:
            print(f"   🟡 VALOR BAIXO - EV positivo pequeno")
        else:
            print(f"   ❌ SEM VALOR - EV negativo")
        print()

if __name__ == "__main__":
    analyze_probability_calculation()
    test_possible_models()
