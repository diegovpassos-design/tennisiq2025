#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TESTE DIRETO DA ESTRATÉGIA DE ALAVANCAGEM
=========================================
Verificação se a estratégia está funcionando após deploy
"""

import sys
import os

# Adicionar ao path
PROJECT_ROOT = os.path.dirname(__file__)
sys.path.append(os.path.join(PROJECT_ROOT, 'backend'))

def testar_detector_alavancagem():
    """Testa se o detector de alavancagem está funcionando"""
    
    print("🔍 TESTE DIRETO DA ESTRATÉGIA DE ALAVANCAGEM")
    print("=" * 50)
    
    try:
        # Importar detector
        from backend.core.detector_alavancagem import DetectorAlavancagem
        
        detector = DetectorAlavancagem()
        
        print(f"✅ Detector importado com sucesso")
        print(f"📊 Critérios atuais:")
        print(f"   • Odd mínima: {detector.odd_minima}")
        print(f"   • Odd máxima: {detector.odd_maxima}")
        print(f"   • Momentum mínimo: {detector.momentum_minimo}%")
        
        # Teste com cenário válido
        oportunidade_teste = {
            'jogador': 'Teste Player',
            'oponente': 'Oponente Teste',
            'tipo': 'HOME',
            'momentum_score': 65,
            'ev': 1.0
        }
        
        placar_teste = "6-4,1-0"  # Ganhou primeiro set, liderando segundo
        odds_teste = {'jogador1_odd': 1.30, 'jogador2_odd': 3.50}
        
        print(f"\n🧪 TESTANDO CENÁRIO VÁLIDO:")
        print(f"   • Jogador: {oportunidade_teste['jogador']}")
        print(f"   • Placar: {placar_teste}")
        print(f"   • Odd: {odds_teste['jogador1_odd']}")
        print(f"   • Momentum: {oportunidade_teste['momentum_score']}%")
        
        resultado = detector.analisar_oportunidade_alavancagem(
            oportunidade_teste, placar_teste, odds_teste
        )
        
        print(f"\n📊 RESULTADO:")
        if resultado['alavancagem_aprovada']:
            print(f"   ✅ APROVADO!")
            print(f"   📋 Justificativa: {resultado.get('justificativa', 'N/A')}")
        else:
            print(f"   ❌ REJEITADO: {resultado.get('motivo', 'N/A')}")
        
        return resultado['alavancagem_aprovada']
        
    except Exception as e:
        print(f"❌ Erro ao testar detector: {e}")
        return False

def testar_bot_alavancagem():
    """Testa se o bot principal usa alavancagem"""
    
    print(f"\n🔍 TESTE DO BOT PRINCIPAL")
    print("=" * 30)
    
    try:
        from backend.core.bot import TennisIQBot
        
        print(f"✅ Bot importado com sucesso")
        
        # Verificar se tem detector de alavancagem
        bot = TennisIQBot()
        
        if hasattr(bot, 'detector_alavancagem'):
            print(f"✅ Bot tem detector de alavancagem")
            
            # Verificar critérios do detector
            detector = bot.detector_alavancagem
            print(f"📊 Critérios do detector no bot:")
            print(f"   • Odd mínima: {detector.odd_minima}")
            print(f"   • Odd máxima: {detector.odd_maxima}")
            print(f"   • Momentum mínimo: {detector.momentum_minimo}%")
            
            # Verificar se tem função de análise
            if hasattr(bot, 'analisar_alavancagem'):
                print(f"✅ Bot tem função analisar_alavancagem")
                return True
            else:
                print(f"❌ Bot NÃO tem função analisar_alavancagem")
                return False
        else:
            print(f"❌ Bot NÃO tem detector de alavancagem")
            return False
        
    except Exception as e:
        print(f"❌ Erro ao testar bot: {e}")
        return False

def verificar_logs_railway():
    """Sugere verificações para o Railway"""
    
    print(f"\n🔍 VERIFICAÇÕES SUGERIDAS PARA RAILWAY")
    print("=" * 40)
    
    print(f"1️⃣ VERIFICAR DEPLOY:")
    print(f"   • O commit 00e0f76 foi deployado?")
    print(f"   • As mudanças estão na instância ativa?")
    print(f"   • Houve restart após o deploy?")
    
    print(f"\n2️⃣ VERIFICAR LOGS:")
    print(f"   • Procurar por: '🚀 ALAVANCAGEM:'")
    print(f"   • Procurar por: 'Analisando oportunidade'")
    print(f"   • Verificar se detector está sendo usado")
    
    print(f"\n3️⃣ VERIFICAR TIMING:")
    print(f"   • Estratégia só roda em partidas específicas")
    print(f"   • Precisa ter primeiro set terminado")
    print(f"   • Precisa estar no segundo set")
    
    print(f"\n4️⃣ LOGS DE DEBUG:")
    print(f"   • Ativar nível DEBUG temporariamente")
    print(f"   • Verificar se oportunidades chegam ao detector")
    print(f"   • Monitorar ciclos específicos")

def executar_verificacao_completa():
    """Executa verificação completa"""
    
    print("🎯 VERIFICAÇÃO COMPLETA DA ESTRATÉGIA DE ALAVANCAGEM")
    print("=" * 60)
    
    # Teste 1: Detector direto
    detector_ok = testar_detector_alavancagem()
    
    # Teste 2: Bot principal
    bot_ok = testar_bot_alavancagem()
    
    # Sugestões para Railway
    verificar_logs_railway()
    
    # Conclusão
    print(f"\n🎯 CONCLUSÃO:")
    
    if detector_ok and bot_ok:
        print(f"✅ SISTEMA LOCAL FUNCIONANDO CORRETAMENTE")
        print(f"🔍 PROBLEMA PROVÁVEL: Deploy não efetivado ou logs suprimidos")
        print(f"📝 AÇÃO: Verificar se Railway aplicou as mudanças")
    elif detector_ok and not bot_ok:
        print(f"⚠️ DETECTOR OK, MAS BOT COM PROBLEMA")
        print(f"📝 AÇÃO: Verificar integração no bot principal")
    else:
        print(f"❌ PROBLEMA NO DETECTOR")
        print(f"📝 AÇÃO: Revisar implementação do detector")
    
    return detector_ok and bot_ok

if __name__ == "__main__":
    executar_verificacao_completa()
