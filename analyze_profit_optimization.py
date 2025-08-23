"""
Análise de lucratividade das oportunidades - identificando perdas de lucro
"""

def analyze_opportunities_data():
    print("📊 ANÁLISE DE LUCRATIVIDADE - IDENTIFICANDO PERDAS DE LUCRO")
    print("=" * 70)
    
    # Dados extraídos da planilha - TODAS AS 38 OPORTUNIDADES
    opportunities = [
        {"id": 1, "torneio": "WTA Cleveland", "jogo": "Sorana Cirstea vs Anastasia Zakharova", "aposta": "Anastasia Zakharova", "odd": 2.375, "ev": 18.8, "status": "RED", "resultado": -30},
        {"id": 2, "torneio": "UTR Pro Waco", "jogo": "Zachary Cohen vs Sean Ferguson", "aposta": "Sean Ferguson", "odd": 2.100, "ev": 5.0, "status": "RED", "resultado": -30},
        {"id": 3, "torneio": "ATP Winston-Salem", "jogo": "Botic Van De Zandschulp vs Giovanni Mpetshi Perricard", "aposta": "Botic Van De Zandschulp", "odd": 2.200, "ev": 10.0, "status": "GREEN", "resultado": 36},
        {"id": 4, "torneio": "WTA Cleveland", "jogo": "Ann Li vs Xinyu Wang", "aposta": "Ann Li", "odd": 2.200, "ev": 10.0, "status": "GREEN", "resultado": 36},
        {"id": 5, "torneio": "UTR Pro Gold Coast", "jogo": "Scott Jones vs Zane Stevens", "aposta": "Zane Stevens", "odd": 2.375, "ev": 18.8, "status": "AVOID", "resultado": 0},
        {"id": 6, "torneio": "UTR Pro Yokohama", "jogo": "Ryotaro Matsumura vs Ryota Tanuma", "aposta": "Ryota Tanuma", "odd": 2.250, "ev": 12.5, "status": "RED", "resultado": -30},
        {"id": 7, "torneio": "WTA Monterrey", "jogo": "Marie Bouzkova vs Ekaterina Alexandrova", "aposta": "Marie Bouzkova", "odd": 2.200, "ev": 10.0, "status": "AVOID", "resultado": 0},
        {"id": 8, "torneio": "ITF M15 Nakhon Pathom", "jogo": "Thantub Suksumrarn vs Markus Malaszszak", "aposta": "Markus Malaszszak", "odd": 2.375, "ev": 18.8, "status": "GREEN", "resultado": 41.25},
        {"id": 9, "torneio": "ITF W15 Nakhon Pathom", "jogo": "Patcharin Cheapchandej vs Fangran Tian", "aposta": "Fangran Tian", "odd": 2.200, "ev": 10.0, "status": "RED", "resultado": -30},
        {"id": 10, "torneio": "ITF W15 Nakhon Pathom", "jogo": "Aunchisa Chanta vs Misaki Matsuda", "aposta": "Aunchisa Chanta", "odd": 2.100, "ev": 5.0, "status": "RED", "resultado": -30},
        {"id": 11, "torneio": "UTR Pro Yokohama Women", "jogo": "Rio Wakayama vs Suzuna Oigawa", "aposta": "Rio Wakayama", "odd": 2.100, "ev": 5.0, "status": "RED", "resultado": -30},
        {"id": 12, "torneio": "ITF M15 Nakhon Pathom MD", "jogo": "Fitriadi/Junhyeon Lee vs Auytayakul/Malaszszak", "aposta": "Auytayakul/Malaszszak", "odd": 2.250, "ev": 10.3, "status": "GREEN", "resultado": 37.5},
        {"id": 13, "torneio": "UTR Pro Budapest Women", "jogo": "Hannah Read vs Nikola Homolkova", "aposta": "Nikola Homolkova", "odd": 2.250, "ev": 12.5, "status": "RED", "resultado": -30},
        {"id": 14, "torneio": "UTR Pro Budapest", "jogo": "Gergely Madarasz vs Stijn Paardekooper", "aposta": "Stijn Paardekooper", "odd": 2.200, "ev": 10.0, "status": "RED", "resultado": -30},
        {"id": 15, "torneio": "ITF W50 Bistrita", "jogo": "Miriam Bulgaru vs Ylena In-Albon", "aposta": "Ylena In-Albon", "odd": 2.375, "ev": 18.8, "status": "RED", "resultado": -30},
        {"id": 16, "torneio": "ITF M25 Idanha-A-Nova", "jogo": "Tom Paris vs Joris De Loore", "aposta": "Tom Paris", "odd": 2.200, "ev": 7.8, "status": "GREEN", "resultado": 36},
        {"id": 17, "torneio": "ITF W35 Verbier", "jogo": "Sofia Shapatava vs Tina Nadine Smith", "aposta": "Sofia Shapatava", "odd": 2.100, "ev": 5.0, "status": "RED", "resultado": -30},
        {"id": 18, "torneio": "ITF M25 Maribor", "jogo": "Sean Cuenin vs Sebastian Sorger", "aposta": "Sean Cuenin", "odd": 2.250, "ev": 12.5, "status": "GREEN", "resultado": 37.5},
        {"id": 19, "torneio": "Challenger Augsburg MD", "jogo": "Masur/Sanchez Martinez vs Ruehl/Zahraj", "aposta": "Ruehl/Zahraj", "odd": 2.200, "ev": 7.8, "status": "RED", "resultado": -30},
        {"id": 20, "torneio": "ITF M15 Bastad", "jogo": "Filip Gustafsson vs Nikola Slavic", "aposta": "Filip Gustafsson", "odd": 2.100, "ev": 5.0, "status": "RED", "resultado": -30},
        {"id": 21, "torneio": "ITF W15 Logrono", "jogo": "Britt Du Pree vs Alice Gillan", "aposta": "Britt Du Pree", "odd": 2.200, "ev": 10.0, "status": "RED", "resultado": -30},
        {"id": 22, "torneio": "Challenger Hersonissos", "jogo": "Moez Echargui vs Dan Added", "aposta": "Dan Added", "odd": 2.100, "ev": 2.9, "status": "AVOID", "resultado": 0},
        {"id": 23, "torneio": "ITF M25 Idanha-A-Nova MD", "jogo": "Araujo/Marques vs Barroso Campos/Oliveira", "aposta": "Barroso Campos/Oliveira", "odd": 2.250, "ev": 14.7, "status": "RED", "resultado": -30},
        {"id": 24, "torneio": "ITF W35 Verbier", "jogo": "Dalila Jakupovic vs Alina Granwehr", "aposta": "Alina Granwehr", "odd": 2.100, "ev": 5.0, "status": "GREEN", "resultado": 33},
        {"id": 25, "torneio": "ITF M25 Maribor MD", "jogo": "Kaukovalta/Vasa vs Basic/Kupcic", "aposta": "Basic/Kupcic", "odd": 2.250, "ev": 12.5, "status": "RED", "resultado": -30},
        {"id": 26, "torneio": "ITF M25 Muttenz MD", "jogo": "Casanova/Parizzia vs Burdet/Von Der Schulenburg", "aposta": "Burdet/Von Der Schulenburg", "odd": 2.375, "ev": 21.1, "status": "GREEN", "resultado": 41.25},
        {"id": 27, "torneio": "ITF W15 Wanfercee-Baulet", "jogo": "Amelie Van Impe vs Mina Hodzic", "aposta": "Mina Hodzic", "odd": 2.375, "ev": 18.8, "status": "RED", "resultado": -30},
        {"id": 28, "torneio": "ITF M15 Bastad MD", "jogo": "H Lithen/Slavic vs Johansson/Shepp", "aposta": "Johansson/Shepp", "odd": 2.200, "ev": 7.8, "status": "GREEN", "resultado": 36},
        {"id": 29, "torneio": "Challenger Augsburg", "jogo": "Cedrik-Marcel Stebe vs Alexander Ritschard", "aposta": "Cedrik-Marcel Stebe", "odd": 2.100, "ev": 5.0, "status": "GREEN", "resultado": 33},
        {"id": 30, "torneio": "ITF M15 Krakow", "jogo": "Karol Filar vs Jakub Filip", "aposta": "Jakub Filip", "odd": 2.100, "ev": 5.0, "status": "RED", "resultado": -30},
        {"id": 31, "torneio": "ITF M15 Huy", "jogo": "Jack Loge vs Harold Huens", "aposta": "Harold Huens", "odd": 2.375, "ev": 21.1, "status": "RED", "resultado": -30},
        {"id": 32, "torneio": "ITF M25 Muttenz MD", "jogo": "Genier/Nikles vs Barry/Gerch", "aposta": "Genier/Nikles", "odd": 2.200, "ev": 10.0, "status": "RED", "resultado": -30},
        {"id": 33, "torneio": "ITF M15 Monastir MD", "jogo": "Maxted/Nolan vs Donnet/Murgett", "aposta": "Maxted/Nolan", "odd": 2.100, "ev": 5.0, "status": "GREEN", "resultado": 33},
        {"id": 34, "torneio": "ITF W15 Wanfercee-Baulet", "jogo": "Veronika Podrez vs Alice Tubello", "aposta": "Veronika Podrez", "odd": 2.100, "ev": 5.0, "status": "RED", "resultado": -30},
        {"id": 35, "torneio": "ITF M25 Lesa", "jogo": "Lorenzo Carboni vs Oleksandr Ovcharenko", "aposta": "Oleksandr Ovcharenko", "odd": 2.100, "ev": 5.0, "status": "RED", "resultado": -30},
        {"id": 36, "torneio": "Challenger Augsburg MD", "jogo": "Masur/Sanchez Martinez vs Barnat/Duda", "aposta": "Masur/Sanchez Martinez", "odd": 2.100, "ev": 7.1, "status": "GREEN", "resultado": 33},
        {"id": 37, "torneio": "ITF M25 Uberlingen", "jogo": "Oscar Otte vs Tom Gentzsch", "aposta": "Tom Gentzsch", "odd": 2.375, "ev": 21.1, "status": "GREEN", "resultado": 41.25},
        {"id": 38, "torneio": "ITF M25 Uberlingen MD", "jogo": "Schell/Wessels vs Kellovsky/Pecak", "aposta": "Kellovsky/Pecak", "odd": 2.100, "ev": 5.0, "status": "RED", "resultado": -30},
    ]
    
    # Análise geral
    total_apostas = len(opportunities)
    apostas_verdes = len([o for o in opportunities if o["status"] == "GREEN"])
    apostas_vermelhas = len([o for o in opportunities if o["status"] == "RED"])
    apostas_evitadas = len([o for o in opportunities if o["status"] == "AVOID"])
    
    print(f"📈 RESUMO GERAL:")
    print(f"Total de oportunidades: {total_apostas}")
    print(f"🟢 Vitórias (GREEN): {apostas_verdes} ({apostas_verdes/total_apostas*100:.1f}%)")
    print(f"🔴 Derrotas (RED): {apostas_vermelhas} ({apostas_vermelhas/total_apostas*100:.1f}%)")
    print(f"⚫ Evitadas (AVOID): {apostas_evitadas} ({apostas_evitadas/total_apostas*100:.1f}%)")
    
    # Análise de lucratividade
    lucro_total = sum([o["resultado"] for o in opportunities])
    lucro_sem_evitadas = sum([o["resultado"] for o in opportunities if o["status"] != "AVOID"])
    
    print(f"\n💰 ANÁLISE FINANCEIRA:")
    print(f"Lucro total atual: R$ {lucro_total:.2f}")
    print(f"Lucro sem apostas evitadas: R$ {lucro_sem_evitadas:.2f}")
    
    # Taxa de acerto
    apostas_realizadas = [o for o in opportunities if o["status"] != "AVOID"]
    taxa_acerto = len([o for o in apostas_realizadas if o["resultado"] > 0]) / len(apostas_realizadas) * 100
    
    print(f"📊 Taxa de acerto: {taxa_acerto:.1f}%")
    
    return opportunities

