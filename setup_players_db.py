#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os

def setup_players_db():
    """Configura o banco players.db com a tabela sent_opportunities"""
    db_path = "storage/database/players.db"
    
    # Garante que o diretório existe
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Cria a tabela sent_opportunities se não existir
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sent_opportunities (
                event_id TEXT PRIMARY KEY,
                match_info TEXT,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Remove qualquer oportunidade existente
        cursor.execute("DELETE FROM sent_opportunities")
        
        conn.commit()
        
        # Verifica o resultado
        cursor.execute("SELECT COUNT(*) FROM sent_opportunities")
        count = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"✅ Banco players.db configurado! Oportunidades: {count}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    setup_players_db()
