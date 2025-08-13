
🚀 DEPLOY FINAL - RATE LIMITING CORRIGIDO
============================================================
📅 Data: 2025-08-13 13:11:06

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
