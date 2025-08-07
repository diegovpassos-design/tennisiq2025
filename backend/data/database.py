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
        # Usar SQLite sempre (funciona local e na nuvem)
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
        # Usar SQLite sempre
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
            print(f"❌ Erro ao salvar: {e}")
    
    def get_estatisticas(self):
        """Get statistics from database"""
        # Usar JSON sempre
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
