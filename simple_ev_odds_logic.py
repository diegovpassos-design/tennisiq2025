"""
MODELO SIMPLIFICADO: APENAS EV + ODDS
Lógica que usa somente EV e Odds como parâmetros de decisão
"""

def simple_ev_odds_logic():
    print("🎯 MODELO SIMPLIFICADO: APENAS EV + ODDS")
    print("=" * 60)
    
    print("\n📋 CONCEITO:")
    print("Usar apenas Expected Value (EV) e range de odds para decidir apostas")
    print("SEM considerar: confidence, tipo de torneio, dados dos jogadores")
    
    print("\n🔧 LÓGICA PROPOSTA:")
    print("=" * 40)
    
    print("\n1️⃣ FILTRO POR ODDS:")
    print("• Odds mínimas: 1.80 (probabilidade máxima 55.6%)")
    print("• Odds máximas: 2.50 (probabilidade mínima 40.0%)")
    print("• Razão: Evita favoritos demais e azarões demais")
    
    print("\n2️⃣ FILTRO POR EV:")
    print("• EV mínimo: 5.0%")
    print("• EV máximo: 20.0%")
    print("• Razão: EV muito baixo = pouco lucro, EV muito alto = suspeito")
    
    print("\n3️⃣ FAIXAS DE EV RECOMENDADAS:")
    print("• EV 5-8%: Conservador (alta probabilidade de acerto)")
    print("• EV 8-12%: Moderado (boa relação risco/retorno)")
    print("• EV 12-20%: Agressivo (maior retorno, maior risco)")
    
    print("\n" + "=" * 60)
    print("💻 IMPLEMENTAÇÃO DE CÓDIGO:")
    print("=" * 60)
    
    print("\n```python")
    print("def should_bet_simple(ev: float, odds: float) -> bool:")
    print('    """')
    print("    Decide se deve apostar baseado APENAS em EV e odds")
    print("    ")
    print("    Args:")
    print("        ev: Expected Value em decimal (ex: 0.08 = 8%)")
    print("        odds: Odds da aposta (ex: 2.20)")
    print("    ")
    print("    Returns:")
    print("        True se deve apostar, False caso contrário")
    print('    """')
    print("    # Filtro 1: Range de odds")
    print("    if odds < 1.80 or odds > 2.50:")
    print("        return False")
    print("    ")
    print("    # Filtro 2: Range de EV")
    print("    if ev < 0.05 or ev > 0.20:")
    print("        return False")
    print("    ")
    print("    # Filtro 3: EV mínimo progressivo baseado em odds")
    print("    if odds <= 2.00:")
    print("        min_ev_required = 0.08  # 8% para odds baixas")
    print("    elif odds <= 2.20:")
    print("        min_ev_required = 0.06  # 6% para odds médias")
    print("    else:")
    print("        min_ev_required = 0.05  # 5% para odds altas")
    print("    ")
    print("    return ev >= min_ev_required")
    print("```")
    
    print("\n" + "=" * 60)
    print("📊 VERSÕES DA LÓGICA:")
    print("=" * 60)
    
    print("\n🔥 VERSÃO ULTRACONSERVADORA:")
    print("```python")
    print("def ultra_conservative(ev: float, odds: float) -> bool:")
    print("    return (1.90 <= odds <= 2.30) and (0.08 <= ev <= 0.12)")
    print("```")
    print("• Apenas odds 1.90-2.30 e EV 8-12%")
    print("• Máxima segurança, pouquíssimas apostas")
    
    print("\n⚖️ VERSÃO EQUILIBRADA:")
    print("```python")
    print("def balanced(ev: float, odds: float) -> bool:")
    print("    return (1.80 <= odds <= 2.50) and (0.05 <= ev <= 0.15)")
    print("```")
    print("• Odds 1.80-2.50 e EV 5-15%")
    print("• Boa relação entre segurança e oportunidades")
    
    print("\n🚀 VERSÃO AGRESSIVA:")
    print("```python")
    print("def aggressive(ev: float, odds: float) -> bool:")
    print("    return (1.70 <= odds <= 3.00) and (0.03 <= ev <= 0.25)")
    print("```")
    print("• Odds 1.70-3.00 e EV 3-25%")
    print("• Mais oportunidades, maior risco")
    
    print("\n" + "=" * 60)
    print("🧮 SIMULAÇÃO COM SEUS DADOS:")
    print("=" * 60)
    
    # Simula com dados das 38 oportunidades
    opportunities = [
        {"id": 1, "ev": 18.8, "odds": 2.375, "result": "RED"},
        {"id": 2, "ev": 5.0, "odds": 2.100, "result": "RED"},
        {"id": 3, "ev": 10.0, "odds": 2.200, "result": "GREEN"},
        {"id": 4, "ev": 10.0, "odds": 2.200, "result": "GREEN"},
        {"id": 5, "ev": 18.8, "odds": 2.375, "result": "AVOID"},
        {"id": 8, "ev": 18.8, "odds": 2.375, "result": "GREEN"},
        {"id": 15, "ev": 18.8, "odds": 2.375, "result": "RED"},
        {"id": 26, "ev": 21.1, "odds": 2.375, "result": "GREEN"},
        {"id": 31, "ev": 21.1, "odds": 2.375, "result": "RED"},
        {"id": 37, "ev": 21.1, "odds": 2.375, "result": "GREEN"}
    ]
    
    def should_bet_conservative(ev, odds):
        return (1.90 <= odds <= 2.30) and (0.08 <= ev <= 0.12)
    
    def should_bet_balanced(ev, odds):
        return (1.80 <= odds <= 2.50) and (0.05 <= ev <= 0.15)
    
    def should_bet_aggressive(ev, odds):
        return (1.70 <= odds <= 3.00) and (0.03 <= ev <= 0.25)
    
    print("\n📊 RESULTADOS DA SIMULAÇÃO:")
    
    for version_name, bet_function in [
        ("ULTRACONSERVADORA", should_bet_conservative),
        ("EQUILIBRADA", should_bet_balanced), 
        ("AGRESSIVA", should_bet_aggressive)
    ]:
        print(f"\n🎯 VERSÃO {version_name}:")
        
        accepted = []
        rejected = []
        
        for opp in opportunities:
            ev_decimal = opp["ev"] / 100.0
            if bet_function(ev_decimal, opp["odds"]):
                accepted.append(opp)
            else:
                rejected.append(opp)
        
        print(f"   Apostas aceitas: {len(accepted)}")
        print(f"   Apostas rejeitadas: {len(rejected)}")
        
        if accepted:
            green_count = len([o for o in accepted if o["result"] == "GREEN"])
            red_count = len([o for o in accepted if o["result"] == "RED"])
            avoid_count = len([o for o in accepted if o["result"] == "AVOID"])
            
            if (green_count + red_count) > 0:
                success_rate = green_count / (green_count + red_count) * 100
                print(f"   Taxa de acerto: {success_rate:.1f}%")
            
            print(f"   Distribuição: {green_count} GREEN, {red_count} RED, {avoid_count} AVOID")
            
            # Lista as apostas aceitas
            print("   Apostas aceitas:")
            for opp in accepted:
                print(f"     • EV {opp['ev']:.1f}%, Odds {opp['odds']}, {opp['result']}")
    
    print("\n" + "=" * 60)
    print("🔧 IMPLEMENTAÇÃO NO SEU CÓDIGO:")
    print("=" * 60)
    
    print("\n📝 MODIFICAÇÃO EM prelive_scanner.py:")
    print("```python")
    print("def _should_bet_simple(self, ev: float, odds: float) -> bool:")
    print('    """Lógica simplificada: apenas EV + odds"""')
    print("    # Escolha UMA das versões:")
    print("    ")
    print("    # VERSÃO ULTRACONSERVADORA")
    print("    return (1.90 <= odds <= 2.30) and (0.08 <= ev <= 0.12)")
    print("    ")
    print("    # OU VERSÃO EQUILIBRADA")
    print("    # return (1.80 <= odds <= 2.50) and (0.05 <= ev <= 0.15)")
    print("    ")
    print("    # OU VERSÃO AGRESSIVA")
    print("    # return (1.70 <= odds <= 3.00) and (0.03 <= ev <= 0.25)")
    print("```")
    
    print("\n📝 SUBSTITUIR A CHAMADA:")
    print("```python")
    print("# ANTES:")
    print("if self._should_bet_based_on_confidence(ev_home, confidence, match.league):")
    print("    # aceita aposta")
    print("")
    print("# DEPOIS:")
    print("if self._should_bet_simple(ev_home, odds_data.home_od):")
    print("    # aceita aposta")
    print("```")
    
    print("\n" + "=" * 60)
    print("🎯 RECOMENDAÇÃO:")
    print("=" * 60)
    
    print("\n🏆 PARA VOCÊ, RECOMENDO A VERSÃO EQUILIBRADA:")
    print("• Odds: 1.80 - 2.50")
    print("• EV: 5% - 15%")
    print("• Motivos:")
    print("  - Elimina EVs muito altos (20%+) que são suspeitos")
    print("  - Mantém faixa de odds testada e funcional")
    print("  - Permite EV até 15% que ainda é realístico")
    print("  - Deve capturar ~60% das suas oportunidades reais")
    
    print("\n💡 VANTAGENS DA LÓGICA SIMPLES:")
    print("• Transparente e fácil de entender")
    print("• Sem dependência de dados externos")
    print("• Foco apenas no que importa: EV e odds")
    print("• Elimina complexity desnecessária")
    
    print("\n⚠️ DESVANTAGENS:")
    print("• Pode aceitar apostas com dados ruins")
    print("• Não diferencia WTA de ITF")
    print("• Menos sofisticado que filtro de confidence")
    
    print("\n🎯 IMPLEMENTAR?")
    print("Esta lógica pode ser implementada substituindo")
    print("o filtro de confidence atual por esta versão simples.")

if __name__ == "__main__":
    simple_ev_odds_logic()
