#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CALCULADORA DE REQUISIÇÕES API - TennisIQ Bot
=============================================
Calcula quantas requisições por ciclo e por hora o sistema faz
"""

def analisar_requisicoes_por_ciclo():
    """Analisa quantas requisições são feitas por ciclo"""
    
    print("🔍 === ANÁLISE DE REQUISIÇÕES POR CICLO ===")
    print("=" * 50)
    
    # Baseado na análise do código
    requisicoes_ciclo = {
        "timing_filter": {
            "descricao": "Filtro de timing (seleção_time.py)",
            "quantidade": 1,
            "detalhes": "1 requisição para buscar partidas em andamento"
        },
        "coleta_partidas": {
            "descricao": "Coleta de dados das partidas (seleção_final.py)", 
            "quantidade": 2,
            "detalhes": "1 req para inplay + 1 req para detalhes de cada partida"
        },
        "odds_por_partida": {
            "descricao": "Buscar odds por oportunidade encontrada",
            "quantidade_media": 5,  # Estimativa baseada em ~5 oportunidades por ciclo
            "detalhes": "1 requisição por evento que vira oportunidade"
        },
        "stats_por_partida": {
            "descricao": "Estatísticas reais por partida analisada",
            "quantidade_media": 3,  # Apenas para partidas que passam nos filtros
            "detalhes": "1 requisição de stats por partida que gera sinal"
        }
    }
    
    total_requisicoes = 0
    
    print("📊 REQUISIÇÕES POR CICLO:")
    for categoria, dados in requisicoes_ciclo.items():
        if "quantidade_media" in dados:
            qty = dados["quantidade_media"]
        else:
            qty = dados["quantidade"]
        
        total_requisicoes += qty
        print(f"  🔸 {dados['descricao']}: {qty} requisições")
        print(f"     └─ {dados['detalhes']}")
    
    print(f"\n🎯 TOTAL ESTIMADO POR CICLO: {total_requisicoes} requisições")
    return total_requisicoes

def calcular_ciclos_por_hora():
    """Calcula quantos ciclos por hora baseado no tempo de espera"""
    
    print("\n⏰ === CÁLCULO DE CICLOS POR HORA ===")
    print("=" * 50)
    
    # Tempos de espera baseados no código (linha 2232-2239 do bot.py)
    tempos_espera = {
        "normal": 55,      # Uso normal (< 900 requests/hora)
        "medio": 65,       # 50% do limite (900-1200 requests/hora)  
        "alto": 75,        # 67% do limite (1200-1500 requests/hora)
        "critico": 90      # 83% do limite (> 1500 requests/hora)
    }
    
    print("⏱️ TEMPOS DE ESPERA POR CENÁRIO:")
    ciclos_por_hora = {}
    
    for cenario, tempo in tempos_espera.items():
        ciclos = 3600 / tempo  # 3600 segundos = 1 hora
        ciclos_por_hora[cenario] = round(ciclos, 1)
        print(f"  🔸 {cenario.title()}: {tempo}s → {ciclos_por_hora[cenario]} ciclos/hora")
    
    return ciclos_por_hora

def calcular_requisicoes_por_hora():
    """Calcula total de requisições por hora"""
    
    print("\n📈 === REQUISIÇÕES TOTAIS POR HORA ===")
    print("=" * 50)
    
    req_por_ciclo = analisar_requisicoes_por_ciclo()
    ciclos_por_hora = calcular_ciclos_por_hora()
    
    print("🎯 REQUISIÇÕES TOTAIS POR HORA:")
    
    for cenario, ciclos in ciclos_por_hora.items():
        total_req_hora = req_por_ciclo * ciclos
        print(f"  🔸 {cenario.title()}: {int(total_req_hora)} requisições/hora")
        print(f"     └─ {req_por_ciclo} req/ciclo × {ciclos} ciclos/hora")
    
    return req_por_ciclo, ciclos_por_hora

def verificar_limites_api():
    """Verifica se estamos dentro dos limites da API"""
    
    print("\n⚠️ === VERIFICAÇÃO DE LIMITES ===")
    print("=" * 50)
    
    limite_api = 1800  # Limite da API por hora
    req_por_ciclo, ciclos_por_hora = calcular_requisicoes_por_hora()
    
    print(f"📋 LIMITE DA API: {limite_api} requisições/hora")
    print("\n🎯 ANÁLISE DE SEGURANÇA:")
    
    for cenario, ciclos in ciclos_por_hora.items():
        total_req = req_por_ciclo * ciclos
        percentual = (total_req / limite_api) * 100
        
        if percentual < 50:
            status = "✅ SEGURO"
        elif percentual < 75:
            status = "⚠️ MODERADO"
        elif percentual < 90:
            status = "🚨 ALTO"
        else:
            status = "❌ CRÍTICO"
        
        print(f"  {status} {cenario.title()}: {int(total_req)}/1800 ({percentual:.1f}%)")
    
    # Calcular cenário mais provável
    print(f"\n💡 CENÁRIO MAIS PROVÁVEL:")
    print(f"   • Normal/Médio: {req_por_ciclo} req/ciclo × ~60 ciclos/hora = ~{req_por_ciclo * 60} req/hora")
    print(f"   • Uso da API: ~{((req_por_ciclo * 60) / limite_api) * 100:.1f}% do limite")

def main():
    """Função principal"""
    print("🚀 CALCULADORA DE REQUISIÇÕES API - TennisIQ Bot")
    print("=" * 60)
    
    calcular_requisicoes_por_hora()
    verificar_limites_api()
    
    print("\n" + "=" * 60)
    print("📋 RESUMO EXECUTIVO:")
    print("✅ Sistema usa ~11 requisições por ciclo")
    print("✅ Executa ~60-65 ciclos por hora (modo normal)")
    print("✅ Total: ~660-715 requisições/hora (~37-40% do limite)")
    print("✅ Rate limiting dinâmico mantém segurança")
    print("✅ Margem de 60% para picos e contingências")

if __name__ == "__main__":
    main()
