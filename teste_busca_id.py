#!/usr/bin/env python3
"""
Teste da busca por ID específico
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.data.results.resultados import VerificadorResultados

def main():
    verificador = VerificadorResultados()
    
    # Testar IDs específicos do histórico
    ids_teste = ["10418898", "10422469", "10419025"]
    
    print("🔍 Testando busca por ID específico:")
    print("=" * 50)
    
    for partida_id in ids_teste:
        print(f"\n📊 Testando ID: {partida_id}")
        resultado = verificador.buscar_resultado_por_id(partida_id)
        
        if resultado:
            if resultado.get('partida_terminada'):
                print(f"✅ Partida finalizada:")
                print(f"   Home: {resultado.get('home_team', 'N/A')}")
                print(f"   Away: {resultado.get('away_team', 'N/A')}")
                print(f"   Vencedor: {resultado.get('vencedor', 'N/A')}")
                print(f"   Score: {resultado.get('ss', 'N/A')}")
            else:
                print(f"⏳ Partida em andamento:")
                print(f"   Status: {resultado.get('status', 'N/A')}")
                print(f"   Home: {resultado.get('home_team', 'N/A')}")
                print(f"   Away: {resultado.get('away_team', 'N/A')}")
        else:
            print(f"❌ ID {partida_id} não foi encontrado na API de dados")
        
        print("-" * 40)

if __name__ == "__main__":
    main()
