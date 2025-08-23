import sqlite3
import os

# Verificar bancos de dados
print('=== VERIFICAÇÃO DE BANCOS DE DADOS ===')

db_files = []
for root, dirs, files in os.walk('.'):
    for file in files:
        if file.endswith('.db'):
            db_files.append(os.path.join(root, file))

print('Bancos encontrados:')
for db_file in db_files:
    print(f'  - {db_file}')

print()

# Verificar prelive.db
prelive_path = 'storage/database/prelive.db'
if os.path.exists(prelive_path):
    print(f'=== PRELIVE.DB ({prelive_path}) ===')
    conn = sqlite3.connect(prelive_path)
    
    # Listar tabelas
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    for table_name in tables:
        table = table_name[0]
        print(f'\nTabela: {table}')
        
        # Contar registros
        cursor = conn.execute(f'SELECT COUNT(*) FROM {table}')
        count = cursor.fetchone()[0]
        print(f'  Registros: {count}')
        
        # Estrutura
        cursor = conn.execute(f'PRAGMA table_info({table})')
        columns = cursor.fetchall()
        print('  Colunas:')
        for col in columns:
            print(f'    {col[1]} ({col[2]})')
    
    conn.close()
else:
    print(f'❌ {prelive_path} não encontrado')

# Verificar players.db
players_path = 'storage/database/players.db'
if os.path.exists(players_path):
    print(f'\n=== PLAYERS.DB ({players_path}) ===')
    conn = sqlite3.connect(players_path)
    
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    for table_name in tables:
        table = table_name[0]
        cursor = conn.execute(f'SELECT COUNT(*) FROM {table}')
        count = cursor.fetchone()[0]
        print(f'Tabela {table}: {count} registros')
    
    conn.close()
else:
    print(f'❌ {players_path} não encontrado')
