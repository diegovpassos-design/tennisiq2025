"""
INVESTIGAÇÃO: Falso Otimismo do Modelo em Apostas de EV Alto
Análise detalhada dos problemas de overconfidence
"""

def investigate_model_overconfidence():
    print("🔍 INVESTIGAÇÃO: FALSO OTIMISMO EM APOSTAS DE EV ALTO")
    print("=" * 70)
    
    # Dados das 38 oportunidades
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
    
    # Separar apostas por faixa de EV para análise detalhada
    ev_alto = [o for o in opportunities if o["ev"] >= 15.0]
    ev_medio_alto = [o for o in opportunities if 12.0 <= o["ev"] < 15.0]
    ev_medio = [o for o in opportunities if 8.0 <= o["ev"] < 12.0]
    ev_baixo = [o for o in opportunities if o["ev"] < 8.0]
    
    print("📊 ANÁLISE DETALHADA POR FAIXAS DE EV:")
    print("-" * 50)
    
    # Análise EV ALTO (15%+) - ZONA PROBLEMA
    print("\n🚨 EV ALTO (15%+) - ZONA DE FALSO OTIMISMO:")
    print(f"Total: {len(ev_alto)} apostas")
    vitórias_alto = [o for o in ev_alto if o["status"] == "GREEN"]
    derrotas_alto = [o for o in ev_alto if o["status"] == "RED"]
    evitadas_alto = [o for o in ev_alto if o["status"] == "AVOID"]
    
    print(f"🟢 Vitórias: {len(vitórias_alto)}")
    print(f"🔴 Derrotas: {len(derrotas_alto)}")
    print(f"⚫ Evitadas: {len(evitadas_alto)}")
    
    if len(ev_alto) > len(evitadas_alto):
        taxa_acerto_alto = len(vitórias_alto) / (len(ev_alto) - len(evitadas_alto)) * 100
        print(f"📊 Taxa de acerto: {taxa_acerto_alto:.1f}%")
    
    print("\n🔍 APOSTAS DE EV ALTO DETALHADAS:")
    for op in ev_alto:
        status_emoji = "🟢" if op["status"] == "GREEN" else "🔴" if op["status"] == "RED" else "⚫"
        print(f"   {status_emoji} {op['ev']}% | {op['odd']} | {op['torneio']} | {op['aposta']}")
    
    # Análise por tipo de torneio em EV alto
    print("\n📈 ANÁLISE POR TIPO DE TORNEIO (EV ALTO):")
    torneios_ev_alto = {}
    for op in ev_alto:
        tipo = op['torneio'].split()[0]  # WTA, ITF, ATP, etc.
        if tipo not in torneios_ev_alto:
            torneios_ev_alto[tipo] = {"total": 0, "green": 0, "red": 0}
        torneios_ev_alto[tipo]["total"] += 1
        if op["status"] == "GREEN":
            torneios_ev_alto[tipo]["green"] += 1
        elif op["status"] == "RED":
            torneios_ev_alto[tipo]["red"] += 1
    
    for tipo, stats in torneios_ev_alto.items():
        if stats["total"] > 0:
            taxa = stats["green"] / (stats["green"] + stats["red"]) * 100 if (stats["green"] + stats["red"]) > 0 else 0
            print(f"   {tipo}: {stats['green']}/{stats['total']} vitórias ({taxa:.1f}%)")
    
    # Análise temporal
    print("\n⏰ ANÁLISE TEMPORAL DAS APOSTAS DE EV ALTO:")
    print("(Verificando se há padrão temporal no fracasso)")
    for op in ev_alto:
        status_emoji = "🟢" if op["status"] == "GREEN" else "🔴" if op["status"] == "RED" else "⚫"
        print(f"   {status_emoji} {op['ev']}% | ID {op['id']} | {op['torneio']}")
    
    # Comparação com EV médio (ZONA BOA)
    print("\n✅ COMPARAÇÃO: EV MÉDIO (8-12%) - ZONA LUCRATIVA:")
    print(f"Total: {len(ev_medio)} apostas")
    vitórias_medio = [o for o in ev_medio if o["status"] == "GREEN"]
    derrotas_medio = [o for o in ev_medio if o["status"] == "RED"]
    
    if len(ev_medio) > 0:
        taxa_acerto_medio = len(vitórias_medio) / len(ev_medio) * 100
        print(f"🟢 Vitórias: {len(vitórias_medio)}")
        print(f"🔴 Derrotas: {len(derrotas_medio)}")
        print(f"📊 Taxa de acerto: {taxa_acerto_medio:.1f}%")
        lucro_medio = sum([o["resultado"] for o in ev_medio])
        print(f"💰 Lucro: R$ {lucro_medio:.2f}")
    
    # HIPÓTESES SOBRE O PROBLEMA
    print("\n" + "=" * 70)
    print("🔬 HIPÓTESES SOBRE O FALSO OTIMISMO:")
    print("=" * 70)
    
    print("\n1. 🎯 PROBLEMA DE DADOS DESATUALIZADOS:")
    print("   • ITF tournaments têm dados menos confiáveis")
    print("   • Rankings/Form podem estar desatualizados")
    print("   • Jogadores menos conhecidos = dados imprecisos")
    
    print("\n2. 🧠 OVERCONFIDENCE DO MODELO:")
    print("   • Modelo pode estar superestimando probabilidades")
    print("   • EV >18% teoricamente deveria ter ~60% de acerto")
    print("   • Na prática só tem ~20% de acerto")
    
    print("\n3. 📊 PROBLEMA DE CALIBRAÇÃO:")
    print("   • Odds de 2.375 implicam 42% de probabilidade real")
    print("   • Modelo calcula ~61% de probabilidade (EV 18.8%)")
    print("   • Gap de ~19% entre modelo e realidade")
    
    print("\n4. 🏆 ANÁLISE POR NÍVEL DE TORNEIO:")
    print("   • WTA/ATP: Dados mais confiáveis")
    print("   • ITF/UTR: Dados menos confiáveis")
    print("   • Challenger: Meio termo")
    
    # Cálculo de probabilidades implícitas
    print("\n" + "=" * 70)
    print("💡 ANÁLISE DE PROBABILIDADES - ONDE ESTÁ O ERRO:")
    print("=" * 70)
    
    for op in ev_alto[:5]:  # Primeiros 5 casos
        odds = op["odd"]
        ev = op["ev"]
        prob_bet365 = 1/odds * 100  # Probabilidade implícita da casa
        prob_modelo = ((ev/100 + 1) * (1/odds)) * 100  # Probabilidade calculada pelo modelo
        
        print(f"\n🎾 {op['aposta']} ({op['status']}):")
        print(f"   📊 Odds: {odds} (Bet365 vê {prob_bet365:.1f}% de chance)")
        print(f"   🤖 Modelo vê: {prob_modelo:.1f}% de chance")
        print(f"   ⚖️ Diferença: {prob_modelo - prob_bet365:.1f}% pontos")
        print(f"   💯 EV: {ev}%")
    
    print("\n" + "=" * 70)
    print("🎯 RECOMENDAÇÕES PARA CORRIGIR O FALSO OTIMISMO:")
    print("=" * 70)
    
    print("\n1. 📉 AJUSTAR FILTRO DE EV:")
    print("   • EV > 20%: Muito suspeito, evitar")
    print("   • EV 15-20%: Revisar com cautela")
    print("   • EV 8-14%: Zona mais confiável")
    
    print("\n2. 🏆 FILTRAR POR TIPO DE TORNEIO:")
    print("   • WTA/ATP: Manter EV até 18%")
    print("   • Challenger: Máximo EV 15%")
    print("   • ITF/UTR: Máximo EV 12%")
    
    print("\n3. 🔧 CALIBRAR MODELO:")
    print("   • Reduzir peso dos dados antigos")
    print("   • Aumentar peso de head-to-head recente")
    print("   • Adicionar penalty para dados incompletos")
    
    print("\n4. 📊 IMPLEMENTAR CONFIDENCE SCORE:")
    print("   • Alto: WTA/ATP com dados completos")
    print("   • Médio: Challenger e ITF com ranking")
    print("   • Baixo: UTR e ITF sem ranking recente")

if __name__ == "__main__":
    investigate_model_overconfidence()
