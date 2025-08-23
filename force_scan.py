from backend.core.prelive_scanner import PreLiveScanner
from backend.core.tennis_model import SophisticatedTennisModel
from backend.core.database import PreLiveDatabase
import logging
import json

# Configurar logging para ver o que acontece
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print('🔍 FORÇANDO SCAN MANUAL DE OPORTUNIDADES...\n')

# Carregar configuração
try:
    with open('backend/config/config.json', 'r') as f:
        config = json.load(f)
    api_token = config["api_key"]
    api_base = config["api_base_url"]
    print(f'✅ Config carregada: {api_base}')
    print(f'🔑 API Key: {api_token[:10]}...')
except Exception as e:
    print(f'❌ Erro carregando config: {e}')
    # Usar valores padrão
    api_token = "138-kQv5ogQbxPKhgC"
    api_base = "https://api.b365api.com"
    print(f'🔄 Usando config padrão: {api_base}')

# Criar componentes
db = PreLiveDatabase()
scanner = PreLiveScanner(api_token=api_token, api_base=api_base)

# Executar scan
try:
    print('📡 Iniciando scan...')
    opportunities = scanner.scan_opportunities(
        hours_ahead=72,
        min_ev=0.005,  # EV mínimo de 0.5%
        odd_min=1.80,
        odd_max=2.40
    )
    
    print(f'📊 Encontradas: {len(opportunities) if opportunities else 0} oportunidades')
    
    if opportunities:
        # Mostrar detalhes
        for i, opp in enumerate(opportunities[:5], 1):
            print(f'  {i}. {opp.match_name} ({opp.side}) - EV: {opp.ev:.3f} - Odd: {opp.odd:.2f}')
        
        # Salvar
        saved = db.save_opportunities(opportunities)
        print(f'💾 Salvas: {saved} novas oportunidades')
    else:
        print('📭 Nenhuma oportunidade encontrada')
        
except Exception as e:
    print(f'❌ Erro no scan: {e}')
    import traceback
    traceback.print_exc()
