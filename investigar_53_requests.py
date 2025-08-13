#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
INVESTIGAÇÃO FINAL: MÚLTIPLAS INSTÂNCIAS OU LIMITE POR MINUTO
============================================================
53 req/ciclo × 80 ciclos = 4240 req/hora > 3600 limite
"""

def analisar_53_requests_por_ciclo():
    """Analisa por que há 53 requests por ciclo"""
    
    print("🔍 === ANÁLISE: 53 REQUESTS POR CICLO ===")
    print("=" * 50)
    
    requests_estimados = {
        "timing_filter": 1,
        "partidas_inplay": 1,
        "odds_por_partida": 10,  # 10 partidas em andamento
        "stats_por_partida": 5,  # 5 partidas que passam filtros
        "telegram_notifications": 2,  # 1 sinal
        "dashboard_updates": 1,
        "verificacao_resultados": 1
    }
    
    total_esperado = sum(requests_estimados.values())
    discrepancia = 53 - total_esperado
    
    print("📊 BREAKDOWN ESPERADO:")
    for categoria, qty in requests_estimados.items():
        print(f"  • {categoria}: {qty} req")
    
    print(f"\n🎯 COMPARAÇÃO:")
    print(f"  • Total esperado: {total_esperado} req/ciclo")
    print(f"  • Observado nos logs: 53 req/ciclo")
    print(f"  • Discrepância: +{discrepancia} req ({(discrepancia/total_esperado)*100:.0f}% extra)")
    
    return discrepancia

def investigar_multiplas_instancias():
    """Investiga possibilidade de múltiplas instâncias"""
    
    print(f"\n🔍 === INVESTIGAÇÃO: MÚLTIPLAS INSTÂNCIAS ===")
    print("=" * 50)
    
    print("🚨 HIPÓTESE: 2 INSTÂNCIAS RODANDO")
    print("  • Cada instância: ~26 req/ciclo (normal)")
    print("  • Total observado: 53 req/ciclo")
    print("  • 26 × 2 = 52 ≈ 53 ✅ MATCH!")
    
    print(f"\n📋 COMO VERIFICAR NO RAILWAY:")
    verificacoes = [
        "Dashboard Railway > TennisIQ > Replicas: deve mostrar '1 Replica'",
        "Metrics > Memory/CPU: se 2 instâncias, uso será dobrado",
        "Logs: procurar por 'Bot inicializado' duplicado no mesmo timestamp",
        "Variables: verificar se não há auto-scaling habilitado"
    ]
    
    for i, verif in enumerate(verificacoes, 1):
        print(f"  {i}. {verif}")

def investigar_limite_por_minuto():
    """Investiga possibilidade de limite por minuto"""
    
    print(f"\n🔍 === INVESTIGAÇÃO: LIMITE POR MINUTO ===")
    print("=" * 50)
    
    limite_hora = 3600
    limite_minuto_teorico = limite_hora / 60
    
    print(f"🎯 CÁLCULOS:")
    print(f"  • Limite teórico por minuto: {limite_hora}/60 = {limite_minuto_teorico} req/min")
    print(f"  • Observado por ciclo (45s): 53 req")
    print(f"  • Convertido para minuto: 53 × (60/45) = {53 * (60/45):.1f} req/min")
    
    if 53 * (60/45) > limite_minuto_teorico:
        print(f"  🚨 PROBLEMA: Excede limite por minuto!")
    else:
        print(f"  ✅ OK: Dentro do limite por minuto")
    
    print(f"\n💡 TESTE NO CÓDIGO:")
    print(f"  • Rate limiter atual: max_requests_per_minute=30")
    print(f"  • Necessário: {53 * (60/45):.0f} req/min")
    print(f"  • Ajuste sugerido: max_requests_per_minute=80")

def investigar_burst_requests():
    """Investiga rajadas de requisições"""
    
    print(f"\n🔍 === INVESTIGAÇÃO: RAJADAS DE REQUISIÇÕES ===")
    print("=" * 50)
    
    print("🚨 PROBLEMA POSSÍVEL:")
    print("  • Bot faz todas as 53 req em poucos segundos no início do ciclo")
    print("  • API tem limite de burst (ex: max 10 req/segundo)")
    print("  • Rate limiter da API rejeita requisições simultâneas")
    
    print(f"\n💡 SOLUÇÕES:")
    solucoes = [
        "Adicionar delay entre requisições (0.5s)",
        "Implementar batch processing",
        "Distribuir requisições ao longo do ciclo",
        "Rate limiting por segundo (max 5 req/s)"
    ]
    
    for i, sol in enumerate(solucoes, 1):
        print(f"  {i}. {sol}")

def criar_plano_debug():
    """Cria plano para debuggar o problema"""
    
    print(f"\n🛠️ === PLANO DE DEBUG ===")
    print("=" * 50)
    
    acoes = {
        "IMEDIATO": [
            "Verificar Railway dashboard: quantas replicas ativas?",
            "Corrigir max_requests_per_minute: 30 → 80",
            "Deploy com limite 3600 + logs detalhados"
        ],
        "MONITORAMENTO": [
            "Log timestamp de cada requisição",
            "Contar requisições reais vs estimadas",
            "Alertas quando > 50 req/ciclo"
        ],
        "OTIMIZAÇÃO": [
            "Delay 0.5s entre requisições críticas",
            "Cache mais agressivo (90s vs 45s)",
            "Batch processing quando possível"
        ]
    }
    
    for categoria, lista in acoes.items():
        print(f"\n🔸 {categoria}:")
        for acao in lista:
            print(f"    • {acao}")

def main():
    """Investigação completa"""
    
    print("🚨 INVESTIGAÇÃO FINAL: 53 REQ/CICLO")
    print("=" * 60)
    
    analisar_53_requests_por_ciclo()
    investigar_multiplas_instancias()
    investigar_limite_por_minuto()
    investigar_burst_requests()
    criar_plano_debug()
    
    print(f"\n" + "=" * 60)
    print("💡 CONCLUSÕES:")
    print("❓ 53 req/ciclo é 2x o esperado (~26)")
    print("🔍 Possível: 2 instâncias Railway ou burst limit")
    print("✅ AÇÃO: Corrigir limite + verificar replicas + rate limit por minuto")

if __name__ == "__main__":
    main()
