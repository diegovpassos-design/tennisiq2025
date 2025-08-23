#!/usr/bin/env python3
"""
Análise das 10 oportunidades enviadas via Telegram
Verifica status atual de cada uma
"""

from datetime import datetime
import pytz

# Lista das 10 oportunidades enviadas via Telegram
telegram_opportunities = [
    {
        "match": "Sorana Cirstea vs Anastasia Zakharova",
        "league": "WTA Cleveland", 
        "target": "Anastasia Zakharova",
        "odd": 2.375,
        "ev": 18.8,
        "date": "22/08",
        "time": "21:30"
    },
    {
        "match": "Scott Jones vs Zane Stevens",
        "league": "UTR Pro Gold Coast",
        "target": "Zane Stevens", 
        "odd": 2.375,
        "ev": 18.8,
        "date": "23/08",
        "time": "00:30"
    },
    {
        "match": "Thantub Suksumrarn vs Markus Malaszszak",
        "league": "ITF M15 Nakhon Pathom",
        "target": "Markus Malaszszak",
        "odd": 2.375, 
        "ev": 18.8,
        "date": "23/08",
        "time": "02:00"
    },
    {
        "match": "Ryotaro Matsumura vs Ryota Tanuma",
        "league": "UTR Pro Yokohama",
        "target": "Ryota Tanuma",
        "odd": 2.25,
        "ev": 12.5,
        "date": "23/08", 
        "time": "01:30"
    },
    {
        "match": "Botic Van De Zandschulp vs Giovanni Mpetshi Perricard",
        "league": "ATP Winston-Salem",
        "target": "Botic Van De Zandschulp",
        "odd": 2.2,
        "ev": 10.0,
        "date": "22/08",
        "time": "22:30"
    },
    {
        "match": "Ann Li vs Xinyu Wang", 
        "league": "WTA Cleveland",
        "target": "Ann Li",
        "odd": 2.2,
        "ev": 10.0,
        "date": "22/08",
        "time": "23:00"
    },
    {
        "match": "Marie Bouzkova vs Ekaterina Alexandrova",
        "league": "WTA Monterrey", 
        "target": "Marie Bouzkova",
        "odd": 2.2,
        "ev": 10.0,
        "date": "23/08",
        "time": "01:30"
    },
    {
        "match": "Patcharin Cheapchandej vs Fangran Tian",
        "league": "ITF W15 Nakhon Pathom",
        "target": "Fangran Tian",
        "odd": 2.2,
        "ev": 10.0,
        "date": "23/08", 
        "time": "02:00"
    },
    {
        "match": "Zachary Cohen vs Sean Ferguson",
        "league": "UTR Pro Waco",
        "target": "Sean Ferguson",
        "odd": 2.1,
        "ev": 5.0,
        "date": "22/08",
        "time": "21:30"
    },
    {
        "match": "Aunchisa Chanta vs Misaki Matsuda",
        "league": "ITF W15 Nakhon Pathom", 
        "target": "Aunchisa Chanta",
        "odd": 2.1,
        "ev": 5.0,
        "date": "23/08",
        "time": "02:00"
    }
]

def analyze_opportunities():
    """Analisa status das oportunidades"""
    now = datetime.now(pytz.UTC)
    
    print("🎾 ANÁLISE DAS 10 OPORTUNIDADES ENVIADAS VIA TELEGRAM")
    print("=" * 60)
    print(f"⏰ Horário atual: {now.strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print()
    
    active_count = 0
    expired_count = 0
    
    for i, opp in enumerate(telegram_opportunities, 1):
        # Constrói datetime do jogo
        if opp["date"] == "22/08":
            game_date = datetime(2025, 8, 22, int(opp["time"][:2]), int(opp["time"][3:]), tzinfo=pytz.UTC)
        else:  # 23/08
            game_date = datetime(2025, 8, 23, int(opp["time"][:2]), int(opp["time"][3:]), tzinfo=pytz.UTC)
        
        # Verifica status
        time_diff = (game_date - now).total_seconds() / 3600  # horas
        
        status = "🔴 EXPIRADO" if time_diff <= 0 else "🟢 ATIVO"
        if time_diff <= 0:
            expired_count += 1
        else:
            active_count += 1
            
        # Mostra informações
        print(f"🎯 OPORTUNIDADE {i} - {status}")
        print(f"   ⚔️ {opp['match']}")
        print(f"   🏆 {opp['league']}")
        print(f"   🎯 {opp['target']} @ {opp['odd']}")
        print(f"   📊 EV: {opp['ev']}%")
        print(f"   📅 {opp['date']} às {opp['time']}")
        
        if time_diff > 0:
            print(f"   ⏰ Tempo restante: {time_diff:.1f}h")
        else:
            print(f"   ⏰ Expirou há: {abs(time_diff):.1f}h")
        print()
    
    print("📊 RESUMO:")
    print(f"🟢 Oportunidades ativas: {active_count}")
    print(f"🔴 Oportunidades expiradas: {expired_count}")
    print(f"📈 Total analisado: {len(telegram_opportunities)}")
    
    print("\n💡 CONCLUSÕES:")
    print(f"• Das {len(telegram_opportunities)} oportunidades enviadas via Telegram")
    print(f"• {active_count} ainda estão dentro do prazo (jogos não começaram)")
    print(f"• {expired_count} expiraram (jogos já começaram)")
    print(f"• A API do dashboard mostra apenas oportunidades ativas")
    
    return active_count, expired_count

if __name__ == "__main__":
    analyze_opportunities()
