#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TennisIQ - Apenas Dashboard
===========================

Executa apenas o dashboard web.
"""

import os
from backend.services.dashboard_web import app

if __name__ == "__main__":
    # Configuração para produção (Railway)
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    
    print("🎾 TennisIQ - Dashboard Web")
    print("=" * 50)
    print("🌐 Iniciando Dashboard...")
    
    if debug_mode:
        print("📊 Acesse: http://localhost:5000")
    else:
        print("📊 Rodando em produção na nuvem")
        
    print("🔄 Atualizações automáticas a cada 30 segundos")
    print("💡 Pressione Ctrl+C para parar")
    
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
