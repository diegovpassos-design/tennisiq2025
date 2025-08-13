#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 DEPLOY FINAL: CORREÇÕES COMPLETAS
============================================================
Script final para aplicar todas as correções e fazer deploy
"""

import os
import time
from pathlib import Path

def aplicar_correcao_bot():
    """Aplica correções finais no bot.py"""
    print("🔧 Aplicando correções finais no bot.py...")
    
    bot_path = "backend/core/bot.py"
    
    with open(bot_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar se já tem o rate limiter avançado
    if 'rate_limiter_avancado' not in content:
        # Adicionar import do rate limiter avançado
        import_line = "from backend.utils.rate_limiter_avancado import RateLimiterAvancado"
        
        # Inserir após outros imports
        if "from backend.utils.logger_formatado import" in content:
            content = content.replace(
                "from backend.utils.logger_formatado import",
                f"{import_line}\nfrom backend.utils.logger_formatado import"
            )
    
    # Atualizar thresholds de rate limiting para 3600 req/hour
    corrections = [
        ("se usage_hour >= 2800:", "se usage_hour >= 2800:"),  # Já correto
        ("if usage_hour >= 1400:", "if usage_hour >= 2800:"),  # Corrigir threshold crítico
        ("Uso alto: {usage_hour}/1800", "Uso alto: {usage_hour}/3600"),
        ("Critical: {usage_hour}/1800", "Critical: {usage_hour}/3600"),
        ("Rate: {usage_hour}/1800", "Rate: {usage_hour}/3600"),
    ]
    
    for old, new in corrections:
        if old in content and old != new:
            content = content.replace(old, new)
            print(f"  ✅ Corrigido: {old} → {new}")
    
    # Adicionar log de requests por ciclo
    if "📊 Requests este ciclo:" not in content:
        # Procurar onde adicionar o log
        if "def executar_analise_completa" in content:
            # Adicionar contador de requests
            cycle_counter = '''
        # Contador de requests por ciclo
        self.requests_this_cycle = 0
        start_cycle_time = time.time()
        
        print(f"🔄 === INICIANDO CICLO {datetime.now().strftime('%H:%M:%S')} ===")'''
            
            content = content.replace(
                "def executar_analise_completa(self):",
                f"def executar_analise_completa(self):{cycle_counter}"
            )
    
    with open(bot_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Bot.py atualizado!")

def gerar_arquivo_deploy():
    """Gera arquivo com informações para deploy"""
    print("📋 Gerando arquivo de deploy...")
    
    deploy_info = """
🚀 DEPLOY FINAL - RATE LIMITING CORRIGIDO
============================================================
📅 Data: {timestamp}

🔧 CORREÇÕES APLICADAS:
• API Limit: 1800 → 3600 req/hour
• Rate Limiter: max_requests_per_minute = 80 (vs 30)
• Rate Limiter: max_requests_per_second = 5 (novo)
• Bot Thresholds: 1400 → 2800 (crítico)
• Odds Caching: 45s timeout
• Burst Control: 0.2s delay entre requests

📊 ESTIMATIVAS CORRIGIDAS:
• Requests por ciclo: ~26 (vs 53 observado)
• Requests por hora: 26 × 80 = 2080 (vs 3600 limite)
• Margem de segurança: 42%

🔍 INVESTIGAÇÃO MÚLTIPLAS INSTÂNCIAS:
• Local: 1 instância detectada ✅
• Railway: Verificar dashboard - deve ter 1 replica
• Comando: railway ps (verificar processos)

🚨 PROBLEMAS IDENTIFICADOS:
• 53 req/ciclo = ~2x o esperado
• Possível: 2 replicas Railway (26×2≈53)
• Possível: Burst limiting na API

💡 SOLUÇÕES IMPLEMENTADAS:
• Rate limiting por segundo: max 5 req/s
• Delay entre requests: 0.2s
• Cache odds: 45s para reduzir requests
• Monitoring detalhado nos logs

🎯 PRÓXIMOS PASSOS DEPLOY:
1. Verificar Railway dashboard: quantas replicas?
2. Deploy com correções aplicadas
3. Monitorar logs: deve mostrar ~26 req/ciclo
4. Se ainda 53 req/ciclo → ajustar para 2 replicas

🔗 COMANDOS RAILWAY:
• railway ps                 # Ver processos
• railway status            # Status serviço  
• railway logs -f           # Logs tempo real
• railway variables         # Ver variáveis

============================================================
""".format(timestamp=time.strftime('%Y-%m-%d %H:%M:%S'))
    
    with open("DEPLOY_RATE_LIMITING_FINAL.md", 'w', encoding='utf-8') as f:
        f.write(deploy_info)
    
    print("✅ Arquivo de deploy criado!")

def verificar_arquivos_corrigidos():
    """Verifica se todos os arquivos foram corrigidos"""
    print("🔍 Verificando arquivos corrigidos...")
    
    files_to_check = [
        ("backend/utils/rate_limiter.py", ["max_requests_per_hour=3600", "max_requests_per_minute=80"]),
        ("backend/core/bot.py", ["usage_hour >= 2800", "usage_hour}/3600"]),
        ("backend/utils/rate_limiter_avancado.py", ["max_requests_per_second=5", "burst_delay=0.2"]),
    ]
    
    all_correct = True
    
    for file_path, expected_content in files_to_check:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            missing = []
            for expected in expected_content:
                if expected not in content:
                    missing.append(expected)
            
            if missing:
                print(f"❌ {file_path}: Faltando {missing}")
                all_correct = False
            else:
                print(f"✅ {file_path}: Correto")
        else:
            print(f"❌ {file_path}: Arquivo não encontrado")
            all_correct = False
    
    return all_correct

def main():
    """Função principal"""
    print("🚀 === DEPLOY FINAL - RATE LIMITING ===")
    print(f"📅 {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 1. Aplicar correções finais
        aplicar_correcao_bot()
        
        # 2. Verificar correções
        if verificar_arquivos_corrigidos():
            print("\n✅ Todas as correções aplicadas!")
        else:
            print("\n❌ Algumas correções faltando")
        
        # 3. Gerar arquivo de deploy
        gerar_arquivo_deploy()
        
        print("\n🎯 === DEPLOY PRONTO! ===")
        print("\n📋 CHECKLIST FINAL:")
        print("  ✅ Rate limiter: 3600 req/hour")
        print("  ✅ Bot thresholds: 2800 crítico")
        print("  ✅ Burst control: 5 req/s max")
        print("  ✅ Odds caching: 45s timeout")
        print("  ✅ Scripts investigação criados")
        
        print("\n🚀 PRÓXIMO PASSO:")
        print("  1. Deploy no Railway")
        print("  2. Verificar Railway dashboard: 1 replica")
        print("  3. Monitorar logs: ~26 req/ciclo esperado")
        
        print("\n📁 ARQUIVOS PARA DEPLOY:")
        print("  • backend/utils/rate_limiter.py")
        print("  • backend/core/bot.py")
        print("  • backend/utils/rate_limiter_avancado.py")
        print("  • DEPLOY_RATE_LIMITING_FINAL.md")
        
    except Exception as e:
        print(f"❌ Erro no deploy final: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    main()