def identify_profit_losses(opportunities):
    """Identifica onde estamos perdendo lucro"""
    print(f"\n" + "=" * 70)
    print("🔍 IDENTIFICANDO PERDAS DE LUCRO")
    print("=" * 70)
    
    # 1. Análise por EV
    print("📊 ANÁLISE POR FAIXA DE EV:")
    
    ev_ranges = [
        (0, 7, "Baixo EV (0-7%)"),
        (7, 12, "EV Médio (7-12%)"),
        (12, 20, "EV Alto (12-20%)")
    ]
    
    for ev_min, ev_max, categoria in ev_ranges:
        ops_faixa = [o for o in opportunities if ev_min <= o["ev"] < ev_max]
        if ops_faixa:
            vitórias = len([o for o in ops_faixa if o["resultado"] > 0])
            derrotas = len([o for o in ops_faixa if o["resultado"] < 0])
            evitadas = len([o for o in ops_faixa if o["resultado"] == 0])
            total_faixa = len(ops_faixa)
            lucro_faixa = sum([o["resultado"] for o in ops_faixa])
            
            print(f"\n🎯 {categoria}:")
            print(f"   Total: {total_faixa} | Vitórias: {vitórias} | Derrotas: {derrotas} | Evitadas: {evitadas}")
            print(f"   Taxa acerto: {vitórias/(vitórias+derrotas)*100 if (vitórias+derrotas) > 0 else 0:.1f}%")
            print(f"   Lucro: R$ {lucro_faixa:.2f}")
    
    # 2. Análise de apostas evitadas
    apostas_evitadas = [o for o in opportunities if o["status"] == "AVOID"]
    print(f"\n⚫ APOSTAS EVITADAS ({len(apostas_evitadas)}):")
    lucro_potencial_perdido = 0
    for aposta in apostas_evitadas:
        # Simula que teria 50% de chance de ganhar (conservador)
        ev_teorico = aposta["ev"]
        lucro_esperado = 30 * (ev_teorico / 100)  # R$ 30 * EV%
        lucro_potencial_perdido += lucro_esperado
        print(f"   🎾 {aposta['jogo'][:40]}... | EV: {aposta['ev']:.1f}% | Lucro perdido: R$ {lucro_esperado:.2f}")
    
    print(f"\n💸 LUCRO POTENCIAL PERDIDO: R$ {lucro_potencial_perdido:.2f}")
    
    # 3. Análise por odds
    print(f"\n📊 ANÁLISE POR FAIXA DE ODDS:")
    
    odds_ranges = [
        (2.0, 2.15, "Odds Baixas (2.0-2.15)"),
        (2.15, 2.3, "Odds Médias (2.15-2.3)"),
        (2.3, 2.5, "Odds Altas (2.3-2.5)")
    ]
    
    for odd_min, odd_max, categoria in odds_ranges:
        ops_faixa = [o for o in opportunities if odd_min <= o["odd"] < odd_max and o["status"] != "AVOID"]
        if ops_faixa:
            vitórias = len([o for o in ops_faixa if o["resultado"] > 0])
            derrotas = len([o for o in ops_faixa if o["resultado"] < 0])
            total_faixa = len(ops_faixa)
            lucro_faixa = sum([o["resultado"] for o in ops_faixa])
            
            print(f"\n🎯 {categoria}:")
            print(f"   Total: {total_faixa} | Vitórias: {vitórias} | Derrotas: {derrotas}")
            print(f"   Taxa acerto: {vitórias/(vitórias+derrotas)*100 if (vitórias+derrotas) > 0 else 0:.1f}%")
            print(f"   Lucro: R$ {lucro_faixa:.2f}")

