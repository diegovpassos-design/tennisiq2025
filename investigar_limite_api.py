#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ANÁLISE CRÍTICA: API 3600 REQ/HORA COM ERRO 429
===============================================
Se o limite real é 3600/hora, por que estamos tendo 429 errors?
"""

def analisar_limite_real():
    """Analisa o problema real da API"""
    
    print("🚨 === ANÁLISE CRÍTICA DO LIMITE REAL ===")
    print("=" * 60)
    
    limite_esperado = 3600  # Que você mencionou
    limite_codigo = 1800    # Que está no código
    
    print(f"🔍 DISCREPÂNCIA IDENTIFICADA:")
    print(f"  • Limite REAL da API: {limite_esperado} req/hora")
    print(f"  • Limite no CÓDIGO: {limite_codigo} req/hora")
    print(f"  • Diferença: {limite_esperado - limite_codigo} req/hora ({((limite_esperado/limite_codigo)-1)*100:.0f}% maior)")
    
    print(f"\n🚨 CONSEQUÊNCIAS:")
    print(f"  ❌ Rate limiter configurado para METADE do limite real")
    print(f"  ❌ Sistema entra em 'modo crítico' muito cedo")
    print(f"  ❌ Desperdício de 50% da capacidade da API")
    
    return limite_esperado, limite_codigo

def recalcular_com_limite_correto():
    """Recalcula cenários com limite correto"""
    
    print(f"\n📊 === RECÁLCULO COM LIMITE CORRETO ===")
    print("=" * 60)
    
    limite_real = 3600
    req_por_ciclo = 15  # Estimativa média
    
    cenarios_tempo = {
        55: "Normal",
        65: "Moderado", 
        75: "Alto",
        90: "Crítico"
    }
    
    print("🔢 CENÁRIOS COM LIMITE CORRETO (3600 req/hora):")
    
    for tempo, nome in cenarios_tempo.items():
        ciclos_hora = 3600 / tempo
        req_hora = req_por_ciclo * ciclos_hora
        percentual = (req_hora / limite_real) * 100
        
        if percentual < 30:
            status = "✅ MUITO SEGURO"
        elif percentual < 50:
            status = "✅ SEGURO"
        elif percentual < 70:
            status = "🟡 MODERADO"
        elif percentual < 85:
            status = "⚠️ ALTO"
        else:
            status = "🚨 CRÍTICO"
        
        print(f"  {status} {nome}: {tempo}s → {ciclos_hora:.1f} ciclos → {req_hora:.0f} req/hora ({percentual:.1f}%)")

def identificar_causa_real():
    """Identifica a causa real dos erros 429"""
    
    print(f"\n🔍 === POSSÍVEIS CAUSAS REAIS ===")
    print("=" * 60)
    
    causas = {
        "limite_por_minuto": {
            "desc": "Limite por minuto (não por hora)",
            "calculo": "3600/hora = 60/minuto",
            "problematico": "Picos de requisições em poucos segundos"
        },
        "multiplas_instancias": {
            "desc": "Múltiplas instâncias do bot rodando",
            "calculo": "2 instâncias × 1800 req/hora = 3600",
            "problematico": "Compartilhando o mesmo limite"
        },
        "rate_limit_sliding": {
            "desc": "Janela deslizante (não hora fixa)",
            "calculo": "Últimos 60 minutos, não hora corrente",
            "problematico": "Acúmulo das requisições passadas"
        },
        "requisicoes_extras": {
            "desc": "Outras aplicações usando a mesma chave",
            "calculo": "Bot + outros serviços = limite compartilhado",
            "problematico": "Competição pela mesma quota"
        },
        "bursts_requisicoes": {
            "desc": "Rajadas de requisições simultâneas",
            "calculo": "10 req em 1 segundo vs distribuídas",
            "problematico": "Rate limiter da API muito sensível"
        }
    }
    
    print("🚨 CAUSAS PROVÁVEIS:")
    for causa, dados in causas.items():
        print(f"\n🔸 {dados['desc'].upper()}:")
        print(f"    • Cálculo: {dados['calculo']}")
        print(f"    • Problema: {dados['problematico']}")

def investigar_logs_railway():
    """Investiga padrões nos logs do Railway"""
    
    print(f"\n🔍 === INVESTIGAÇÃO DOS LOGS ===")
    print("=" * 60)
    
    # Padrões observados nos logs
    observacoes = [
        "Erro 429 em ciclos consecutivos (13-15)",
        "53 requests mostrado no contador",
        "Próximo ciclo: 45s (não os tempos novos)",
        "Erro na primeira requisição do ciclo"
    ]
    
    print("📋 PADRÕES OBSERVADOS:")
    for obs in observacoes:
        print(f"  • {obs}")
    
    print(f"\n💡 HIPÓTESES:")
    print(f"  1. 🔄 Deploy ainda não aplicado (ainda usando 45s)")
    print(f"  2. ⏱️ Rate limit por MINUTO, não por hora")
    print(f"  3. 🌐 Múltiplas instâncias compartilhando limite")
    print(f"  4. 📊 Contador de requests incorreto/defasado")

def solucoes_imediatas():
    """Propõe soluções imediatas"""
    
    print(f"\n🛠️ === SOLUÇÕES IMEDIATAS ===")
    print("=" * 60)
    
    solucoes = {
        "atualizar_limite": {
            "desc": "Corrigir limite no código para 3600",
            "arquivo": "rate_limiter.py, bot.py",
            "urgencia": "CRÍTICA"
        },
        "verificar_instancias": {
            "desc": "Verificar se há múltiplas instâncias rodando",
            "arquivo": "Railway dashboard",
            "urgencia": "ALTA"
        },
        "implementar_burst_control": {
            "desc": "Controle de rajadas (max 5 req/10s)",
            "arquivo": "rate_limiter.py",
            "urgencia": "ALTA"
        },
        "monitorar_real_time": {
            "desc": "Log de cada requisição com timestamp",
            "arquivo": "bot.py",
            "urgencia": "MÉDIA"
        }
    }
    
    print("🎯 AÇÕES PRIORITÁRIAS:")
    for i, (nome, dados) in enumerate(solucoes.items(), 1):
        print(f"\n{i}. {dados['desc'].upper()} ({dados['urgencia']})")
        print(f"    📁 Arquivo: {dados['arquivo']}")

def main():
    """Análise completa"""
    
    print("🚨 INVESTIGAÇÃO: POR QUE 429 COM LIMITE 3600?")
    print("=" * 70)
    
    analisar_limite_real()
    recalcular_com_limite_correto()
    identificar_causa_real()
    investigar_logs_railway()
    solucoes_imediatas()
    
    print(f"\n" + "=" * 70)
    print("💡 CONCLUSÃO PRELIMINAR:")
    print("❌ Código configurado para 1800 req/hora (50% do limite real)")
    print("❌ Possível limite por MINUTO ou múltiplas instâncias")
    print("✅ AÇÃO: Corrigir limite para 3600 + investigar Railway")

if __name__ == "__main__":
    main()
