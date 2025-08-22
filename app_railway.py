#!/usr/bin/env python3
"""
TennisQ - Entrada simplificada para Railway
"""

import os
import sys

print("🚀 TennisQ Railway - Iniciando...")
print(f"📁 Diretório atual: {os.getcwd()}")
print(f"📋 Arquivos disponíveis: {os.listdir('.')}")

# Adiciona path do backend
if os.path.exists('backend'):
    sys.path.insert(0, 'backend')
    print("✅ Backend path adicionado")

try:
    # Importa e executa o app principal
    from app import TennisQRailwayApp
    
    print("✅ App importado com sucesso")
    
    # Configura porta do Railway
    port = int(os.environ.get("PORT", 8080))
    
    # Cria e inicia o app
    app = TennisQRailwayApp()
    print(f"🌐 Iniciando servidor na porta {port}")
    app.start()
    
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
    
    # Fallback - servidor Flask simples
    print("🔄 Iniciando servidor fallback...")
    from flask import Flask
    
    fallback_app = Flask(__name__)
    
    @fallback_app.route('/')
    def home():
        return "TennisQ - Sistema temporariamente indisponível"
    
    @fallback_app.route('/health')
    def health():
        return {"status": "error", "message": "Sistema em modo fallback"}
    
    fallback_app.run(host='0.0.0.0', port=port)
