# 🎾 TennisIQ - Bot de Análise de Tennis

Sistema inteligente de análise de oportunidades em partidas de tênis com estratégias tradicionais e invertidas.

## 🚀 Deploy Railway

Este projeto está configurado para deploy automático no Railway.

### Variáveis de Ambiente Necessárias:

```
TELEGRAM_BOT_TOKEN=seu_token_aqui
TELEGRAM_CHAT_ID=seu_chat_id_aqui  
TELEGRAM_CHANNEL_ID=seu_channel_id_aqui
DATABASE_URL=postgresql://... (configurado automaticamente pelo Railway)
```

### Serviços:

- **Web Process**: Dashboard Flask (run_dashboard.py)
- **Worker Process**: Bot de Monitoramento 24/7 (run_bot.py)

## 🔧 Configuração Local

1. Clone o repositório
2. Instale as dependências: `pip install -r requirements.txt`
3. Configure as variáveis de ambiente
4. Execute: `python run_bot.py` e `python run_dashboard.py`

## 📊 Features

- ✅ Análise de EV (Expected Value)
- ✅ Momentum Score
- ✅ Estratégias Invertidas 
- ✅ Dashboard Web em tempo real
- ✅ Notificações Telegram
- ✅ Links diretos Bet365
- ✅ Backup automático

## 🎯 Performance

Taxa de acerto: ~66.7% (8 greens / 12 apostas)
