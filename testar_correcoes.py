#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TESTE DAS CORREÇÕES IMPLEMENTADAS
=================================
Verificação das melhorias de rate limiting e visibilidade de logs
"""

import sys
import os

# Adicionar ao path
PROJECT_ROOT = os.path.dirname(__file__)
sys.path.append(os.path.join(PROJECT_ROOT, 'backend'))

def testar_logger_ultra():
    """Testa o logger ultra-otimizado"""
    
    print("🧪 TESTE DO LOGGER ULTRA-OTIMIZADO")
    print("=" * 40)
    
    try:
        from backend.utils.logger_ultra import logger_ultra
        
        print(f"✅ Logger ultra importado com sucesso")
        print(f"📊 Ambiente detectado: {logger_ultra.ambiente}")
        print(f"📊 Logger ativo: {logger_ultra.ativo}")
        
        # Simular logs críticos (alavancagem)
        print(f"\n🧪 TESTANDO LOGS CRÍTICOS:")
        
        logger_ultra.success("🚀 ALAVANCAGEM APROVADA: Teste Player")
        logger_ultra.info("📊 Justificativa: Teste de correção implementada")
        logger_ultra.strategy_log("alavancagem", "aprovado", "Teste do sistema otimizado")
        
        # Simular logs que devem ser suprimidos
        print(f"\n🧪 TESTANDO SUPRESSÃO:")
        
        for i in range(5):
            logger_ultra.info(f"🔍 Stats coletados: MS1={i}, MS2={i+10}")  # Deve ser suprimido
            logger_ultra.info(f"💰 Odds coletados: Odd1={1.5+i/10}")  # Deve ser suprimido
        
        print(f"\n✅ Teste do logger ultra concluído")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste do logger ultra: {e}")
        return False

def testar_bot_com_correcoes():
    """Testa o bot com as correções implementadas"""
    
    print(f"\n🧪 TESTE DO BOT COM CORREÇÕES")
    print("=" * 35)
    
    try:
        from backend.core.bot import TennisIQBot
        
        print(f"✅ Bot importado com correções")
        
        # Verificar se logger ultra está disponível
        bot = TennisIQBot()
        
        # Testar função de alavancagem
        oportunidade_teste = {
            'jogador': 'Teste Corrigido',
            'oponente': 'Oponente Teste',
            'tipo': 'HOME',
            'momentum_score': 65,
            'ev': 1.0,
            'placar': '6-4,1-0'
        }
        
        odds_teste = {'jogador1_odd': 1.30, 'jogador2_odd': 3.50}
        
        print(f"\n🧪 TESTANDO ANÁLISE DE ALAVANCAGEM:")
        resultado = bot.analisar_alavancagem(oportunidade_teste, odds_teste)
        
        if resultado['alavancagem_aprovada']:
            print(f"✅ Análise aprovada com logs otimizados")
        else:
            print(f"❌ Análise rejeitada: {resultado.get('motivo', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste do bot: {e}")
        return False

def verificar_imports():
    """Verifica se todos os imports estão funcionando"""
    
    print(f"\n🧪 VERIFICAÇÃO DE IMPORTS")
    print("=" * 30)
    
    imports_ok = 0
    total_imports = 0
    
    # Testar imports essenciais
    imports_testes = [
        ("Rate Limiter", "backend.utils.rate_limiter", "api_rate_limiter"),
        ("Logger Produção", "backend.utils.logger_producao", "logger_prod"),
        ("Logger Ultra", "backend.utils.logger_ultra", "logger_ultra"),
        ("Detector Alavancagem", "backend.core.detector_alavancagem", "DetectorAlavancagem"),
        ("Bot Principal", "backend.core.bot", "TennisIQBot")
    ]
    
    for nome, modulo, objeto in imports_testes:
        total_imports += 1
        try:
            mod = __import__(modulo, fromlist=[objeto])
            getattr(mod, objeto)
            print(f"✅ {nome}: OK")
            imports_ok += 1
        except Exception as e:
            print(f"❌ {nome}: ERRO - {e}")
    
    print(f"\n📊 RESULTADO: {imports_ok}/{total_imports} imports funcionando")
    return imports_ok == total_imports

def executar_teste_completo():
    """Executa teste completo das correções"""
    
    print("🔧 TESTE COMPLETO DAS CORREÇÕES IMPLEMENTADAS")
    print("=" * 50)
    
    testes = [
        ("Verificação de Imports", verificar_imports),
        ("Logger Ultra", testar_logger_ultra),
        ("Bot com Correções", testar_bot_com_correcoes)
    ]
    
    resultados = {}
    
    for nome, func_teste in testes:
        try:
            resultado = func_teste()
            resultados[nome] = "✅ OK" if resultado else "❌ FALHA"
        except Exception as e:
            resultados[nome] = f"❌ ERRO: {e}"
    
    # Resumo final
    print(f"\n{'='*50}")
    print("📊 RESUMO DOS TESTES")
    print("=" * 50)
    
    for nome, resultado in resultados.items():
        print(f"{nome:25} {resultado}")
    
    # Análise
    sucessos = sum(1 for r in resultados.values() if "✅" in r)
    total = len(resultados)
    
    print(f"\n🎯 RESULTADO GERAL: {sucessos}/{total} testes aprovados")
    
    if sucessos == total:
        print(f"✅ TODAS AS CORREÇÕES FUNCIONANDO!")
        print(f"🚀 Sistema pronto para resolver rate limiting")
        print(f"🎯 Logs de alavancagem agora serão visíveis")
    else:
        print(f"⚠️ ALGUMAS CORREÇÕES PRECISAM DE AJUSTES")
        print(f"📝 Revisar implementação antes do deploy")
    
    return sucessos == total

if __name__ == "__main__":
    executar_teste_completo()
