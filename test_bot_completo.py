#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TESTE DO BOT COMPLETO - Com monitoramento
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

print("🎾 TennisIQ - Teste Completo")
print("=" * 50)

try:
    print("1. Inicializando bot...")
    from backend.core.bot import TennisIQBot
    bot = TennisIQBot()
    print("✅ Bot inicializado!")
    
    print("2. Iniciando monitoramento...")
    bot.executar_monitoramento()
    
except KeyboardInterrupt:
    print("\n🛑 Bot interrompido pelo usuário")
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
