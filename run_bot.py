#!/usr/bin/env python3
# Redirecionamento para o sistema correto no backend

import os
import sys

# Adiciona path do backend
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Executar app principal do backend
if __name__ == "__main__":
    from app import main
    main()