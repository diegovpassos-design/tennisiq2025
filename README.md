# TennisQ Pré-Live 🎾

Sistema automatizado para identificar oportunidades de apostas pré-live no tênis, calculando valor esperado (EV) e enviando notificações via Telegram.

## 🎯 Funcionalidades

- **Escaneamento Automático**: Monitora jogos de tênis nas próximas 72 horas
- **Cálculo de EV**: Compara probabilidades do modelo com odds do mercado
- **Monitoramento de Linha**: Acompanha movimento das odds para calcular CLV
- **Notificações Telegram**: Envia alertas automáticos das melhores oportunidades
- **Banco de Dados**: Armazena histórico completo para análise

## 🚀 Deploy no Railway

### 1. Preparação

1. **Fork este repositório** para sua conta do GitHub

2. **Configure as variáveis de ambiente** no Railway:
   - `API_KEY`: Sua chave da BetsAPI/b365api
   - `TELEGRAM_TOKEN`: Token do seu bot do Telegram
   - `CHAT_ID`: ID do chat/canal para receber notificações
   - `API_BASE_URL`: https://api.b365api.com

### 2. Deploy

1. Conecte seu repositório ao Railway
2. O Railway irá detectar automaticamente o `Procfile`
3. O sistema iniciará automaticamente

### 3. Configuração do Telegram

1. Crie um bot com o @BotFather
2. Obtenha o token do bot
3. Adicione o bot ao seu grupo/canal
4. Obtenha o chat_id

## 📊 Como Funciona

### Algoritmo Principal

1. **Coleta de Dados**:
   - Busca jogos futuros via API
   - Obtém odds pré-jogo do mercado "Match Winner"

2. **Cálculo de Probabilidades**:
   - Remove margem da casa das odds
   - Aplica modelo próprio para estimar probabilidades "justas"

3. **Identificação de Oportunidades**:
   - Calcula EV: `EV = p_model * (odds - 1) - (1 - p_model)`
   - Filtra por EV mínimo (padrão: 1.5%)
   - Considera apenas odds entre 1.70 - 2.30

4. **Monitoramento**:
   - Acompanha movimento de linha
   - Calcula CLV (Closing Line Value)
   - Envia notificações automáticas

### Critérios de Filtro

- **EV Mínimo**: 1.5%
- **Faixa de Odds**: 1.70 - 2.30
- **Confiança**: ALTA/MÉDIA/BAIXA baseada em EV e probabilidade
- **Antecedência**: 0.5h - 72h antes do jogo

## 🔧 Estrutura do Projeto

```
TennisQ/
├── backend/
│   ├── core/
│   │   ├── prelive_scanner.py    # Scanner principal
│   │   └── database.py           # Gerenciamento de dados
│   ├── services/
│   │   └── monitoring_service.py # Serviço de monitoramento
│   ├── config/
│   │   └── config.json          # Configurações
│   └── app.py                   # Aplicação principal
├── storage/
│   ├── database/                # Banco SQLite
│   └── exports/                 # Exportações
├── Procfile                     # Configuração Railway
├── requirements.txt             # Dependências Python
└── test_system.py              # Script de teste
```

## 📱 Notificações

O sistema envia notificações automáticas via Telegram:

- **Início do sistema**
- **Novas oportunidades encontradas** (top 5)
- **Erros críticos**
- **Health checks** (status periódico)

### Exemplo de Notificação:

```
🎾 NOVAS OPORTUNIDADES PRÉ-LIVE

1. Djokovic vs Nadal
📍 ATP Masters 1000
🎯 Lado: HOME | Odd: 1.95
📊 EV: 3.2% | Confiança: ALTA
⏰ Início: 2025-08-23 15:00 UTC

💡 Encontradas 8 oportunidades no total
```

## 🧪 Teste Local

Execute o script de teste antes do deploy:

```bash
python test_system.py
```

Este script verifica:
- ✅ Configuração válida
- ✅ Conexão com API
- ✅ Funcionamento do Telegram
- ✅ Banco de dados
- ✅ Scanner de oportunidades

## ⚙️ Configuração Avançada

### Ajuste de Parâmetros

No arquivo `monitoring_service.py`, você pode ajustar:

```python
# Escaneamento de oportunidades
opportunities = scanner.scan_opportunities(
    hours_ahead=72,      # Janela de tempo
    min_ev=0.015,        # EV mínimo (1.5%)
    odd_min=1.70,        # Odd mínima
    odd_max=2.30         # Odd máxima
)
```

### Frequência de Execução

- **Scan completo**: A cada 3 horas
- **Monitoramento de linha**: A cada 30 minutos
- **Health check**: A cada 1 hora

## 📈 Modelo de Probabilidades

O sistema inclui um modelo básico que você pode expandir:

### Atual (Placeholder):
- Probabilidade base: 50%
- Ajustes simples por superfície/forma

### Recomendado para Expansão:
- **Elo por superfície** (clay, hard, grass, indoor)
- **Forma recente** (últimos 5-10 jogos)
- **Head-to-head** (histórico entre jogadores)
- **Fatores contextuais** (fadiga, viagem, condições)

## 🔍 Monitoramento

### Logs no Railway:
- Acompanhe execução via logs do Railway
- Health checks automáticos
- Notificações de erro via Telegram

### Dados Armazenados:
- Histórico de oportunidades
- Movimento de linha completo
- Estatísticas de performance
- CLV (Closing Line Value)

## 💡 Estratégia de Uso

1. **Entrada Antecipada**: 1-3 dias antes do jogo
2. **Filtros Conservadores**: EV > 2% para maior confiança
3. **Gestão de Banca**: Stake proporcional à confiança
4. **Análise de CLV**: Mede qualidade das entradas

## 🆘 Suporte

- **Logs**: Verifique logs no Railway para debugging
- **Telegram**: Bot enviará notificações de erro
- **Health Check**: Sistema se auto-monitora

## 📄 Licença

Projeto pessoal para identificação de oportunidades de apostas esportivas.

---

**⚠️ Disclaimer**: Este sistema é para fins educacionais e de análise. Apostas esportivas envolvem risco. Aposte com responsabilidade.
