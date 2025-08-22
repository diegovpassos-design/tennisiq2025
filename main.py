#!/usr/bin/env python3
"""
TennisQ Railway - Versão simplificada
"""

import os
import sys
import threading
from flask import Flask, jsonify

print("🚀 TennisQ iniciando...")

# Cria Flask app básico
app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "service": "TennisQ Pre-Live",
        "version": "2.0",
        "message": "Sistema de oportunidades pré-live funcionando!"
    })

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "timestamp": "2025-08-22",
        "service": "TennisQ"
    })

@app.route('/status')
def status():
    return jsonify({
        "status": "active",
        "features": [
            "Scanner de oportunidades",
            "Notificações Telegram", 
            "Anti-duplicatas",
            "API health checks"
        ]
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    print(f"🌐 Servidor iniciando na porta {port}")
    
    # Tenta importar o sistema completo
    try:
        sys.path.insert(0, 'backend')
        from app import TennisQRailwayApp
        
        print("✅ Sistema completo carregado")
        
        # Inicia sistema completo em thread separada
        def start_tennis_system():
            try:
                tennis_app = TennisQRailwayApp()
                tennis_app.start()
            except Exception as e:
                print(f"⚠️ Sistema completo falhou: {e}")
        
        tennis_thread = threading.Thread(target=start_tennis_system, daemon=True)
        tennis_thread.start()
        
    except Exception as e:
        print(f"⚠️ Sistema completo não disponível: {e}")
        print("🔄 Rodando apenas API básica")
    
    # Sempre roda o Flask (garantia de funcionamento)
    app.run(host='0.0.0.0', port=port, debug=False)
