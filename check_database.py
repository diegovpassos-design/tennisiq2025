#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os

def check_database():
    """Verifica o estado atual do banco de dados"""
    db_path = "storage/database/players.db"
    
    if not os.path.exists(db_path):
        print("❌ Banco de dados não encontrado!")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verifica a tabela sent_opportunities
        cursor.execute("SELECT COUNT(*) FROM sent_opportunities")
        count = cursor.fetchone()[0]
        
        print(f"📊 Oportunidades enviadas no banco: {count}")
        
        if count > 0:
            cursor.execute("SELECT * FROM sent_opportunities LIMIT 5")
            opportunities = cursor.fetchall()
            print("\n🔍 Últimas oportunidades:")
            for opp in opportunities:
                print(f"   - {opp}")
        else:
            print("✅ Banco de dados limpo - nenhuma oportunidade enviada")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao verificar banco: {e}")

if __name__ == "__main__":
    check_database()
