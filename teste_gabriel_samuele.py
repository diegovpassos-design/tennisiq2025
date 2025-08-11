#!/usr/bin/env python3
"""
Teste específico para Gabriel Ghetu vs Samuele Pieri
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.data.results.resultados import VerificadorResultados

def main():
    verificador = VerificadorResultados()
    
    print("🎾 Testando Gabriel Ghetu vs Samuele Pieri (ID: 10418898)")
    print("=" * 60)
    
    # Buscar a aposta específica
    aposta_teste = None
    for aposta in verificador.historico_apostas:
        if aposta.get('partida_id') == '10418898':
            aposta_teste = aposta
            break
    
    if not aposta_teste:
        print("❌ Aposta não encontrada no histórico!")
        return
    
    print(f"✅ Aposta encontrada:")
    print(f"   ID: {aposta_teste.get('partida_id')}")
    print(f"   Jogador: {aposta_teste.get('jogador_apostado')}")
    print(f"   Oponente: {aposta_teste.get('oponente')}")
    print(f"   Odd: {aposta_teste.get('odd')}")
    print(f"   Status: {aposta_teste.get('status')}")
    
    # Verificar resultado
    print(f"\n🔍 Verificando resultado...")
    resultado = verificador.verificar_resultado_aposta(aposta_teste)
    
    if resultado:
        status = resultado.get('status')
        motivo = resultado.get('motivo', 'N/A')
        vencedor = resultado.get('jogador_winner', 'N/A')
        score = resultado.get('score_string', 'N/A')
        
        print(f"📊 Resultado encontrado:")
        print(f"   Status: {status}")
        print(f"   Motivo: {motivo}")
        print(f"   Vencedor: {vencedor}")
        print(f"   Score: {score}")
        
        if status == 'GREEN':
            print(f"🎉 PARABÉNS! Aposta foi GREEN!")
        elif status == 'RED':
            print(f"😞 Aposta foi RED")
        elif status == 'VOID':
            print(f"⚠️ Aposta foi VOID")
    else:
        print(f"❌ Não foi possível verificar o resultado")

if __name__ == "__main__":
    main()
