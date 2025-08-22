#!/usr/bin/env python3
"""
TennisQ - Sistema de Oportunidades Pré-Live de Tênis
Arquivo principal de execução do bot

Autor: Diego Viana
Data: 2025-08-22
Versão: 1.0
"""

import os
import sys
import logging
import signal
from pathlib import Path

# Adiciona o path do backend ao Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

def setup_logging():
    """Configura sistema de logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('storage/logs/system/tennisq.log', mode='a')
        ]
    )

def check_requirements():
    """Verifica se todos os requisitos estão instalados"""
    try:
        import requests
        import sqlite3
        import flask
        print("✅ Dependências verificadas com sucesso")
        return True
    except ImportError as e:
        print(f"❌ Dependência faltando: {e}")
        print("Execute: pip install -r requirements.txt")
        return False

def check_config():
    """Verifica se a configuração está presente"""
    config_path = "backend/config/config.json"
    if not os.path.exists(config_path):
        print(f"❌ Arquivo de configuração não encontrado: {config_path}")
        return False
    
    try:
        import json
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        required_keys = ["api_key", "telegram_token", "chat_id", "api_base_url"]
        for key in required_keys:
            if key not in config or not config[key]:
                print(f"❌ Configuração '{key}' está faltando")
                return False
        
        print("✅ Configuração verificada com sucesso")
        return True
    except Exception as e:
        print(f"❌ Erro ao verificar configuração: {e}")
        return False

def create_directories():
    """Cria diretórios necessários se não existirem"""
    directories = [
        "storage/database",
        "storage/logs/system",
        "storage/exports"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    print("✅ Diretórios criados/verificados")

def main():
    """Função principal"""
    print("🎾 TENNISQ - SISTEMA DE OPORTUNIDADES PRÉ-LIVE")
    print("=" * 60)
    
    # Verificações pré-execução
    print("🔍 Verificando sistema...")
    
    if not check_requirements():
        sys.exit(1)
    
    if not check_config():
        sys.exit(1)
    
    create_directories()
    setup_logging()
    
    # Importa e inicia o sistema
    try:
        from app import TennisQRailwayApp
        
        print("🚀 Iniciando TennisQ...")
        app = TennisQRailwayApp()
        
        # Handler para parada graceful
        def signal_handler(signum, frame):
            print("\\n🛑 Parando sistema...")
            app.stop()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Inicia o sistema
        app.start()
        
    except KeyboardInterrupt:
        print("\\n🛑 Sistema interrompido pelo usuário")
    except Exception as e:
        print(f"❌ Erro crítico: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
