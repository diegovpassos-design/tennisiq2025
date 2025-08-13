#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ANÁLISE DO LOG DE DEPLOYMENT ATUAL
=================================
Verificação do status das otimizações implementadas
"""

def analisar_log_deployment():
    """Analisa o log de deployment mais recente"""
    
    print("📊 ANÁLISE DO LOG DE DEPLOYMENT ATUAL")
    print("=" * 50)
    
    log_path = "deployment_logs_tennisiq_1755097350292.log"
    
    try:
        with open(log_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        total_lines = len(lines)
        
        print(f"📄 Arquivo: {log_path}")
        print(f"📏 Total de linhas: {total_lines}")
        
        # Análise de rate limiting
        rate_limit_errors = content.count("Railway rate limit of 500 logs/sec reached")
        messages_dropped = content.count("Messages dropped:")
        
        print(f"\n🚨 RATE LIMITING:")
        print(f"   • Erros de rate limit: {rate_limit_errors}")
        print(f"   • Mensagens perdidas: {messages_dropped}")
        
        if rate_limit_errors > 0:
            print(f"   ❌ PROBLEMA: Ainda há rate limiting!")
        else:
            print(f"   ✅ OK: Sem erros de rate limiting")
        
        # Análise do logger de produção
        logs_suprimidos = content.count("logs similares suprimidos")
        
        print(f"\n📊 LOGGER DE PRODUÇÃO:")
        print(f"   • Supressões ativas: {logs_suprimidos}")
        
        if logs_suprimidos > 0:
            print(f"   ✅ OK: Logger de produção funcionando")
        else:
            print(f"   ⚠️ AVISO: Logger de produção pode não estar ativo")
        
        # Análise de alavancagem
        alavancagem_mentions = content.count("alavancagem") + content.count("ALAVANCAGEM")
        
        print(f"\n🎯 ESTRATÉGIA DE ALAVANCAGEM:")
        print(f"   • Menções de alavancagem: {alavancagem_mentions}")
        
        if alavancagem_mentions == 0:
            print(f"   ❌ PROBLEMA: Sem menções de alavancagem!")
            print(f"   ❌ A estratégia pode não estar sendo executada")
        else:
            print(f"   ✅ OK: Estratégia sendo executada")
        
        # Análise de oportunidades
        oportunidades_aprovadas = content.count("OPORTUNIDADES APROVADAS")
        sinais_enviados = content.count("🎯 SINAL ENVIADO") + content.count("📨 Telegram")
        nenhum_sinal = content.count("Nenhum sinal novo para enviar")
        
        print(f"\n🎯 OPORTUNIDADES E SINAIS:")
        print(f"   • Ciclos com oportunidades: {oportunidades_aprovadas}")
        print(f"   • Sinais enviados: {sinais_enviados}")
        print(f"   • Ciclos sem sinais: {nenhum_sinal}")
        
        # Análise de partidas
        partidas_analisadas = content.count("📊 Analisando:")
        
        print(f"\n📊 ATIVIDADE GERAL:")
        print(f"   • Partidas analisadas: {partidas_analisadas}")
        
        # Últimas linhas para ver status atual
        print(f"\n🕐 STATUS MAIS RECENTE:")
        for line in lines[-10:]:
            if line.strip() and "[info]" in line:
                timestamp = line.split("Z [info] ")[0].split("T")[1] if "T" in line else "N/A"
                message = line.split("Z [info] ")[1] if "Z [info] " in line else line
                print(f"   {timestamp}: {message[:80]}...")
                break
        
        # Conclusão
        print(f"\n🎯 CONCLUSÃO:")
        
        if rate_limit_errors > 5:
            print(f"   🚨 CRÍTICO: Rate limiting ainda é um problema!")
            print(f"   📝 Ação: Revisar configurações do logger de produção")
        elif alavancagem_mentions == 0:
            print(f"   ⚠️ ATENÇÃO: Estratégia de alavancagem não está sendo executada")
            print(f"   📝 Ação: Verificar se as otimizações foram deployadas")
        elif sinais_enviados == 0 and oportunidades_aprovadas > 0:
            print(f"   ⚠️ ATENÇÃO: Oportunidades detectadas mas nenhum sinal enviado")
            print(f"   📝 Ação: Verificar lógica de envio de sinais")
        else:
            print(f"   ✅ SISTEMA FUNCIONANDO: Logs indicam operação normal")
            print(f"   📝 Próximo: Monitorar por mais tempo para ver sinais de alavancagem")
        
        return True
        
    except FileNotFoundError:
        print(f"❌ Arquivo de log não encontrado: {log_path}")
        return False
    except Exception as e:
        print(f"❌ Erro ao analisar log: {e}")
        return False

if __name__ == "__main__":
    analisar_log_deployment()
