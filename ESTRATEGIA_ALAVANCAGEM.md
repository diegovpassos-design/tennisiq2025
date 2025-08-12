# 🚀 ESTRATÉGIA DE ALAVANCAGEM - TENNISIQ

## 📋 VISÃO GERAL

A **Estratégia de Alavancagem** é uma nova funcionalidade do TennisIQ que identifica oportunidades de apostas em jogadores dominantes que estão consolidando sua vantagem durante a partida. Esta estratégia complementa as estratégias Tradicional e Invertida já existentes.

## 🎯 OBJETIVO

Capitalizar momentos onde um jogador demonstrou superioridade clara e está consolidando sua vantagem, oferecendo apostas de baixo risco com retorno moderado.

## ✅ CRITÉRIOS DA ESTRATÉGIA

Para que um sinal de alavancagem seja enviado, **TODOS** os critérios abaixo devem ser atendidos:

### 1. 🏆 **Primeiro Set Terminado**
- O primeiro set da partida deve ter sido concluído
- Formato aceito: "6-4, 3-2" (primeiro set 6-4, segundo set em andamento)

### 2. 🥇 **Jogador Ganhou o Primeiro Set**
- O jogador da oportunidade deve ter vencido o primeiro set
- Comprova superioridade inicial

### 3. 📈 **Ganhando o Segundo Set**
- Deve estar liderando o segundo set no momento da análise
- Demonstra continuidade da dominância

### 4. 📊 **Superioridade Estatística**
- Momentum Score ≥ 65%
- Confirma que é estatisticamente superior ao oponente

### 5. 💰 **Odd Específica**
- Odd entre **1.20 e 1.40**
- Range restrito para minimizar riscos

## 🔄 COMPARAÇÃO COM OUTRAS ESTRATÉGIAS

| Estratégia | Odds | Foco | Risco | Conceito |
|------------|------|------|--------|----------|
| 🔵 **Tradicional** | 1.8 - 2.2 | Estatísticas | Médio | Jogador com vantagem estatística |
| 🟣 **Invertida** | ≥ 1.8 | Vantagem Mental | Alto | Adversário com vantagem psicológica |
| 🚀 **Alavancagem** | 1.2 - 1.4 | Dominância | Baixo | Favorito consolidando superioridade |

## 📱 FORMATO DO SINAL

```
🎾 TennisIQ - Sinal - Alavancagem 🚀

Oponente vs Jogador Target
⏰ 14:32

🚀 APOSTAR EM: Jogador Target 🚀
💰 Odd: 1.35
⚠️ Limite Mínimo: 1.31 (não apostar abaixo)

🔗 Link direto: [Link da Bet365]

#TennisIQ
```

## 🎮 EXEMPLOS PRÁTICOS

### ✅ APROVADO - Caso Ideal
```
📊 Situação: Rafael Nadal vs Novak Djokovic
🏆 Placar: 6-3, 4-2
📈 Momentum: 78%
💰 Odd: 1.32
🎯 Resultado: SINAL ENVIADO ✅
```
**Por que aprovado?**
- ✅ 1º set terminou (6-3)
- ✅ Nadal ganhou o 1º set
- ✅ Nadal lidera 2º set (4-2)
- ✅ Momentum 78% > 65%
- ✅ Odd 1.32 está entre 1.20-1.40

### ❌ REJEITADO - Odd Alta
```
📊 Situação: Carlos Alcaraz vs Daniil Medvedev
🏆 Placar: 7-5, 3-1
📈 Momentum: 82%
💰 Odd: 1.48
🎯 Resultado: REJEITADO ❌
```
**Por que rejeitado?**
- ❌ Odd 1.48 > 1.40 (fora do range)

### ❌ REJEITADO - Perdeu 1º Set
```
📊 Situação: Stefanos Tsitsipas vs Alexander Zverev
🏆 Placar: 4-6, 3-1
📈 Momentum: 71%
💰 Odd: 1.38
🎯 Resultado: REJEITADO ❌
```
**Por que rejeitado?**
- ❌ Tsitsipas perdeu o 1º set (4-6)

## 🔧 IMPLEMENTAÇÃO TÉCNICA

### Arquivos Envolvidos
- `backend/core/detector_alavancagem.py` - Detector principal
- `backend/core/bot.py` - Integração com o sistema
- `demonstracao_alavancagem.py` - Demonstração e testes

### Fluxo de Análise
1. **Coleta de Dados**: Bot identifica oportunidade
2. **Análise Mental**: Verifica vantagem mental (estratégia invertida)
3. **Análise Alavancagem**: Verifica critérios de alavancagem
4. **Priorização**: Alavancagem > Invertida > Tradicional
5. **Envio**: Sinal formatado e enviado via Telegram

## 📊 LOGS E RASTREAMENTO

### Arquivo de Log
- `apostas_alavancagem.json` - Histórico de apostas de alavancagem

### Dados Salvos
```json
{
  "timestamp": "2025-08-11T...",
  "tipo": "APOSTA_ALAVANCAGEM",
  "jogador_alvo": "Rafael Nadal",
  "odd_alvo": 1.32,
  "momentum_score": 78,
  "justificativa": "Alavancagem: Rafael Nadal ganhou 1º set...",
  "confianca": "ALTA"
}
```

## 🎨 DASHBOARD INTEGRATION

A estratégia de alavancagem está integrada ao dashboard com:
- **Tipo**: "ALAVANCAGEM"
- **Cor**: 🚀 (emoji distintivo)
- **Métricas**: Odds, momentum, justificativa
- **Rastreamento**: Logs separados das outras estratégias

## 🚨 AVISOS IMPORTANTES

1. **Range de Odds Restrito**: Apenas 1.20-1.40 para controle de risco
2. **Critérios Rígidos**: Todos os 5 critérios devem ser atendidos
3. **Complementar**: Não substitui outras estratégias, as complementa
4. **Timing Específico**: Apenas quando 1º set terminou e 2º set em andamento

## ✅ STATUS

- ✅ **Implementado**: Detector de alavancagem
- ✅ **Integrado**: Sistema principal do bot
- ✅ **Testado**: Casos de uso validados
- ✅ **Documentado**: Guia completo criado
- ✅ **Pronto**: Sistema operacional

---

**Data de Implementação**: 11/08/2025  
**Versão**: 1.0  
**Status**: Operacional  
**Desenvolvedor**: Sistema TennisIQ
