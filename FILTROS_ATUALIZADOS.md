# 🎾 FILTROS ATUALIZADOS - TENNISQ

**Data da Atualização:** 27/08/2025 23:30

## 📋 MUDANÇAS IMPLEMENTADAS

### 🎯 **1. FILTRO DE EV RESTRITO**
- **ANTES**: EV entre 3% - 25%
- **AGORA**: EV entre 10% - 15%
- **Arquivo**: `backend/core/prelive_scanner.py` - método `_should_bet_simple_aggressive()`

### 👩‍🎾 **2. FILTRO DE JOGOS FEMININOS**
- **NOVO**: Apenas jogos femininos (individuais e duplas)
- **BLOQUEIO**: Todos os jogos masculinos são ignorados
- **Arquivo**: `backend/core/prelive_scanner.py` - método `_is_female_match()`

#### **Critérios de Detecção de Jogos Femininos:**
1. **Liga**: WTA, Women, Ladies, Female, ITF Women, etc.
2. **Nomes**: Indicadores femininos como Anna, Maria, Elena, etc.
3. **Duplas**: Formato com "/" indicando duplas femininas
4. **Top Players**: Lista de jogadoras conhecidas (Swiatek, Sabalenka, etc.)

### 📊 **3. PARÂMETROS ATUALIZADOS**

```python
# monitoring_service.py
opportunities = self.scanner.scan_opportunities(
    hours_ahead=72,
    min_ev=0.10,   # 10% mínimo (era 0.5%)
    odd_min=1.80,  
    odd_max=2.40   
)

# prelive_scanner.py  
def _should_bet_simple_aggressive(self, ev: float, odds: float):
    # EV entre 10% - 15%
    if ev < 0.10 or ev > 0.15:
        return False
```

### 💬 **4. NOTIFICAÇÕES TELEGRAM ATUALIZADAS**
- **Título**: "🎾 OPORTUNIDADE FEMININA"
- **EV**: Mostra "(10-15% range)"
- **Resumo**: "👩‍🎾 X oportunidades FEMININAS enviadas!"

### 📈 **5. NÍVEIS DE CONFIANÇA AJUSTADOS**
- **ALTA**: EV ≥ 12% + probabilidade entre 30%-70%
- **MÉDIA**: EV ≥ 10%
- **BAIXA**: EV < 10%

## ✅ **RESULTADO ESPERADO**

O sistema agora irá:
- ✅ Detectar apenas jogos de tênis feminino
- ✅ Filtrar apenas oportunidades com EV entre 10%-15%
- ✅ Ignorar completamente jogos masculinos
- ✅ Enviar notificações mais específicas
- ✅ Ser mais seletivo (menos oportunidades, maior qualidade)

## 🔧 **ARQUIVOS MODIFICADOS**

1. `backend/core/prelive_scanner.py`
   - Novo método `_is_female_match()`
   - Filtro EV 10%-15%
   - Filtro de gênero no scan principal

2. `backend/services/monitoring_service.py`
   - Parâmetro min_ev=0.10
   - Mensagens Telegram atualizadas

## 🚀 **PRÓXIMOS PASSOS**

Para ativar as mudanças:
1. Reiniciar o bot: `python run_bot.py`
2. O sistema começará a aplicar os novos filtros
3. Apenas jogos femininos com EV 10-15% serão notificados

---
**Sistema otimizado para máxima precisão em oportunidades femininas! 🎯**
