#!/usr/bin/env python3
"""
Arquivo de redirecionamento temporário
O Railway está tentando executar este arquivo, então vamos redirecionar para server.py
"""

import subprocess
import sys

if __name__ == "__main__":
    # Executa o server.py
    subprocess.run([sys.executable, "server.py"])
