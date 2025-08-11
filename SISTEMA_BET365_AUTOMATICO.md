# Sistema Automático de Links da Bet365

## 📋 Visão Geral

O **Bet365 Link Manager** é um sistema robusto que gerencia automaticamente os links diretos da Bet365, capturando e atualizando o parâmetro `_h` quando necessário.

## 🚀 Funcionalidades

### ✅ Recursos Implementados

1. **Captura Automática**: Extrai o parâmetro `_h` atual da página da Bet365
2. **Validação de Links**: Testa se os links estão funcionando antes de usar
3. **Atualização Proativa**: Monitora e atualiza links automaticamente
4. **Fallback Manual**: Permite definição manual de parâmetros
5. **Histórico**: Mantém registro de todas as atualizações
6. **Notificações**: Avisa via Telegram quando links são atualizados

### 🔄 Funcionamento Automático

O sistema funciona em background integrado ao bot principal:

- ✅ **Verificação Automática**: A cada 2 horas verifica se os links funcionam
- ✅ **Atualização Inteligente**: Quando detecta link quebrado, tenta capturar novo parâmetro
- ✅ **Notificação Proativa**: Informa via Telegram sobre atualizações ou problemas
- ✅ **Persistência**: Salva configurações para não perder dados entre reinicializações

## 🛠️ Uso Manual

### Teste do Sistema
```bash
# Teste completo das funcionalidades
python teste_bet365_manager.py

# Interface interativa para gerenciamento manual
python teste_bet365_manager.py manual
```

### Comandos Manuais Disponíveis

1. **Ver Status**: Verificar estado atual dos links
2. **Atualizar Automaticamente**: Forçar captura de novo parâmetro
3. **Definir Manual**: Inserir parâmetro `_h` manualmente
4. **Testar Links**: Validar se link atual funciona
5. **Gerar Links**: Criar links de teste
6. **Ver Histórico**: Consultar atualizações anteriores

## 📁 Arquivos do Sistema

### Código Principal
- `backend/services/bet365_link_manager.py` - Classe principal do gerenciador
- `backend/core/bot.py` - Integração com o bot principal
- `teste_bet365_manager.py` - Scripts de teste e interface manual

### Configuração
- `config/bet365_config.json` - Armazena parâmetro atual e histórico

```json
{
  "h_param": "LKUUnzn5idsD_NCCi9iyvQ%3D%3D",
  "last_update": "2025-08-05T20:00:00",
  "update_history": [...]
}
```

## 🔧 Integração com Bot

### Uso Automático
O bot agora usa automaticamente o sistema:

```python
# Antes (estático)
bet365_link = f"https://www.bet365.bet.br/?_h=FIXO&btsffd=1#/IP/EV{event_id}C13"

# Agora (dinâmico)
bet365_link = bet365_manager.generate_link(event_id)
```

### Verificação Proativa
Durante o ciclo do bot:
- 🔍 Verifica links a cada 2 horas
- 🔄 Atualiza automaticamente se necessário
- 📱 Notifica sobre mudanças via Telegram

## ⚠️ Quando Usar Manualmente

### Situações que Exigem Intervenção Manual

1. **Links Quebrados**: Quando sistema automático falha
2. **Novos Parâmetros**: Para testar parâmetros obtidos externamente
3. **Manutenção**: Para verificar status e histórico
4. **Debug**: Para diagnosticar problemas

### Como Obter Novo Parâmetro `_h`

Se o sistema automático falhar:

1. **Acesse a Bet365** no navegador
2. **Abra DevTools** (F12)
3. **Vá para Network** e recarregue a página
4. **Procure por requests** que contenham `_h=`
5. **Copie o valor** do parâmetro
6. **Use o comando manual** para definir

## 📊 Monitoramento

### Logs do Sistema
```
🔗 Inicializando Bet365 Link Manager...
✅ Bet365 Link Manager inicializado com parâmetro manual
✅ Bet365 links prontos: LKUUnzn5idsD_NCCi9iy...
🔍 Verificando links da Bet365...
⚠️ Links da Bet365 não estão funcionando, tentando atualizar...
✅ Links da Bet365 atualizados com sucesso
```

### Notificações Telegram
- 🔗 "Links da Bet365 foram atualizados automaticamente"
- ⚠️ "ATENÇÃO: Links da Bet365 podem estar com problema"

## 🎯 Benefícios da Solução

### Para Usuários
- ✅ **Links Sempre Funcionando**: Atualizações automáticas
- ✅ **Zero Manutenção**: Sistema se mantém sozinho
- ✅ **Notificações Transparentes**: Sempre sabe o que está acontecendo

### Para Desenvolvedores
- ✅ **Código Limpo**: Lógica centralizada no gerenciador
- ✅ **Fácil Manutenção**: Interface clara para debugging
- ✅ **Histórico Completo**: Rastreamento de todas as mudanças

## 🔮 Próximos Passos

### Melhorias Futuras
1. **Múltiplas Fontes**: Capturar `_h` de diferentes endpoints
2. **Predição**: Identificar padrões de mudança do parâmetro
3. **Cache Inteligente**: Otimizar verificações baseado em histórico
4. **API Externa**: Integrar com serviços que fornecem parâmetros atualizados

### Expansão
- Suporte a outras casas de apostas
- Sistema de backup de parâmetros
- Interface web para monitoramento

---

**🎾 TennisIQ - Sistema Robusto de Links Automáticos** 🚀
