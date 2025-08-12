#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VERIFICAÇÃO PRÉ-DEPLOY: RAILWAY
==============================
Verifica se todos os arquivos estão prontos para deploy no Railway
"""

import os
import sys

def verificar_deploy_railway():
    """
    Verifica se está tudo pronto para deploy no Railway
    """
    print("🚀 VERIFICAÇÃO PRÉ-DEPLOY: RAILWAY")
    print("=" * 50)
    print()
    
    arquivos_obrigatorios = [
        'requirements.txt',
        'Procfile', 
        'railway.json',
        'run_bot.py',
        'run_dashboard.py',
        'backend/core/bot.py',
        'backend/core/detector_alavancagem.py',
        'backend/core/detector_vantagem_mental.py'
    ]
    
    print("📋 Verificando arquivos obrigatórios:")
    todos_presentes = True
    
    for arquivo in arquivos_obrigatorios:
        if os.path.exists(arquivo):
            print(f"   ✅ {arquivo}")
        else:
            print(f"   ❌ {arquivo} - NÃO ENCONTRADO!")
            todos_presentes = False
    
    print()
    
    # Verificar se não há erros de sintaxe nos arquivos principais
    print("🔍 Verificando sintaxe dos arquivos Python:")
    
    arquivos_python = [
        'run_bot.py',
        'run_dashboard.py', 
        'backend/core/bot.py',
        'backend/core/detector_alavancagem.py'
    ]
    
    for arquivo in arquivos_python:
        try:
            with open(arquivo, 'r', encoding='utf-8') as f:
                compile(f.read(), arquivo, 'exec')
            print(f"   ✅ {arquivo} - Sintaxe OK")
        except SyntaxError as e:
            print(f"   ❌ {arquivo} - ERRO DE SINTAXE: {e}")
            todos_presentes = False
        except Exception as e:
            print(f"   ⚠️ {arquivo} - Aviso: {e}")
    
    print()
    
    # Verificar configurações do Railway
    print("⚙️ Verificando configurações do Railway:")
    
    # Procfile
    try:
        with open('Procfile', 'r') as f:
            procfile_content = f.read()
        if 'worker: python run_bot.py' in procfile_content:
            print("   ✅ Procfile - worker configurado corretamente")
        else:
            print("   ❌ Procfile - worker não encontrado")
            todos_presentes = False
            
        if 'web: python run_dashboard.py' in procfile_content:
            print("   ✅ Procfile - web configurado corretamente")  
        else:
            print("   ⚠️ Procfile - web não encontrado (opcional)")
    except Exception as e:
        print(f"   ❌ Erro ao ler Procfile: {e}")
        todos_presentes = False
    
    # Requirements.txt
    try:
        with open('requirements.txt', 'r') as f:
            requirements = f.read()
        deps_essenciais = ['requests', 'flask', 'python-dotenv']
        for dep in deps_essenciais:
            if dep in requirements:
                print(f"   ✅ requirements.txt - {dep} presente")
            else:
                print(f"   ⚠️ requirements.txt - {dep} não encontrado")
    except Exception as e:
        print(f"   ❌ Erro ao ler requirements.txt: {e}")
    
    print()
    
    # Verificar novos arquivos da estratégia de alavancagem
    print("🚀 Verificando arquivos da estratégia de alavancagem:")
    
    arquivos_alavancagem = [
        'backend/core/detector_alavancagem.py',
        'demonstracao_alavancagem.py',
        'ESTRATEGIA_ALAVANCAGEM.md',
        'ALAVANCAGEM_IMPLEMENTADA.md'
    ]
    
    for arquivo in arquivos_alavancagem:
        if os.path.exists(arquivo):
            print(f"   ✅ {arquivo}")
        else:
            print(f"   ⚠️ {arquivo} - Não encontrado (pode ser opcional)")
    
    print()
    
    # Resultado final
    if todos_presentes:
        print("🎉 RESULTADO: PRONTO PARA DEPLOY!")
        print("✅ Todos os arquivos obrigatórios estão presentes")
        print("✅ Sintaxe dos arquivos Python está correta")
        print("✅ Configurações do Railway estão OK")
        print()
        print("📡 COMANDOS PARA DEPLOY NO RAILWAY:")
        print("1. Commit das mudanças:")
        print("   git add .")
        print('   git commit -m "feat: Implementação da estratégia de alavancagem"')
        print("2. Push para o Railway:")
        print("   git push")
        print()
        print("🚀 A estratégia de alavancagem será ativada automaticamente!")
        
    else:
        print("❌ RESULTADO: NÃO PRONTO PARA DEPLOY!")
        print("⚠️ Corrija os problemas listados acima antes do deploy")
    
    print()
    print("💡 DICA: O Railway automaticamente detectará as mudanças")
    print("   e fará o redeploy do bot com a nova estratégia!")

if __name__ == "__main__":
    verificar_deploy_railway()
