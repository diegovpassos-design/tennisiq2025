"""
INVESTIGAÇÃO: Limitação de 50 jogos na API B365
Testa se é limitação da API ou configuração nossa
"""

import sys
import os
sys.path.append('backend')

import requests
import json
from datetime import datetime, timedelta

def investigate_api_limit():
    print("🔍 INVESTIGAÇÃO: LIMITAÇÃO DE 50 JOGOS")
    print("=" * 60)
    
    print("\n📋 HIPÓTESES A TESTAR:")
    print("1. API B365 tem limite de 50 resultados por request")
    print("2. Nosso código está limitando a 50 jogos")
    print("3. Parâmetro de paginação missing")
    print("4. Filtro de tempo reduzindo resultados")
    
    print("\n" + "=" * 60)
    print("🔍 ANÁLISE DO CÓDIGO ATUAL:")
    print("=" * 60)
    
    print("\n📝 CÓDIGO EM prelive_scanner.py:")
    print("-" * 40)
    print("get_upcoming_events() → sem limite no nosso código")
    print("params = {'sport_id': 13, 'token': token}")
    print("→ NÃO há parâmetro 'limit' ou 'max_results'")
    print("→ NÃO há paginação implementada")
    
    print("\n📊 PROCESSAMENTO DOS RESULTADOS:")
    print("events = data.get('results', [])")
    print("→ Processa TODOS os eventos retornados")
    print("→ Filtra apenas por tempo (hours_ahead)")
    print("→ NÃO há limite de quantidade")
    
    print("\n" + "=" * 60)
    print("🌐 DOCUMENTAÇÃO API B365:")
    print("=" * 60)
    
    print("\n📚 PARÂMETROS CONHECIDOS:")
    print("• sport_id: ID do esporte (13 = tênis)")
    print("• token: Token de autenticação")
    print("• day: Filtro por dia específico")
    print("• cc: Código do país")
    
    print("\n❓ PARÂMETROS POSSÍVEIS (não testados):")
    print("• limit: Número máximo de resultados")
    print("• page: Página para paginação")
    print("• max_results: Limite máximo")
    print("• offset: Deslocamento para paginação")
    
    print("\n" + "=" * 60)
    print("🧪 TESTE PRÁTICO:")
    print("=" * 60)
    
    print("\n🔧 VAMOS TESTAR DIFERENTES PARÂMETROS:")
    
    # Simula diferentes chamadas para testar
    test_scenarios = [
        {
            "name": "Padrão atual",
            "params": {"sport_id": 13, "token": "FAKE_TOKEN"},
            "description": "Sem parâmetros extras"
        },
        {
            "name": "Com limit=100",
            "params": {"sport_id": 13, "token": "FAKE_TOKEN", "limit": 100},
            "description": "Tentativa de aumentar limite"
        },
        {
            "name": "Com max_results=200",
            "params": {"sport_id": 13, "token": "FAKE_TOKEN", "max_results": 200},
            "description": "Outro parâmetro de limite"
        },
        {
            "name": "Com day=today",
            "params": {"sport_id": 13, "token": "FAKE_TOKEN", "day": "today"},
            "description": "Filtro específico por dia"
        },
        {
            "name": "Com paginação",
            "params": {"sport_id": 13, "token": "FAKE_TOKEN", "page": 1, "limit": 50},
            "description": "Teste de paginação"
        }
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n{i}. {scenario['name']}:")
        print(f"   📝 {scenario['description']}")
        print(f"   🔗 Parâmetros: {scenario['params']}")
        print(f"   💡 Para testar: adicionar estes params na request")
    
    print("\n" + "=" * 60)
    print("📊 ANÁLISE DOS LOGS:")
    print("=" * 60)
    
    print("\n🔍 O QUE VERIFICAR NOS LOGS:")
    print("• 'Encontrados X jogos nas próximas Yh'")
    print("• Se sempre para em ~50 jogos")
    print("• Se varia por horário/dia")
    print("• Se API retorna exatamente 50 ou nosso filtro limita")
    
    print("\n📈 PADRÕES ESPERADOS:")
    print("• Se API limita: sempre ~50 resultados")
    print("• Se nosso filtro: varia conforme horário")
    print("• Se temporal: mais jogos em fins de semana")
    
    print("\n" + "=" * 60)
    print("🛠️ SOLUÇÕES POSSÍVEIS:")
    print("=" * 60)
    
    print("\n💡 SE FOR LIMITAÇÃO DA API:")
    print("1. Implementar paginação")
    print("2. Fazer múltiplas requests por dia")
    print("3. Usar parâmetros de limite (limit, max_results)")
    print("4. Filtrar por liga/região específica")
    
    print("\n💡 SE FOR NOSSO CÓDIGO:")
    print("1. Verificar filtros desnecessários")
    print("2. Aumentar hours_ahead")
    print("3. Revisar lógica de processamento")
    
    print("\n" + "=" * 60)
    print("🎯 IMPLEMENTAÇÃO SUGERIDA:")
    print("=" * 60)
    
    print("\n🔧 TESTE COM PAGINAÇÃO:")
    print("""
def get_upcoming_events_paginated(self, hours_ahead: int = 48):
    all_matches = []
    page = 1
    max_pages = 5  # Limite de segurança
    
    while page <= max_pages:
        params = {
            "sport_id": self.sport_id_tennis,
            "token": self.api_token,
            "page": page,
            "limit": 100  # Tenta limite maior
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        events = data.get("results", [])
        
        if not events:  # Sem mais resultados
            break
            
        # Processa eventos desta página
        matches_this_page = self.process_events(events, hours_ahead)
        all_matches.extend(matches_this_page)
        
        logger.info(f"Página {page}: {len(events)} eventos, {len(matches_this_page)} válidos")
        page += 1
    
    return all_matches
""")
    
    print("\n🎯 TESTE MANUAL RECOMENDADO:")
    print("1. Fazer request direto na API com diferentes params")
    print("2. Contar quantos eventos retorna")
    print("3. Testar parâmetros limit/page/max_results")
    print("4. Verificar se API documenta limites")
    
    print("\n🔍 QUER QUE EU IMPLEMENTE O TESTE?")
    print("Posso criar versão com paginação para testar se resolve")

if __name__ == "__main__":
    investigate_api_limit()
