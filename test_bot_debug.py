#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TESTE SIMPLES DO BOT - Debug do travamento
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

print("🎾 TennisIQ - Teste de Inicialização")
print("=" * 50)

try:
    print("1. Testando imports básicos...")
    import signal
    import os
    print("✅ Imports básicos OK")
    
    print("2. Testando import do bot...")
    from backend.core.bot import TennisIQBot
    print("✅ Import do bot OK")
    
    print("3. Testando inicialização do bot...")
    bot = TennisIQBot()
    print("✅ Bot inicializado com sucesso!")
    
    print("4. Bot pronto para uso!")
    
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
