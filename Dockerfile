FROM python:3.9-slim

WORKDIR /app

# Copiar arquivos de dependências
COPY requirements.txt .

# Instalar dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Criar diretórios necessários
RUN mkdir -p storage/logs/system storage/database storage/exports

# Comando de inicialização
CMD ["python", "server.py"]
