#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TennisIQ - Apenas Bot
====================

Executa apenas o bot de monitoramento.
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
    # Detectar se está rodando em produção
    is_production = os.environ.get('RAILWAY_ENVIRONMENT') == 'production'
    
    print("🎾 TennisIQ - Bot de Monitoramento")
    print("=" * 50)
    print("🤖 Iniciando Bot...")
    
    if is_production:
        print("🌐 Rodando em produção na nuvem (Railway)")
    else:
        print("�️ Rodando em desenvolvimento local")
        print("�💡 Pressione Ctrl+C para parar")
    
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
        
        # Em produção, tentar reiniciar automaticamente
        if is_production:
            print("🔄 Tentando reiniciar em 30 segundos...")
            import time
            time.sleep(30)
            main()  # Recursivo para reiniciar

if __name__ == "__main__":
    main()