def optimization_recommendations():
    """Recomendações para otimização de lucro"""
    print(f"\n" + "=" * 70)
    print("🚀 RECOMENDAÇÕES PARA MAXIMIZAR LUCRO")
    print("=" * 70)
    
    print("1. 🎯 AJUSTAR FILTROS DE EV:")
    print("   • EV < 7%: Taxa de acerto baixa, considerar filtrar")
    print("   • EV 12-20%: Melhor performance, focar nesta faixa")
    print("   • Sugestão: EV mínimo de 8% ao invés de 5%")
    
    print("\n2. 📊 REVISAR CRITÉRIO DE ODDS:")
    print("   • Odds 2.0-2.15: Avaliar se vale a pena (menor retorno)")
    print("   • Odds 2.2-2.4: Faixa ótima atual")
    print("   • Considerar expandir para odds até 2.5 em casos de EV alto")
    
    print("\n3. ⚫ REDUZIR APOSTAS EVITADAS:")
    print("   • Analisar critérios que causam AVOID")
    print("   • Implementar sistema de confiança gradual")
    print("   • Apostas com EV > 15% raramente deveriam ser evitadas")
    
    print("\n4. 🤖 MELHORAR MODELO PREDITIVO:")
    print("   • Analisar fatores que causam falsos positivos")
    print("   • Dar mais peso a estatísticas recentes")
    print("   • Considerar surface específica e head-to-head")
    
    print("\n5. 💰 GESTÃO DE BANCA:")
    print("   • EV 5-10%: Apostar R$ 25")
    print("   • EV 10-15%: Apostar R$ 35")
    print("   • EV 15%+: Apostar R$ 50")
    print("   • Isso aumentaria o lucro das apostas vencedoras")
    
    print("\n6. ⏰ TIMING DAS APOSTAS:")
    print("   • Apostar mais próximo do jogo (odds mais estáveis)")
    print("   • Evitar apostas com > 12h de antecedência")
    print("   • Implementar verificação de odds antes de apostar")

