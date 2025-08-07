#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DASHBOARD WEB - TennisIQ Bot
============================
Interface web para monitoramento em tempo real
"""

from flask import Flask, render_template, jsonify, request
import json
import os
from datetime import datetime, timedelta
import threading
import time
import requests
from collections import defaultdict
import sqlite3
import sys

# Configurar caminhos para nova estrutura
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

# Importar o dashboard_logger corrigido
from .dashboard_logger import dashboard_logger

app = Flask(__name__, 
           template_folder=os.path.join(PROJECT_ROOT, 'frontend', 'templates'),
           static_folder=os.path.join(PROJECT_ROOT, 'frontend', 'static'))

class DashboardData:
    def __init__(self):
        self.init_database()
        self.dados_tempo_real = {
            'partidas_analisadas': [],
            'sinais_gerados': [],
            'partidas_aprovadas_filtro_atual': 0,  # NOVO: Valor capturado do terminal em tempo real
            'estatisticas': {
                'total_partidas': 0,
                'partidas_aprovadas_filtro': 0,  # NOVO: Número atual de partidas aprovadas no filtro
                'total_sinais': 0,
                'taxa_sucesso': 0,
                'ev_medio': 0,
                'sinais_invertidos': 0,
                'sinais_tradicionais': 0
            },
            'performance_horaria': defaultdict(int),
            'filtros_aplicados': {
                'timing': 0,
                'ev': 0,
                'momentum': 0,
                'mental': 0,
                'odds': 0
            },
            'bot_status': {
                'ativo': False,
                'ultimo_update': None,
                'requests_restantes': 3600,
                'proxima_verificacao': None
            }
        }
        # Carregar dados imediatamente na inicialização
        self.atualizar_dados_bot()
    
    def init_database(self):
        """Inicializa banco de dados SQLite para persistência"""
        db_path = os.path.join(PROJECT_ROOT, 'storage', 'database', 'dashboard_data.db')
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        cursor = self.conn.cursor()
        
        # Tabela de partidas analisadas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS partidas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                jogador1 TEXT,
                jogador2 TEXT,
                placar TEXT,
                odds1 REAL,
                odds2 REAL,
                ev REAL,
                momentum_score REAL,
                timing_priority INTEGER,
                mental_score INTEGER,
                decisao TEXT,
                motivo TEXT
            )
        ''')
        
        # Tabela de sinais
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sinais (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                tipo TEXT,
                target TEXT,
                odd REAL,
                ev REAL,
                confianca REAL,
                mental_score INTEGER,
                fatores_mentais TEXT,
                resultado TEXT,
                roi REAL
            )
        ''')
        
        # Tabela de performance
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data DATE,
                total_sinais INTEGER,
                sinais_green INTEGER,
                sinais_red INTEGER,
                taxa_sucesso REAL,
                roi_total REAL,
                ev_medio REAL
            )
        ''')
        
        self.conn.commit()
    
    def atualizar_dados_bot(self):
        """Atualiza dados do bot usando dashboard_logger corrigido"""
        try:
            print(f"[DEBUG] Usando dados do dashboard_logger corrigido...")
            
            # Obter dados processados do dashboard_logger
            dados = dashboard_logger.obter_dados_dashboard()
            
            # Atualizar dados tempo real
            self.dados_tempo_real['partidas_analisadas'] = dados['partidas_analisadas']
            self.dados_tempo_real['sinais_gerados'] = dados['sinais_gerados']
            self.dados_tempo_real['estatisticas'] = dados['estatisticas']
            
            # Adicionar status do bot se existir
            status_file = os.path.join(PROJECT_ROOT, 'storage', 'database', 'bot_status.json')
            if os.path.exists(status_file):
                with open(status_file, 'r', encoding='utf-8') as f:
                    status = json.load(f)
                    self.dados_tempo_real['bot_status'] = status
            else:
                self.dados_tempo_real['bot_status'] = {
                    'ativo': True,
                    'ultimo_update': datetime.now().isoformat(),
                    'requests_restantes': 3600,
                    'proxima_verificacao': None
                }
            
            print(f"[DEBUG] Dados carregados - Partidas: {len(self.dados_tempo_real['partidas_analisadas'])}, Sinais: {len(self.dados_tempo_real['sinais_gerados'])}")
            print(f"[DEBUG] EV médio calculado: {self.dados_tempo_real['estatisticas']['ev_medio']}")
            
        except Exception as e:
            print(f"[ERROR] Erro ao atualizar dados: {e}")
            import traceback
            traceback.print_exc()

# Instância global
dashboard_data = DashboardData()

@app.route('/')
def index():
    """Página principal do dashboard"""
    return render_template('dashboard.html')

@app.route('/simples')
def dashboard_simples():
    """Dashboard simples para testes"""
    return render_template('dashboard_simples.html')

@app.route('/novo')
def dashboard_novo():
    """Dashboard principal novo"""
    return render_template('dashboard_principal_novo.html')

@app.route('/api/dados')
def api_dados():
    """API para dados em tempo real usando dashboard_logger corrigido"""
    dashboard_data.atualizar_dados_bot()
    dados = dashboard_data.dados_tempo_real.copy()
    
    print(f"[DEBUG] API Dados - EV médio calculado: {dados.get('estatisticas', {}).get('ev_medio', 0)}")
    print(f"[DEBUG] API Dados - Total partidas: {dados.get('estatisticas', {}).get('total_partidas', 0)}")
    print(f"[DEBUG] API Dados - Total sinais: {dados.get('estatisticas', {}).get('total_sinais', 0)}")
    
    return jsonify(dados)

@app.route('/api/partidas')
def api_partidas():
    """API para lista de partidas analisadas aprovadas no filtro"""
    dashboard_data.atualizar_dados_bot()
    # Retornar apenas partidas aprovadas no filtro ordenadas por mais recente
    partidas = dashboard_data.dados_tempo_real['partidas_analisadas']  # Já filtradas para apenas aprovadas
    
    # Remover duplicatas baseado em jogadores + timestamp + placar
    partidas_unicas = []
    chaves_vistas = set()
    
    for partida in partidas:
        chave = f"{partida.get('jogador1', '')}_vs_{partida.get('jogador2', '')}_{partida.get('timestamp', '')}_{partida.get('placar', '')}"
        if chave not in chaves_vistas:
            chaves_vistas.add(chave)
            partidas_unicas.append(partida)
    
    partidas_recentes = sorted(partidas_unicas, key=lambda x: x.get('timestamp', ''), reverse=True)
    return jsonify(partidas_recentes)

@app.route('/api/sinais')
def api_sinais():
    """API para lista de sinais gerados"""
    dashboard_data.atualizar_dados_bot()
    return jsonify(dashboard_data.dados_tempo_real['sinais_gerados'])

@app.route('/api/performance/<periodo>')
def api_performance(periodo):
    """API para dados de performance por período"""
    cursor = dashboard_data.conn.cursor()
    
    if periodo == 'hoje':
        data_inicio = datetime.now().date()
    elif periodo == 'semana':
        data_inicio = datetime.now().date() - timedelta(days=7)
    elif periodo == 'mes':
        data_inicio = datetime.now().date() - timedelta(days=30)
    else:
        data_inicio = datetime.now().date() - timedelta(days=1)
    
    cursor.execute('''
        SELECT * FROM performance 
        WHERE data >= ? 
        ORDER BY data DESC
    ''', (data_inicio,))
    
    dados = cursor.fetchall()
    colunas = ['id', 'data', 'total_sinais', 'sinais_green', 'sinais_red', 
               'taxa_sucesso', 'roi_total', 'ev_medio']
    
    resultado = []
    for linha in dados:
        resultado.append(dict(zip(colunas, linha)))
    
    return jsonify(resultado)

@app.route('/api/status')
def api_status():
    """API para status do bot"""
    dashboard_data.atualizar_dados_bot()
    return jsonify(dashboard_data.dados_tempo_real['bot_status'])

def atualizar_dados_periodicamente():
    """Thread para atualizar dados a cada 30 segundos"""
    while True:
        try:
            dashboard_data.atualizar_dados_bot()
            # Print apenas do ciclo de atualização (único debug permitido)
            agora = datetime.now().strftime("%H:%M:%S")
            print(f"🔄 [{agora}] Ciclo de atualização dashboard concluído")
        except Exception as e:
            # Falha silenciosa
            pass
        time.sleep(30)

if __name__ == '__main__':
    # Inicia thread de atualização
    thread_atualizacao = threading.Thread(target=atualizar_dados_periodicamente, daemon=True)
    thread_atualizacao.start()
    
    print("🌐 Dashboard TennisIQ iniciado!")
    print("📊 Acesse: http://localhost:5000")
    print("🔄 Atualizações automáticas a cada 30 segundos")
    
    # Inicia servidor Flask
    app.run(host='0.0.0.0', port=5000, debug=False)
