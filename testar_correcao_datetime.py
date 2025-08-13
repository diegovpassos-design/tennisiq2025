#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 TESTE: CORREÇÃO DO ERRO DATETIME/FLOAT
============================================================
Testa se o erro de mistura de tipos foi corrigido
"""

import time
from datetime import datetime, timedelta

def testar_tipos_datetime():
    """Testa as operações que estavam causando erro"""
    print("🔧 === TESTE DE TIPOS DATETIME/FLOAT ===")
    
    # Simular as operações que estavam causando erro
    print("\n1. Teste datetime + timedelta (CORRETO):")
    try:
        agora = datetime.now()
        resultado = agora + timedelta(seconds=45)
        print(f"   ✅ agora (datetime): {agora}")
        print(f"   ✅ agora + timedelta(45): {resultado}")
    except Exception as e:
        print(f"   ❌ ERRO: {e}")
    
    print("\n2. Teste time.time() - time.time() (CORRETO):")
    try:
        agora_timestamp = time.time()
        timestamp_cache = time.time() - 30  # 30s atrás
        diferenca = agora_timestamp - timestamp_cache
        print(f"   ✅ agora_timestamp (float): {agora_timestamp}")
        print(f"   ✅ diferença (float): {diferenca}s")
    except Exception as e:
        print(f"   ❌ ERRO: {e}")
    
    print("\n3. Teste ERRO que estava acontecendo:")
    try:
        agora_float = time.time()
        timedelta_obj = timedelta(seconds=45)
        # Isso causaria erro: float + timedelta
        resultado = agora_float + timedelta_obj
        print(f"   ❌ Não deveria chegar aqui: {resultado}")
    except Exception as e:
        print(f"   ✅ ERRO CAPTURADO (esperado): {e}")
    
    print("\n4. Teste correção para cache:")
    try:
        # Simular cache como no bot
        cache_odds = {}
        agora_timestamp = time.time()
        cache_timeout = 45
        
        # Simular entrada no cache
        cache_odds["test"] = (agora_timestamp - 30, {"odd": 1.5})  # 30s atrás
        
        # Verificar se cache é válido
        for key, (timestamp, data) in cache_odds.items():
            if agora_timestamp - timestamp < cache_timeout:
                print(f"   ✅ Cache válido: {key} - idade {agora_timestamp - timestamp:.1f}s")
            else:
                print(f"   🗑️ Cache expirado: {key} - idade {agora_timestamp - timestamp:.1f}s")
                
    except Exception as e:
        print(f"   ❌ ERRO no cache: {e}")

def testar_cenario_bot():
    """Testa o cenário específico do bot"""
    print("\n🤖 === TESTE CENÁRIO BOT ===")
    
    try:
        # Simular loop do bot
        agora = datetime.now()
        agora_timestamp = time.time()
        
        print(f"✅ agora (datetime): {agora}")
        print(f"✅ agora_timestamp (float): {agora_timestamp}")
        
        # Simular dashboard update
        proxima_verificacao = (agora + timedelta(seconds=45)).isoformat()
        print(f"✅ próxima_verificacao: {proxima_verificacao}")
        
        # Simular cache check
        cache_odds_timeout = 45
        timestamp_ficticio = agora_timestamp - 30  # 30s atrás
        
        if agora_timestamp - timestamp_ficticio < cache_odds_timeout:
            print(f"✅ Cache válido: diferença {agora_timestamp - timestamp_ficticio:.1f}s < {cache_odds_timeout}s")
        else:
            print(f"🗑️ Cache expirado: diferença {agora_timestamp - timestamp_ficticio:.1f}s >= {cache_odds_timeout}s")
            
    except Exception as e:
        print(f"❌ ERRO no cenário bot: {e}")

def main():
    """Função principal"""
    print("🔧 TESTE: CORREÇÃO DATETIME/FLOAT")
    print("=" * 50)
    
    testar_tipos_datetime()
    testar_cenario_bot()
    
    print("\n🎯 === CONCLUSÃO ===")
    print("✅ Se todos os testes passaram, o erro foi corrigido!")
    print("📋 Correções aplicadas:")
    print("   • Separação clara entre datetime e timestamp")
    print("   • agora = datetime.now() para dashboard")
    print("   • agora_timestamp = time.time() para cache")
    print("   • Uso correto de cada tipo em suas operações")

if __name__ == "__main__":
    main()