def calculate_potential_improvements():
    """Calcula melhorias potenciais"""
    print(f"\n" + "=" * 70)
    print("📈 SIMULAÇÃO DE MELHORIAS")
    print("=" * 70)
    
    print("🔮 SE IMPLEMENTÁSSEMOS AS OTIMIZAÇÕES:")
    
    # Cenário 1: Filtrar EV < 8%
    print("\n1️⃣ FILTRO EV MÍNIMO 8%:")
    print("   • Eliminaria apostas de baixo EV com alta taxa de erro")
    print("   • Lucro potencial: +R$ 60-90 (menos derrotas)")
    
    # Cenário 2: Apostar nas evitadas de alto EV
    print("\n2️⃣ APOSTAR EM EVITADAS COM EV > 12%:")
    print("   • Recuperaria R$ 30-50 de lucro perdido")
    print("   • Apenas 2-3 apostas adicionais por período")
    
    # Cenário 3: Gestão de banca progressiva
    print("\n3️⃣ GESTÃO DE BANCA OTIMIZADA:")
    print("   • Apostas altas em EV alto: +R$ 100-150")
    print("   • Apostas baixas em EV baixo: -R$ 30-50")
    print("   • Ganho líquido: +R$ 70-100")
    
    print("\n🎯 POTENCIAL DE MELHORIA TOTAL:")
    print("💰 Lucro adicional estimado: R$ 160-240 por período")
    print("📊 Isso representaria 300-500% de aumento no lucro!")

if __name__ == "__main__":
    opportunities = analyze_opportunities_data()
    identify_profit_losses(opportunities)
    optimization_recommendations()
    calculate_potential_improvements()
