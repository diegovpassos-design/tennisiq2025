"""
Verificar divergência entre odds detectadas pelo sistema e odds reais
"""
import sys
sys.path.append('backend')
from core.prelive_scanner import PreLiveScanner
import json

def check_odds_divergence():
    # Carregar config
    with open('backend/config/config.json', 'r') as f:
        config = json.load(f)

    scanner = PreLiveScanner(config['api_key'], config['api_base_url'])

    # Buscar odds atuais para este jogo específico
    print('🔍 Verificando odds atuais para Britt Du Pree vs Alice Gillan...')
    events = scanner.get_upcoming_events(hours_ahead=72)

    # Procurar o jogo Britt Du Pree vs Alice Gillan
    found = False
    for event in events:
        home = event.home
        away = event.away
        
        if ('Britt Du Pree' in home or 'Alice Gillan' in away or 
            'Britt Du Pree' in away or 'Alice Gillan' in home or
            'Britt' in home or 'Alice' in away or 'Gillan' in away):
            
            print(f'🎾 JOGO ENCONTRADO:')
            print(f'   📅 ID: {event.event_id}')
            print(f'   🏠 Home: {home}')
            print(f'   ✈️ Away: {away}')
            print(f'   ⏰ Start: {event.start_utc}')
            
            # Buscar odds
            odds = scanner.get_event_odds(event.event_id)
            if odds:
                print(f'   💰 Odds atuais via API: Home {odds.home_od} | Away {odds.away_od}')
                print(f'   🎯 Sistema detectou: Home 2.20 | Away 1.61')
                print(f'   🌐 Bet365 mostra: Home 1.90 | Away 1.80')
                
                # Analisar a divergência
                api_home = odds.home_od
                api_away = odds.away_od
                
                if api_home == 2.20 and api_away == 1.61:
                    print('   ✅ API confirma odds do sistema')
                elif api_home == 1.90 and api_away == 1.80:
                    print('   ⚠️ API mudou para odds da Bet365')
                else:
                    print(f'   🔄 API mostra odds diferentes: {api_home} | {api_away}')
                    
            else:
                print(f'   ❌ Odds não encontradas via API')
            
            found = True
            print()
    
    if not found:
        print('❌ Jogo não encontrado nos próximos eventos')
        print('\n📋 Primeiros 5 jogos encontrados:')
        for i, event in enumerate(events[:5]):
            print(f'   {i+1}. {event.home} vs {event.away}')

if __name__ == "__main__":
    check_odds_divergence()
