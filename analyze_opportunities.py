import sqlite3
from datetime import datetime

# Análise detalhada das oportunidades
conn = sqlite3.connect('storage/database/prelive.db')

print('=== RELATÓRIO COMPLETO DE OPORTUNIDADES ===\n')

# Total de oportunidades
cursor = conn.execute('SELECT COUNT(*) FROM opportunities')
total = cursor.fetchone()[0]
print(f'📊 Total de oportunidades encontradas: {total}')

# Oportunidades por status
cursor = conn.execute('SELECT status, COUNT(*) FROM opportunities GROUP BY status')
status_counts = cursor.fetchall()
print('\n📈 Por status:')
for status, count in status_counts:
    print(f'  {status}: {count}')

# Oportunidades por data
cursor = conn.execute('SELECT DATE(created_at) as date, COUNT(*) as count FROM opportunities GROUP BY DATE(created_at) ORDER BY date DESC')
daily_counts = cursor.fetchall()
print('\n📅 Por data:')
for date, count in daily_counts:
    print(f'  {date}: {count}')

# EV médio
cursor = conn.execute('SELECT AVG(ev), MIN(ev), MAX(ev) FROM opportunities')
ev_stats = cursor.fetchone()
print(f'\n💰 Expected Value:')
print(f'  Médio: {ev_stats[0]:.3f}')
print(f'  Mínimo: {ev_stats[1]:.3f}')
print(f'  Máximo: {ev_stats[2]:.3f}')

# Top 10 oportunidades por EV
print('\n🏆 Top 10 melhores oportunidades (por EV):')
cursor = conn.execute('SELECT match_name, side, odd, ev, created_at FROM opportunities ORDER BY ev DESC LIMIT 10')
top_opportunities = cursor.fetchall()
for i, (match, side, odd, ev, created) in enumerate(top_opportunities, 1):
    print(f'  {i}. {match} ({side}) - Odd: {odd:.2f}, EV: {ev:.3f} - {created}')

# Ligas mais ativas
print('\n🏅 Ligas com mais oportunidades:')
cursor = conn.execute('SELECT league, COUNT(*) as count FROM opportunities GROUP BY league ORDER BY count DESC LIMIT 5')
leagues = cursor.fetchall()
for league, count in leagues:
    print(f'  {league}: {count}')

# Movimento de linhas
cursor = conn.execute('SELECT COUNT(*) FROM line_movements')
movements = cursor.fetchone()[0]
print(f'\n📊 Movimentos de linha registrados: {movements}')

# Oportunidades enviadas
cursor = conn.execute('SELECT COUNT(*) FROM sent_opportunities')
sent = cursor.fetchone()[0]
print(f'📤 Oportunidades enviadas via Telegram: {sent}')

# Últimas 5 oportunidades
print('\n🕐 Últimas 5 oportunidades encontradas:')
cursor = conn.execute('SELECT match_name, side, odd, ev, created_at FROM opportunities ORDER BY created_at DESC LIMIT 5')
recent = cursor.fetchall()
for match, side, odd, ev, created in recent:
    print(f'  • {match} ({side}) - Odd: {odd:.2f}, EV: {ev:.3f} - {created}')

conn.close()

print('\n=== ANÁLISE DE JOGADORES ===')
conn_players = sqlite3.connect('storage/database/players.db')

cursor = conn_players.execute('SELECT COUNT(*) FROM players')
total_players = cursor.fetchone()[0]
print(f'👥 Total de jogadores no banco: {total_players}')

# Jogadores com dados reais vs padrão
cursor = conn_players.execute('SELECT COUNT(*) FROM players WHERE ranking != 999')
real_data = cursor.fetchone()[0]
default_data = total_players - real_data

print(f'✅ Jogadores com dados reais: {real_data}')
print(f'⚪ Jogadores com dados padrão: {default_data}')
print(f'📊 % dados reais: {(real_data/total_players)*100:.1f}%')

conn_players.close()
