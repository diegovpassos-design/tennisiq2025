#!/usr/bin/env python3
"""
Script para forçar redeploy no Railway com as melhorias
"""

import subprocess
import sys
import time

def run_command(command, description):
    """Executa comando e trata erros"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - Sucesso!")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()}")
        else:
            print(f"❌ {description} - Erro:")
            print(f"   {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ Erro ao executar '{command}': {e}")
        return False
    return True

def main():
    """Função principal"""
    print("🚀 FORÇANDO REDEPLOY DO TENNISQ")
    print("=" * 50)
    
    # Lista de comandos para redeploy
    commands = [
        ("git add .", "Adicionando arquivos modificados"),
        ("git commit -m 'fix: melhorias nos logs e health checks para resolver travamentos'", "Commitando melhorias"),
        ("git push origin main", "Enviando para GitHub (redeploy automático)")
    ]
    
    # Executa comandos
    for command, description in commands:
        if not run_command(command, description):
            print(f"\n❌ Falha em: {description}")
            return False
        time.sleep(1)
    
    print("\n🎉 REDEPLOY INICIADO!")
    print("🔍 Verifique o Railway em alguns minutos")
    print("📊 Os novos logs devem aparecer com mais detalhes")
    
    return True

if __name__ == "__main__":
    main()
