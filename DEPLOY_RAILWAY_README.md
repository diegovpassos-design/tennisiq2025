# TennisQ v2.0 - Sistema de Oportunidades Pré-Live

## 🚀 DEPLOY RAILWAY PRONTO

### ✅ Arquivos Principais
- `run.py` - Arquivo principal de execução
- `Procfile` - Configuração Railway: `web: python run.py`  
- `requirements.txt` - Dependências atualizadas
- `railway.json` - Configuração de deploy

### 🎯 Funcionalidades
- **Scanner Inteligente**: Detecta oportunidades com EV > 1.5%
- **Anti-Duplicatas**: Evita envio repetido de notificações
- **Notificação de Início**: Informa quando sistema inicia
- **API Health**: Endpoints `/health` e `/status` para Railway
- **Modelo Sofisticado**: Cálculo de probabilidades com múltiplos fatores

### 🔧 Variáveis de Ambiente Necessárias no Railway
```
API_KEY=sua_betsapi_key
TELEGRAM_TOKEN=seu_bot_token
CHAT_ID=id_do_canal
API_BASE_URL=https://api.b365api.com
PORT=8080
```

### 📊 Estrutura do Deploy
```
TennisQ/
├── run.py              # 🚀 Entrada principal
├── backend/
│   ├── app.py         # Flask app para Railway
│   ├── core/          # Scanner + Modelo + Database
│   └── services/      # Monitoramento + Telegram
├── Procfile           # Railway: web: python run.py
├── requirements.txt   # Dependências
└── railway.json       # Config de deploy
```

### ⚡ Comandos Railway
1. Conectar ao repositório: `tennisiq2025`
2. Configurar variáveis de ambiente
3. Deploy automático ativado no push

### ✅ Status do Sistema
- **Testado**: 100% funcional localmente
- **Commit**: ba31ced - Sistema completo
- **Push**: Enviado para GitHub
- **Pronto**: Para deploy no Railway

## 📱 Notificações Telegram
- Início do sistema automático
- Oportunidades individuais formatadas
- Anti-spam integrado
- Canal configurado via CHAT_ID

## 🎾 SISTEMA PRONTO PARA PRODUÇÃO!
