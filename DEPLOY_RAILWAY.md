# 🚀 DEPLOY RAILWAY - INSTRUÇÕES FINAIS

## ✅ ARQUIVOS CRIADOS:

1. **Procfile** ✅ (define web + worker processes)
2. **railway.json** ✅ (configuração da plataforma)
3. **config_production.py** ✅ (configuração de produção)
4. **backend/data/database.py** ✅ (manager PostgreSQL + SQLite)
5. **.gitignore** ✅ (exclusões para deploy)
6. **README.md** ✅ (documentação)
7. **requirements.txt** ✅ (dependências atualizadas)

## 🔥 PRÓXIMOS PASSOS:

### 1️⃣ CRIAR CONTA RAILWAY
- Acesse: https://railway.app/
- Faça login com GitHub
- Gratuito: $5 de crédito inicial

### 2️⃣ UPLOAD PARA GITHUB
```bash
# No diretório TennisQ:
git init
git add .
git commit -m "Deploy Railway - TennisIQ Bot"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/tennisiq.git
git push -u origin main
```

### 3️⃣ CONECTAR RAILWAY
1. No Railway dashboard: **"New Project"**
2. Selecione: **"Deploy from GitHub repo"**
3. Escolha o repositório **tennisiq**
4. Railway detectará automaticamente o **Procfile**

### 4️⃣ CONFIGURAR VARIÁVEIS DE AMBIENTE
No Railway dashboard > Variables:
```
TELEGRAM_BOT_TOKEN=seu_token_bot_telegram
TELEGRAM_CHAT_ID=seu_chat_id
TELEGRAM_CHANNEL_ID=seu_channel_id  
```

### 5️⃣ ADICIONAR POSTGRESQL
1. Railway dashboard > **"+ New"**
2. Selecione **"PostgreSQL"**
3. Railway conectará automaticamente via `DATABASE_URL`

## 🎯 RESULTADO FINAL:

✅ **Web Process**: Dashboard acessível via URL Railway  
✅ **Worker Process**: Bot rodando 24/7 em background  
✅ **PostgreSQL**: Database em nuvem para dados  
✅ **Auto-Deploy**: Commits automáticos via GitHub  

## 📊 CUSTOS:
- **$5/mês**: Inclui tudo (hosting + PostgreSQL + domínio)
- **99.9% uptime**: Garantia de disponibilidade
- **Auto-scaling**: Ajuste automático de recursos

## ⚡ COMANDOS LOCAIS DE TESTE:
```bash
# Testar localmente antes do deploy:
python run_dashboard.py    # http://localhost:5000
python run_bot.py         # Bot rodando localmente
```

---
**🎾 TennisIQ está pronto para a nuvem! 🚀**
