"""
ANÁLISE: Por que oportunidades são enviadas com 6 horas de antecedência
Identifica onde está configurado este filtro e como alterar para 24 horas
"""

import sys
import os
sys.path.append('backend')

def analyze_timing_configuration():
    print("🕐 ANÁLISE DA CONFIGURAÇÃO DE TIMING")
    print("=" * 60)
    
    print("\n📋 COMO FUNCIONA ATUALMENTE:")
    print("-" * 40)
    
    print("\n1️⃣ SCAN DE OPORTUNIDADES:")
    print("• monitoring_service.py linha 109:")
    print("  hours_ahead=72  # Busca jogos até 72h no futuro")
    print("• prelive_scanner.py linha 68:")
    print("  def get_upcoming_events(self, hours_ahead: int = 48)")
    print("• Padrão: 48h, mas service força 72h")
    
    print("\n2️⃣ SALVAMENTO NO BANCO:")
    print("• Todas as oportunidades são salvas")
    print("• Não há filtro de tempo no salvamento")
    
    print("\n3️⃣ ENVIO VIA TELEGRAM:")
    print("• monitoring_service.py linha 125:")
    print("  self._notify_best_opportunities(opportunities)")
    print("• Envia TODAS as oportunidades encontradas no scan")
    print("• NÃO há filtro adicional de tempo")
    
    print("\n4️⃣ MONITORAMENTO (linha diferente):")
    print("• monitoring_service.py linha 144:")
    print("  active_opps = self.db.get_active_opportunities(min_hours_ahead=0.5)")
    print("• Este é para MONITORAR mudanças, não para ENVIAR")
    
    print("\n" + "=" * 60)
    print("🤔 ONDE ESTÁ O FILTRO DE 6 HORAS?")
    print("=" * 60)
    
    print("\n❌ NÃO ENCONTREI filtro específico de 6 horas no código!")
    print("\n💡 POSSÍVEIS CAUSAS:")
    
    print("\n1️⃣ API B365 limitação:")
    print("• A API pode estar retornando apenas jogos próximos")
    print("• Mesmo pedindo 72h, pode retornar só 6h")
    
    print("\n2️⃣ Filtro no banco de dados:")
    print("• database.py get_active_opportunities() usa min_hours_ahead=1 padrão")
    print("• Mas isso não é usado no envio inicial")
    
    print("\n3️⃣ Lógica de 'já enviado':")
    print("• is_opportunity_already_sent() pode estar bloqueando")
    print("• Jogos distantes podem já ter sido 'enviados' antes")
    
    print("\n4️⃣ Configuração externa:")
    print("• Alguma variável de ambiente ou config.json")
    print("• Pode ter filtro não visível no código")
    
    print("\n" + "=" * 60)
    print("✅ COMO GARANTIR 24 HORAS:")
    print("=" * 60)
    
    print("\n🔧 OPÇÃO 1 - Forçar hours_ahead:")
    print("• monitoring_service.py linha 109:")
    print("  hours_ahead=72  →  hours_ahead=48  # Manter 48h é suficiente")
    print("• prelive_scanner.py linha 68:")  
    print("  hours_ahead: int = 48  →  hours_ahead: int = 48  # Já está ok")
    
    print("\n🔧 OPÇÃO 2 - Adicionar filtro de tempo mínimo:")
    print("• Na _notify_best_opportunities() adicionar:")
    print("  # Só envia jogos com mais de X horas")
    print("  min_hours_before = 24")
    print("  filtered_opps = [opp for opp in opportunities")
    print("                   if hours_until_game(opp) >= min_hours_before]")
    
    print("\n🔧 OPÇÃO 3 - Filtrar na query do banco:")
    print("• database.py get_active_opportunities():")
    print("  min_hours_ahead: int = 1  →  min_hours_ahead: int = 24")
    print("• Mas isso afeta monitoramento também!")
    
    print("\n🔧 OPÇÃO 4 - Novo método específico:")
    print("• Criar get_opportunities_for_notification(min_hours=24)")
    print("• Usar apenas no envio inicial")
    print("• Manter get_active_opportunities() para monitoramento")
    
    print("\n" + "=" * 60)
    print("🎯 RECOMENDAÇÃO:")
    print("=" * 60)
    
    print("\n🏆 IMPLEMENTAR OPÇÃO 4 (mais limpa):")
    print("1. Criar novo método no database.py")
    print("2. Filtrar por tempo mínimo antes do jogo")
    print("3. Usar apenas no _notify_best_opportunities()")
    print("4. Não afetar monitoramento de linha")
    
    print("\n📝 CÓDIGO SUGERIDO:")
    print("-" * 30)
    print("# database.py")
    print("def get_opportunities_for_notification(self, min_hours_ahead: int = 24):")
    print("    cutoff_time = (datetime.utcnow() + timedelta(hours=min_hours_ahead))")
    print("    # SELECT onde start_utc > cutoff_time")
    print("")
    print("# monitoring_service.py") 
    print("def _notify_best_opportunities(self, opportunities):")
    print("    # Filtra apenas jogos com 24h+ de antecedência")
    print("    far_opps = self.db.get_opportunities_for_notification(24)")
    print("    # Intersecta com opportunities encontradas")
    print("    # Envia apenas essas")
    
    print("\n⚠️ IMPORTANTE:")
    print("• Não alterar get_active_opportunities() atual")
    print("• Monitoramento precisa continuar funcionando")
    print("• Apenas filtrar no ENVIO inicial")
    
    print(f"\n🔍 QUER QUE EU IMPLEMENTE ESTA SOLUÇÃO?")
    print("Adicionaria o filtro de 24h sem quebrar nada existente")

if __name__ == "__main__":
    analyze_timing_configuration()
