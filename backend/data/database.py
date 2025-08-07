"""
Database manager for TennisIQ - Railway PostgreSQL
"""
import os
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import sqlite3
from urllib.parse import urlparse

class DatabaseManager:
    def __init__(self):
        self.is_production = os.getenv('RAILWAY_ENVIRONMENT') is not None
        
        if self.is_production:
            # PostgreSQL for Railway
            self.db_url = os.getenv('DATABASE_URL')
            if not self.db_url:
                raise ValueError("DATABASE_URL não encontrada no ambiente Railway")
            self.init_postgres()
        else:
            # SQLite for local development
            self.db_path = "storage/database/dashboard_data.db"
            self.init_sqlite()
    
    def init_postgres(self):
        """Initialize PostgreSQL tables"""
        try:
            with psycopg2.connect(self.db_url) as conn:
                with conn.cursor() as cur:
                    # Create tables
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS partidas_analisadas (
                            id SERIAL PRIMARY KEY,
                            data_analise TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            partida_info JSONB,
                            resultado TEXT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS historico_apostas (
                            id SERIAL PRIMARY KEY,
                            data_aposta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            aposta_info JSONB,
                            resultado TEXT,
                            valor_green DECIMAL(10,2),
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS estatisticas_greens (
                            id SERIAL PRIMARY KEY,
                            data_calculo TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            total_apostas INTEGER,
                            total_greens INTEGER,
                            taxa_acerto DECIMAL(5,2),
                            valor_total DECIMAL(10,2),
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    
                    conn.commit()
                    print("✅ PostgreSQL inicializado com sucesso")
        except Exception as e:
            print(f"❌ Erro ao inicializar PostgreSQL: {e}")
    
    def init_sqlite(self):
        """Initialize SQLite for local development"""
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            conn = sqlite3.connect(self.db_path)
            conn.close()
            print("✅ SQLite inicializado com sucesso")
        except Exception as e:
            print(f"❌ Erro ao inicializar SQLite: {e}")
    
    def save_partida_analisada(self, partida_data):
        """Save analyzed match to database"""
        if self.is_production:
            try:
                with psycopg2.connect(self.db_url) as conn:
                    with conn.cursor() as cur:
                        cur.execute("""
                            INSERT INTO partidas_analisadas (partida_info, resultado)
                            VALUES (%s, %s)
                        """, (json.dumps(partida_data), 'PENDENTE'))
                        conn.commit()
            except Exception as e:
                print(f"❌ Erro PostgreSQL: {e}")
        else:
            # SQLite fallback
            try:
                json_file = "storage/database/partidas_analisadas.json"
                os.makedirs(os.path.dirname(json_file), exist_ok=True)
                
                if os.path.exists(json_file):
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                else:
                    data = []
                
                data.append({
                    'timestamp': datetime.now().isoformat(),
                    'partida': partida_data,
                    'resultado': 'PENDENTE'
                })
                
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            except Exception as e:
                print(f"❌ Erro SQLite: {e}")
    
    def get_estatisticas(self):
        """Get statistics from database"""
        if self.is_production:
            try:
                with psycopg2.connect(self.db_url) as conn:
                    with conn.cursor(cursor_factory=RealDictCursor) as cur:
                        cur.execute("""
                            SELECT COUNT(*) as total_apostas,
                                   SUM(CASE WHEN resultado = 'GREEN' THEN 1 ELSE 0 END) as total_greens
                            FROM historico_apostas
                        """)
                        result = cur.fetchone()
                        if result:
                            total = result['total_apostas'] or 0
                            greens = result['total_greens'] or 0
                            taxa = (greens / total * 100) if total > 0 else 0
                            return {
                                'total_apostas': total,
                                'total_greens': greens,
                                'taxa_acerto': round(taxa, 1)
                            }
            except Exception as e:
                print(f"❌ Erro PostgreSQL: {e}")
        
        # SQLite fallback
        try:
            json_file = "backend/results/historico_apostas.json"
            if os.path.exists(json_file):
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    total = len(data)
                    greens = sum(1 for item in data if item.get('resultado') == 'GREEN')
                    taxa = (greens / total * 100) if total > 0 else 0
                    return {
                        'total_apostas': total,
                        'total_greens': greens,
                        'taxa_acerto': round(taxa, 1)
                    }
        except Exception as e:
            print(f"❌ Erro ao ler estatísticas: {e}")
        
        return {'total_apostas': 0, 'total_greens': 0, 'taxa_acerto': 0}

# Global instance
db_manager = DatabaseManager()
