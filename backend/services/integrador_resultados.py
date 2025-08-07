#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integração Bot -> Sistema de Resultados
======================================

Módulo para integrar automaticamente o bot principal com o sistema
de verificação de resultados.
"""

import os
import sys
import json
from datetime import datetime

# Configurar caminhos para nova estrutura
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).parent.parent.parent

# Adicionar PROJECT_ROOT ao path para imports
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from backend.data.results.resultados import VerificadorResultados
except ImportError as e:
    print(f"❌ Erro ao importar VerificadorResultados: {e}")
    VerificadorResultados = None

class IntegradorResultados:
    def __init__(self):
        """Inicializa o integrador."""
        self.verificador = VerificadorResultados() if VerificadorResultados else None
        
    def registrar_aposta_automatica(self, oportunidade: dict, odds_data: dict, dados_filtros: dict = None):
        """
        Registra automaticamente uma aposta quando o sinal é enviado.
        
        Args:
            oportunidade: Dados da oportunidade detectada
            odds_data: Dados das odds da partida
            dados_filtros: Dados dos filtros aplicados (opcional)
        """
        if not self.verificador:
            print("❌ Verificador de resultados não disponível")
            return None
            
        try:
            # Extrair dados da oportunidade
            partida_id = oportunidade.get('partida_id', '')
            jogador_apostado = oportunidade.get('jogador', '')
            oponente = oportunidade.get('oponente', '')
            liga = oportunidade.get('liga', 'Liga não especificada')
            placar_momento = f"{oportunidade.get('placar', '')} | {oportunidade.get('fase', '')}"
            
            # Extrair odd (tentar pegar a odd do jogador apostado)
            odd = 1.0  # Valor padrão
            try:
                if 'jogador1_odd' in odds_data and odds_data['jogador1_odd'] != 'N/A':
                    odd = float(odds_data['jogador1_odd'])
                elif 'jogador2_odd' in odds_data and odds_data['jogador2_odd'] != 'N/A':
                    odd = float(odds_data['jogador2_odd'])
            except:
                odd = 1.0
            
            # Registrar a aposta
            aposta_id = self.verificador.registrar_aposta(
                partida_id=partida_id,
                jogador_apostado=jogador_apostado,
                oponente=oponente,
                odd=odd,
                liga=liga,
                placar_momento=placar_momento
            )
            
            # Armazenar dados dos filtros se disponíveis
            if aposta_id and dados_filtros:
                try:
                    # Adicionar dados dos filtros ao histórico da aposta
                    for aposta in self.verificador.historico_apostas:
                        if aposta.get('id') == aposta_id:
                            aposta['dados_filtros'] = dados_filtros
                            aposta['metadados'] = {
                                'ev': dados_filtros.get('ev', 0),
                                'momentum_score': dados_filtros.get('momentum_score', 0),
                                'double_faults': dados_filtros.get('double_faults', 0),
                                'win_1st_serve': dados_filtros.get('win_1st_serve', 0),
                                'odd_final': dados_filtros.get('odd_final', odd),
                                'timestamp_entrada': dados_filtros.get('timestamp_entrada'),
                                'filtros_aplicados': dados_filtros.get('filtros_aplicados', {})
                            }
                            break
                    
                    # Salvar imediatamente
                    self.verificador.salvar_apostas()
                    print(f"📊 Dados dos filtros armazenados com a aposta {aposta_id}")
                    
                except Exception as e:
                    print(f"⚠️ Erro ao armazenar dados dos filtros: {e}")
            
            print(f"✅ Aposta registrada automaticamente: {aposta_id}")
            return aposta_id
            
        except Exception as e:
            print(f"❌ Erro ao registrar aposta automaticamente: {e}")
            return None
    
    def verificar_resultados_pendentes(self):
        """Verifica resultados pendentes (para uso manual)."""
        if self.verificador:
            self.verificador.verificar_todas_apostas_pendentes()
        else:
            print("❌ Verificador não disponível")
    
    def gerar_relatorio(self):
        """Gera relatório de performance."""
        if self.verificador:
            self.verificador.gerar_relatorio_performance()
        else:
            print("❌ Verificador não disponível")

# Instância global para uso no bot
integrador_resultados = IntegradorResultados()
