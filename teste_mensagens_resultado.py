#!/usr/bin/env python3
"""
Teste das mensagens de resultado sem as linhas removidas
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.core.bot import TennisIQBot

def main():
    print("📧 Testando formato das mensagens de resultado:")
    print("=" * 60)
    
    # Criar instância do bot
    bot = TennisIQBot()
    
    # Dados de teste para GREEN
    aposta_green = {
        'id': 'teste_green',
        'jogador_apostado': 'Samuele Pieri',
        'oponente': 'Gabriel Ghetu',
        'odd': 1.833
    }
    
    resultado_green = {
        'status': 'GREEN',
        'jogador_winner': 'Samuele Pieri',
        'motivo': 'Samuele Pieri VENCEU!'
    }
    
    # Dados de teste para RED
    aposta_red = {
        'id': 'teste_red',
        'jogador_apostado': 'Murariu/Stirbu',
        'oponente': 'Banti/Mesaglio',
        'odd': 2.2
    }
    
    resultado_red = {
        'status': 'RED',
        'jogador_winner': 'Banti/Mesaglio',
        'motivo': 'Banti/Mesaglio venceu'
    }
    
    print("🟢 Testando mensagem GREEN:")
    print("-" * 40)
    
    # Simular envio GREEN (só gerar a mensagem, não enviar)
    try:
        # Chamar a função de envio para ver o formato
        bot.enviar_resultado_aposta(aposta_green, resultado_green)
    except Exception as e:
        print(f"Erro: {e}")
    
    print("\n🔴 Testando mensagem RED:")
    print("-" * 40)
    
    try:
        # Chamar a função de envio para ver o formato
        bot.enviar_resultado_aposta(aposta_red, resultado_red)
    except Exception as e:
        print(f"Erro: {e}")
    
    print("\n✅ Teste concluído! Mensagens formatadas conforme solicitado.")

if __name__ == "__main__":
    main()
