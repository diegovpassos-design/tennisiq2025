#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TennisIQ - Bot Simples (sem Dashboard)
=====================================

Executa apenas o bot de monitoramento sem carregar dashboard.
"""

import signal
import sys
import os

def signal_handler(sig, frame):
    """Handler para parar o bot com Ctrl+C"""
    print("\n🛑 Parando Bot TennisIQ...")
    sys.exit(0)

def main():
    """Função principal do bot"""
    print("🎾 TennisIQ - Bot de Monitoramento (Modo Simples)")
    print("=" * 60)
    print("🤖 Iniciando Bot...")
    print("💡 Pressione Ctrl+C para parar")
    
    # Configurar handler para Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # Importar só quando necessário para evitar travamentos
        sys.path.append(os.path.dirname(__file__))
        from backend.core.bot import TennisIQBot
        
        print("✅ Imports carregados")
        bot = TennisIQBot()
        print("✅ Bot inicializado")
        
        print("🚀 Iniciando monitoramento...")
        bot.executar_monitoramento()
        
    except KeyboardInterrupt:
        print("\n🛑 Bot interrompido pelo usuário")
    except Exception as e:
        print(f"❌ Erro crítico: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
