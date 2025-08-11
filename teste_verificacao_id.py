#!/usr/bin/env python3
"""
Teste da verificação de resultados com ID
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.data.results.resultados import VerificadorResultados
import json

def main():
    verificador = VerificadorResultados()
    
    print("🔍 Testando verificação completa de apostas por ID:")
    print("=" * 60)
    
    # Carregar apostas do histórico
    apostas_teste = verificador.historico_apostas
    
    # Filtrar apenas apostas pendentes que têm ID
    apostas_com_id = [a for a in apostas_teste 
                      if a.get('status') == 'PENDENTE' 
                      and a.get('partida_id')
                      and a['partida_id'].isdigit()]
    
    print(f"📊 Encontradas {len(apostas_com_id)} apostas pendentes com ID válido")
    
    if not apostas_com_id:
        print("❌ Nenhuma aposta pendente com ID encontrada!")
        return
    
    # Testar algumas apostas
    for i, aposta in enumerate(apostas_com_id[:3]):  # Testar apenas 3 primeiras
        print(f"\n🎾 Aposta {i+1}:")
        print(f"   ID: {aposta.get('partida_id', 'N/A')}")
        print(f"   Jogador: {aposta.get('jogador_apostado', 'N/A')}")
        print(f"   Oponente: {aposta.get('oponente', 'N/A')}")
        print(f"   Data: {aposta.get('timestamp', 'N/A')}")
        
        # Verificar resultado
        resultado = verificador.verificar_resultado_aposta(aposta)
        
        if resultado:
            status = resultado.get('status', 'ERRO')
            motivo = resultado.get('motivo', 'N/A')
            
            if status == 'GREEN':
                print(f"   ✅ Resultado: {status} - {motivo}")
            elif status == 'RED':
                print(f"   ❌ Resultado: {status} - {motivo}")
            elif status == 'VOID':
                print(f"   ⚠️ Resultado: {status} - {motivo}")
            elif status == 'PENDENTE':
                print(f"   ⏳ Resultado: {status} - {motivo}")
            else:
                print(f"   🔴 Resultado: {status} - {motivo}")
                
            if resultado.get('jogador_winner'):
                print(f"   🏆 Vencedor: {resultado.get('jogador_winner')}")
                
            if resultado.get('score_string'):
                print(f"   📊 Score: {resultado.get('score_string')}")
        else:
            print(f"   ❌ Erro: Não foi possível verificar resultado")
        
        print("-" * 40)

if __name__ == "__main__":
    main()
