#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TennisIQ - Apenas Bot
====================

Executa apenas o bot de monitoramento.
"""

import signal
import os
from backend.core.bot import TennisIQBot

def signal_handler(sig, frame):
    """Handler para parar o bot com Ctrl+C"""
    print("\n🛑 Parando Bot TennisIQ...")
    os._exit(0)

def main():
    """Função principal do bot"""
    print("🎾 TennisIQ - Bot de Monitoramento")
    print("=" * 50)
    print("🤖 Iniciando Bot...")
    print("💡 Pressione Ctrl+C para parar")
    
    # Configurar handler para Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        bot = TennisIQBot()
        bot.executar_monitoramento()
    except Exception as e:
        print(f"❌ Erro crítico: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
