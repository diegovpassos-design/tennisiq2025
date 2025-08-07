# Arquivo de configuração para produção
import os
from urllib.parse import urlparse

class ProductionConfig:
    # Variáveis de ambiente necessárias
    DATABASE_URL = os.environ.get('DATABASE_URL')
    TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
    TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID') 
    TELEGRAM_CHANNEL_ID = os.environ.get('TELEGRAM_CHANNEL_ID')
    PORT = int(os.environ.get('PORT', 5000))
    
    # Configuração do banco de dados PostgreSQL
    if DATABASE_URL:
        db_url = urlparse(DATABASE_URL)
        DB_CONFIG = {
            'host': db_url.hostname,
            'port': db_url.port or 5432,
            'database': db_url.path[1:] if db_url.path else '',
            'user': db_url.username,
            'password': db_url.password
        }
    else:
        # Fallback para desenvolvimento
        DB_CONFIG = {
            'host': 'localhost',
            'port': 5432,
            'database': 'tennisiq',
            'user': 'postgres',
            'password': 'password'
        }
    
    # Configurações específicas para produção
    DEBUG = False
    ENV = 'production'
    
    # Rate limiting para API calls
    API_RATE_LIMIT = int(os.environ.get('API_RATE_LIMIT', 3600))
    
    # Configurações de logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    
    @classmethod
    def is_production(cls):
        return os.environ.get('RAILWAY_ENVIRONMENT') == 'production'
    
    @classmethod
    def get_database_url(cls):
        return cls.DATABASE_URL or f"postgresql://{cls.DB_CONFIG['user']}:{cls.DB_CONFIG['password']}@{cls.DB_CONFIG['host']}:{cls.DB_CONFIG['port']}/{cls.DB_CONFIG['database']}"
