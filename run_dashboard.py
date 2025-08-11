#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TennisIQ - Apenas Dashboard
===========================

Executa apenas o dashboard web.
"""

from backend.services.dashboard_web import app

if __name__ == "__main__":
    print("🎾 TennisIQ - Dashboard Web")
    print("=" * 50)
    print("🌐 Iniciando Dashboard...")
    print("📊 Acesse: http://localhost:5000")
    print("🔄 Atualizações automáticas a cada 30 segundos")
    print("💡 Pressione Ctrl+C para parar")
    
    app.run(host='0.0.0.0', port=5000, debug=False)
