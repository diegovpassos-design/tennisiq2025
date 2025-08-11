#!/usr/bin/env python3
"""
Teste da verificação automática usando somente IDs
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.core.bot import TennisIQBot

def main():
    print("🤖 Testando verificação automática do bot (somente por ID):")
    print("=" * 70)
    
    # Criar instância do bot
    bot = TennisIQBot()
    
    if not bot.verificador_resultados:
        print("❌ Verificador de resultados não foi inicializado!")
        return
    
    # Simular verificação automática
    print("🔍 Executando verificação automática...")
    bot.verificar_resultados_automatico()
    
    print("\n✅ Teste de verificação automática concluído!")

if __name__ == "__main__":
    main()
