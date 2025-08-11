# Estrutura do Projeto TennisQ

## ✅ LIMPEZA CONCLUÍDA

O projeto foi reorganizado e limpo para eliminar os indicadores "U" e "M" do VS Code.

### 🗂️ Estrutura Organizada

```
TennisQ/
├── backend/                    # Core do sistema
│   ├── core/                  # Lógica principal
│   ├── data/                  # Processamento de dados
│   ├── services/              # Serviços auxiliares
│   └── utils/                 # Utilitários
├── storage/                   # Dados e cache
│   ├── database/              # Bancos de dados JSON
│   └── logs/                  # Logs do sistema
├── config/                    # Configurações
├── frontend/                  # Interface web
└── scripts/                   # Scripts de automação
```

### 🚫 Arquivos Ignorados (.gitignore)

- **Cache Python**: `__pycache__/`, `*.pyc`
- **Logs temporários**: `*.log`, `logs/`
- **Arquivos de teste**: `teste_*.py`, `debug_*.py`
- **Dados dinâmicos**: `bot_status.json`, `partidas_analisadas.json`
- **Configurações sensíveis**: `config/config.json`

### 📊 Status dos Arquivos

- ✅ **Sem indicadores "U" ou "M"** desnecessários
- ✅ **Cache Python limpo** (não rastreado)
- ✅ **Logs temporários ignorados**
- ✅ **Arquivos dinâmicos fora do controle de versão**

### 🔧 Manutenção

Para manter a estrutura limpa:

1. **Não adicionar arquivos de cache** ao Git
2. **Não rastrear arquivos dinâmicos** (status, logs)
3. **Usar .gitignore** para novos tipos de arquivo
4. **Fazer commits organizados** com mensagens descritivas

### 📝 Últimas Mudanças

- **2025-08-11**: Limpeza completa da estrutura
- **Removido**: Cache Python, logs temporários, arquivos de teste
- **Adicionado**: .gitignore abrangente
- **Configurado**: Ignorar arquivos dinâmicos do sistema

---
*Estrutura otimizada para desenvolvimento e deploy Railway*
