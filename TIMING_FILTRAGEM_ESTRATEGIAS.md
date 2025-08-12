# ⏰ FILTRAGEM DE TEMPO POR ESTRATÉGIA - TennisIQ

## 🚀 **ESTRATÉGIA ALAVANCAGEM** (Timing Otimizado)

### ✅ **SITUAÇÕES PRIORITÁRIAS (Timing Override):**
- **🎾 2º Set + Momentum ≥65%**: Liberado SEMPRE (qualquer horário)
- **🔥 1º Set Final + Momentum ≥70%**: Liberado SEMPRE (qualquer horário)

### ⏰ **HORÁRIOS NORMAIS:**
- **06:00 - 23:00**: ✅ **SEMPRE LIBERADO**
- **00:00 - 06:00**: ✅ Liberado SE momentum ≥70%

### 🔄 **LÓGICA ESPECÍFICA:**
```python
# Timing muito flexível para alavancagem devido à especificidade
if '2º set' in contexto and momentum >= 65:
    return True  # OVERRIDE TOTAL
if '1º set' in contexto and momentum >= 70:
    return True  # FINAL 1º SET OK
if 6 <= hora <= 23:
    return True  # HORÁRIO NORMAL
if 0 <= hora <= 6 and momentum >= 70:
    return True  # MADRUGADA COM MOMENTUM ALTO
```

---

## 🟣 **ESTRATÉGIA INVERTIDA** (Timing Flexível)

### ✅ **SITUAÇÕES CRÍTICAS (Timing Override):**
- **🚨 Score Mental ≥300**: Liberado SEMPRE (qualquer horário)
- **⚡ 3º Set ou Tie-break**: Liberado SEMPRE (qualquer horário)

### ⏰ **HORÁRIOS NORMAIS:**
- **06:00 - 23:00**: ✅ **SEMPRE LIBERADO**
- **00:00 - 06:00**: ✅ Liberado SE score mental ≥250

### 🔄 **LÓGICA ESPECÍFICA:**
```python
# Timing flexível para situações de vantagem mental
if score_mental >= 300:
    return True  # SCORE MUITO ALTO
if '3º set' in contexto or 'tie-break' in contexto:
    return True  # SITUAÇÃO CRÍTICA
if 6 <= hora <= 23:
    return True  # HORÁRIO NORMAL
if 0 <= hora <= 6 and score_mental >= 250:
    return True  # MADRUGADA COM SCORE ALTO
```

---

## 🔥 **ESTRATÉGIA TRADICIONAL** (Timing Rígido)

### ❌ **BLOQUEIOS RIGOROSOS:**
- **🌙 00:00 - 06:00**: ❌ **SEMPRE BLOQUEADO**
- **📊 Prioridade <3**: ❌ **SEMPRE BLOQUEADO**

### ⏰ **HORÁRIOS ACEITOS:**
- **08:00 - 22:00**: ✅ **HORÁRIO PREFERIDO**
- **06:00 - 08:00 e 22:00 - 23:00**: ⚠️ Marginal (só se prioridade ≥3)

### 🔄 **LÓGICA ESPECÍFICA:**
```python
# Timing rígido para estratégia tradicional
if prioridade < 3:
    return False  # PRIORIDADE INSUFICIENTE
if 0 <= hora <= 6:
    return False  # MADRUGADA BLOQUEADA
if 8 <= hora <= 22:
    return True  # HORÁRIO COMERCIAL
if prioridade >= 3:
    return True  # MARGINAL COM PRIORIDADE
```

---

## 📊 **COMPARATIVO DE FLEXIBILIDADE**

| Estratégia | Flexibilidade | Madrugada | Override | Prioridade |
|------------|---------------|-----------|----------|------------|
| 🚀 **Alavancagem** | 🟢 **MUITO ALTA** | ✅ Se momentum ≥70% | ✅ 2º set + momentum | 5 |
| 🟣 **Invertida** | 🟡 **ALTA** | ✅ Se score ≥250 | ✅ Situações críticas | 5 |
| 🔥 **Tradicional** | 🔴 **BAIXA** | ❌ Sempre bloqueada | ❌ Sem override | 3 |

---

## 🎯 **CONTEXTO DA PARTIDA**

### 🔍 **IDENTIFICAÇÃO AUTOMÁTICA:**
```python
def identificar_contexto_partida(self, oportunidade):
    # Detecta automaticamente:
    # - 1º set em andamento
    # - 2º set em andamento  
    # - 3º set em andamento
    # - Tie-breaks
    # - Sets empatados
```

### 📈 **DETECÇÃO DE SETS:**
- **1º Set**: Sem sets finalizados no placar
- **2º Set**: 1 set finalizado (6- ou 7- uma vez)
- **3º Set**: 2+ sets finalizados
- **Tie-break**: Presença de 7-6 ou 6-7

---

## ⚡ **TIMING OVERRIDE ATIVO**

### 🚀 **ALAVANCAGEM - Casos Especiais:**
- ✅ **2º set iniciando** + jogador dominando
- ✅ **Final do 1º set** + momentum consolidado
- ✅ **Qualquer horário** se critérios atendidos

### 🟣 **INVERTIDA - Casos Especiais:**
- ✅ **3º set decisivo** + vantagem mental
- ✅ **Tie-break** + score mental alto
- ✅ **Score excepcional** (≥300 pontos)

### 🔥 **TRADICIONAL - Sem Override:**
- ❌ **Sem exceções** para timing
- ❌ **Filtros sempre aplicados**
- ❌ **Madrugada sempre bloqueada**

---

## 📈 **RESULTADO DA OTIMIZAÇÃO**

### ✅ **BENEFÍCIOS IMPLEMENTADOS:**
1. **🚀 Alavancagem**: Timing otimizado para **2º set** (melhor momento)
2. **🟣 Invertida**: Flexibilidade para **situações críticas**
3. **🔥 Tradicional**: Mantém **qualidade alta** com timing rígido

### 🎯 **PRECISÃO TEMPORAL:**
- **Horário Brasília**: UTC-3 sempre
- **Contexto Inteligente**: Detecção automática de sets
- **Override Condicional**: Baseado em métricas específicas

**🚀 Sistema de timing inteligente implementado e ativo no Railway!**
