# 📱 MODELOS DAS MENSAGENS DE SINAL - TennisIQ

### � **ESTRATÉGIA TRADICIONAL** (Prioridade 3)
```
🎾 TennisIQ -| Estratégia | Prioridade | Emoji | Odds | Quando é Enviada |
|------------|------------|-------|------|------------------|
| 🚀 **Alavancagem** | 5 | 🚀 | 1.20-1.40 | Dominância consolidada (1º set vencido + liderando 2º) |
| 🟣 **Invertida** | 5 | 🔁 | 1.8-2.2 | Vantagem mental detectada (score ≥200 + múltiplos fatores) |
| 🔥 **Tradicional** | 3 | 🔥 | 1.8-2.2 | Estatísticas sólidas padrão |l - Tradicional 🔥

{Oponente} vs {Jogador_Alvo}
⏰ {Horário_Brasília}

🚀 APOSTAR EM: {Jogador_Alvo} 🚀
💰 Odd: {Odd_Atual}
⚠️ Limite Mínimo: {Odd_Mínima} (não apostar abaixo)

🔗 Link direto: {Link_Bet365}

#TennisIQ
```

```
🎾 TennisIQ - Sinal - Tradicional 🔥

{Oponente} vs {Jogador_Alvo}
⏰ {Horário_Brasília}

🚀 APOSTAR EM: {Jogador_Alvo} 🚀
💰 Odd: {Odd_Atual}
⚠️ Limite Mínimo: {Odd_Mínima} (não apostar abaixo)

🔗 Link direto: {Link_Bet365}

#TennisIQ
```

### 📊 Características:
- **Título**: `🎾 TennisIQ - Sinal - Tradicional 🔥`
- **Emoji**: 🔥 (fogo - estratégia sólida)
- **Prioridade**: 3 (padrão)
- **Critérios**: EV ≥ 15%, odds 1.15-2.00, estatísticas sólidas

---

### 🟣 **ESTRATÉGIA INVERTIDA** (Prioridade 5) - Odds 1.8-2.2

```
🎾 TennisIQ - Sinal - Invertida 🔁

{Oponente} vs {Jogador_Alvo}
⏰ {Horário_Brasília}

🔁 APOSTAR EM: {Jogador_Alvo} 🚀
💰 Odd: {Odd_Alvo}
⚠️ Limite Mínimo: {Odd_Mínima} (não apostar abaixo)

🔗 Link direto: {Link_Bet365}

#TennisIQ
```

### 📊 Características:
- **Título**: `🎾 TennisIQ - Sinal - Invertida 🔁`
- **Emoji**: 🔁 (seta invertida)
- **Prioridade**: 5 (alta)
- **Critérios**: Vantagem mental detectada, score mental ≥ 200, **odds 1.8-2.2**

---

## 🚀 ESTRATÉGIA ALAVANCAGEM (DOMINÂNCIA)

```
🎾 TennisIQ - Sinal - Alavancagem 🚀

{Oponente} vs {Jogador_Alvo}
⏰ {Horário_Brasília}

🚀 APOSTAR EM: {Jogador_Alvo} 🚀
💰 Odd: {Odd_Alvo}
⚠️ Limite Mínimo: {Odd_Mínima} (não apostar abaixo)

🔗 Link direto: {Link_Bet365}

#TennisIQ
```

### 📊 Características:
- **Título**: `🎾 TennisIQ - Sinal - Alavancagem 🚀`
- **Emoji**: 🚀 (foguete - alavancagem)
- **Prioridade**: 5 (máxima)
- **Critérios**: 1º set vencido, dominando 2º set, momentum ≥65%, odds 1.20-1.40

---

## 🔧 COMPONENTES TÉCNICOS

### ⏰ **Horário**:
```python
# Horário de Brasília (UTC-3)
agora = datetime.now(timezone(timedelta(hours=-3)))
horario = agora.strftime("%H:%M")
```

### 💰 **Cálculo de Odd Mínima**:
```python
def calcular_odd_minima(self, odd_atual):
    # Margem de segurança de 5%
    return round(odd_atual * 0.95, 2)
```

### 🔗 **Link Bet365**:
```python
# Geração automática via bet365_link_manager
bet365_link = bet365_manager.generate_link(event_id)
```

---

## 📊 SISTEMA DE PRIORIDADES

| Estratégia | Prioridade | Emoji | Quando é Enviada |
|------------|------------|-------|------------------|
| 🚀 **Alavancagem** | 5 | 🚀 | Dominância consolidada (1º set vencido + liderando 2º) |
| 🟣 **Invertida** | 5 | 🔁 | Vantagem mental detectada (jogador perdendo mas superior) |
| � **Tradicional** | 3 | � | Estatísticas sólidas padrão |

### 🎯 **Ordem de Execução**:
1. **Primeiro**: Verifica se há oportunidade de **Alavancagem**
2. **Segundo**: Se não houver alavancagem, verifica **Invertida**  
3. **Terceiro**: Se nenhuma das especiais, aplica **Tradicional**

---

## 📝 LOGS ESPECÍFICOS

### 🚀 **Log Alavancagem**:
```json
{
  "timestamp": "2025-08-11T15:30:00",
  "tipo": "APOSTA_ALAVANCAGEM",
  "partida_original": "Jogador vs Oponente",
  "jogador_alvo": "Jogador",
  "odd_alvo": 1.35,
  "momentum_score": 72,
  "ev_estimado": 18.5,
  "confianca": 85,
  "justificativa": "Dominando após vencer 1º set"
}
```

### 🟣 **Log Invertida**:
```json
{
  "timestamp": "2025-08-11T15:30:00", 
  "tipo": "APOSTA_INVERTIDA",
  "partida_original": "Jogador vs Oponente",
  "target_invertido": "Jogador",
  "odd_invertida": 2.10,
  "score_mental": 8.5,
  "fatores": ["melhor_ranking", "head_to_head_positivo"],
  "ev_estimado": 22.3,
  "confianca": 78
}
```

---

## ✅ RESUMO DOS FORMATOS

- **📱 Todos os sinais**: Formato visual consistente com emojis
- **⏰ Horário**: Sempre em Brasília (UTC-3)  
- **💰 Odds**: Com limite mínimo de segurança (-5%)
- **🔗 Links**: Bet365 automático quando disponível
- **#️⃣ Hashtag**: `#TennisIQ` em todos os sinais
- **🎯 Identificação**: Clara diferenciação entre estratégias

**🚀 Sistema completo e operacional no Railway!**
