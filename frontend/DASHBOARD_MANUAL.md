# 🌐 DASHBOARD WEB - TennisIQ Bot

## 📊 Visão Geral

O Dashboard Web do TennisIQ Bot é uma **interface em tempo real** que permite monitorar todas as atividades do bot enquanto ele está rodando. É uma ferramenta completa de supervisão e análise.

## 🚀 Como Acessar

### Opção 1: Início Automático
```bash
# Execute o arquivo batch (recomendado)
iniciar_completo.bat
```
- ✅ Inicia dashboard + bot automaticamente
- 🌐 Abre navegador em http://localhost:5000
- 🔄 Sincronização automática

### Opção 2: Início Manual
```bash
# Terminal 1: Dashboard
python dashboard_web.py

# Terminal 2: Bot (em outra janela)
python bot.py
```

### Opção 3: Demo com Dados Simulados
```bash
# Para testar sem o bot rodando
python demo_dashboard.py
```

## 📈 Funcionalidades do Dashboard

### 🎯 **Status em Tempo Real**
- 🔴/🟢 Status do bot (Ativo/Inativo)
- ⏰ Última atualização
- 📡 Requests de API restantes
- ⏳ Próxima verificação

### 📊 **Estatísticas Gerais**
- 🎾 Total de partidas analisadas
- 📢 Total de sinais gerados
- 📈 Taxa de sucesso atual
- 💰 EV médio

### 🧠 **Análise de Estratégias**
- 🔄 Sinais invertidos (vantagem mental)
- 📊 Sinais tradicionais (filtros rígidos)
- 📈 Proporção entre estratégias

### 🎾 **Partidas Analisadas**
- 👥 Jogadores e placar atual
- 📊 Métricas: EV, MS, Timing, Mental Score
- ✅/❌ Decisão final (aprovada/rejeitada)
- 💭 Motivo da decisão

### 📢 **Sinais Gerados**
- 🎯 Jogador alvo da aposta
- 💰 Odd e EV calculado
- 🎨 Tipo: TRADICIONAL (azul) ou INVERTIDO (roxo)
- 🧠 Score mental (para invertidos)
- 🏆 Status: GREEN/RED/PENDING

## 🎨 Interface Visual

### 🎨 **Código de Cores**
- 🟢 **Verde**: Sucesso, bot ativo, resultados GREEN
- 🔴 **Vermelho**: Erro, bot inativo, resultados RED  
- 🟡 **Amarelo**: Pendente, atenção
- 🔵 **Azul**: Sinais tradicionais
- 🟣 **Roxo**: Sinais invertidos (vantagem mental)
- 🟠 **Laranja**: Status intermediário

### 📱 **Design Responsivo**
- 💻 Desktop: Layout em grid completo
- 📱 Mobile: Cards empilhados
- 🎯 Fácil navegação em qualquer dispositivo

## 🔄 Atualização de Dados

### ⚡ **Automática**
- 📡 Dashboard atualiza a cada **30 segundos**
- 🔄 Bot grava dados em **tempo real**
- 🌐 Interface atualiza automaticamente

### 📁 **Arquivos de Dados**
```
bot_status.json         # Status do bot
partidas_analisadas.json # Histórico de partidas  
sinais_gerados.json     # Histórico de sinais
dashboard_data.db       # Base de dados SQLite
```

## 📊 Métricas Importantes

### 🎯 **Seletividade do Sistema**
- ❌ **Rejeições**: ~60-70% das partidas
- ✅ **Aprovações**: ~30-40% das partidas
- 📢 **Sinais**: ~10-15% das partidas analisadas

### 🧠 **Distribuição de Estratégias**
- 📊 **Tradicionais**: 70% dos sinais
- 🧠 **Invertidos**: 30% dos sinais
- ⚡ **Mental Override**: Situações críticas

### 📈 **Performance Esperada**
- 🎯 **Taxa de Sucesso**: 65-75%
- 💰 **EV Médio**: +0.29
- 🚀 **Melhoria**: 0% → 70% (+∞%)

## 🔍 Como Interpretar os Dados

### 🎾 **Partidas Analisadas**
```
João Silva vs Pedro Costa  |  6-4,3-2
EV: 0.280  MS: 68%  Timing: 4  Mental: 120
⏰ 14:30:25 - SINAL_TRADICIONAL: Aprovado por filtros rígidos
```
- ✅ **Verde**: Sinal gerado
- 🔴 **Vermelho**: Rejeitado
- 📊 Métricas mostram qualidade da oportunidade

### 📢 **Sinais Gerados**
```
🎯 Ana Sousa | TRADICIONAL
Odd: 1.85  EV: +0.280  Confiança: 75.0%
✅ GREEN
```
- 🎨 **Cor da borda**: Tipo de estratégia
- 🏆 **Badge**: Resultado final
- 📊 **Métricas**: Qualidade do sinal

### 🧠 **Sinais Invertidos**
```
🎯 Pedro Costa | INVERTIDO  
Odd: 2.50  EV: +0.350  Confiança: 82.0%
💪 Score Mental: 285
🧠 Pós tie-break vencedor  🧠 Situação nada a perder
```
- 💜 **Borda roxa**: Estratégia invertida
- 🧠 **Fatores mentais**: Razões psicológicas
- 💪 **Score alto**: Maior confiança

## ⚠️ Solução de Problemas

### 🔴 **Dashboard não carrega**
```bash
# Verificar se Flask está instalado
pip install flask

# Verificar se porta 5000 está livre
netstat -an | findstr :5000
```

### 📭 **Sem dados no dashboard**
```bash
# Verificar se bot está rodando
python bot.py

# Ou gerar dados de teste
python demo_dashboard.py
```

### 🔄 **Dados não atualizam**
- ✅ Verificar conexão entre bot e dashboard
- 🔄 Refresh manual (botão no canto)
- 📁 Verificar se arquivos JSON existem

## 🎯 Dicas de Uso

### 👀 **Monitoramento Eficiente**
1. 📊 **Foque nas estatísticas gerais** para visão macro
2. 🎾 **Acompanhe partidas rejeitadas** para entender filtros
3. 🧠 **Monitore sinais invertidos** - são os mais valiosos
4. 📈 **Compare EV médio** com performance real

### 🎪 **Situações Especiais**
- 🚨 **Score Mental > 300**: Situação crítica detectada
- ⚡ **Timing Override**: Sistema ignorou horário restritivo  
- 🎯 **EV > 0.30**: Oportunidade premium
- 🔥 **3º sets**: Alta probabilidade de inversão

### 📱 **Acesso Remoto**
```
http://SEU_IP:5000
```
- 🌐 Dashboard acessível na rede local
- 📱 Use em tablet/celular para monitoramento móvel
- 🔒 Apenas na rede local (segurança)

## 🎉 Conclusão

O Dashboard Web é uma **ferramenta revolucionária** que transforma o monitoramento do bot de algo técnico em uma experiência visual e intuitiva. 

### 🚀 **Benefícios Principais**:
- 👁️ **Visibilidade total** do funcionamento do bot
- 📊 **Dados em tempo real** para decisões rápidas  
- 🧠 **Insights sobre estratégias** mental vs tradicional
- 📈 **Acompanhamento de performance** histórica
- 🎯 **Interface amigável** para usuários não-técnicos

**💡 Resultado**: Controle total sobre seu sistema de apostas automatizado!

---
*Dashboard TennisIQ - Transformando dados em insights visuais* 🎾📊
