#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LOGGER FORMATADO - TennisIQ Bot
==============================
Sistema de logging organizado e visualmente claro
"""

from datetime import datetime, timezone, timedelta
import json
import os

class LoggerFormatado:
    """Logger com apresentação visual organizada"""
    
    def __init__(self):
        self.nivel_verbosidade = "NORMAL"  # MINIMAL, NORMAL, DEBUG
        self.ciclo_atual = 0
        self.inicio_ciclo = None
        
    def set_verbosidade(self, nivel):
        """Define o nível de verbosidade: MINIMAL, NORMAL, DEBUG"""
        self.nivel_verbosidade = nivel.upper()
    
    def get_timestamp(self):
        """Retorna timestamp formatado para Brasil (UTC-3)"""
        agora = datetime.now(timezone(timedelta(hours=-3)))
        return agora.strftime("%H:%M:%S")
    
    def get_data_completa(self):
        """Retorna data completa formatada"""
        agora = datetime.now(timezone(timedelta(hours=-3)))
        return agora.strftime("%d/%m/%Y %H:%M:%S")
    
    def log_inicio_ciclo(self, numero_ciclo):
        """Inicia um novo ciclo com cabeçalho limpo"""
        self.ciclo_atual = numero_ciclo
        self.inicio_ciclo = datetime.now()
        
        if self.nivel_verbosidade == "MINIMAL":
            print(f"\n🎾 CICLO {numero_ciclo} [{self.get_timestamp()}]")
            return
            
        print(f"\n{'='*50}")
        print(f"🎾 TENNISIQ BOT - CICLO {numero_ciclo}")
        print(f"⏰ {self.get_data_completa()}")
        print(f"{'='*50}")
    
    def log_coleta_dados(self, total_partidas, aprovadas_timing, requests_usados=0):
        """Log da fase de coleta de dados"""
        if self.nivel_verbosidade == "MINIMAL":
            print(f"📡 {total_partidas} partidas • {aprovadas_timing} timing OK")
            return
            
        porcentagem = (aprovadas_timing / total_partidas * 100) if total_partidas > 0 else 0
        
        print(f"\n📡 COLETA DE DADOS")
        print(f"├─ ✅ {total_partidas} partidas encontradas")
        print(f"├─ ⏱️  {aprovadas_timing} aprovadas no timing ({porcentagem:.0f}%)")
        if requests_usados > 0:
            print(f"├─ 📊 {requests_usados} requests API utilizados")
        print(f"└─ 🎯 Processando análise detalhada...")
    
    def log_partidas_prioritarias(self, partidas_aprovadas):
        """Log das partidas que passaram no timing"""
        if not partidas_aprovadas:
            if self.nivel_verbosidade != "MINIMAL":
                print(f"\n🔍 PARTIDAS APROVADAS")
                print(f"└─ ❌ Nenhuma partida aprovada no timing")
            return
            
        if self.nivel_verbosidade == "MINIMAL":
            print(f"🎯 {len(partidas_aprovadas)} partidas para análise")
            return
            
        print(f"\n📊 PARTIDAS PRIORITÁRIAS ({len(partidas_aprovadas)})")
        print("┌" + "─"*47 + "┐")
        
        for i, partida in enumerate(partidas_aprovadas[:5], 1):  # Top 5
            prioridade = partida.get('prioridade', 0)
            emoji_prioridade = self._get_emoji_prioridade(prioridade)
            estrategia = self._get_estrategia_partida(partida)
            
            jogador_casa = partida.get('jogador_casa', 'N/A')[:20]
            jogador_visitante = partida.get('jogador_visitante', 'N/A')[:20]
            liga = partida.get('liga', 'N/A')[:15]
            placar = partida.get('placar', 'N/A')
            fase = partida.get('fase', 'N/A')
            
            print(f"│ {emoji_prioridade} P{i} • {jogador_casa} vs {jogador_visitante:<20} │")
            print(f"│    📍 {fase} ({placar}) • {liga:<15} │")
            print(f"│    🎯 Prioridade {prioridade}/5 • {estrategia:<17} │")
            
            if i < len(partidas_aprovadas) and i < 5:
                print("├" + "─"*47 + "┤")
        
        print("└" + "─"*47 + "┘")
    
    def log_analise_filtros(self, resultados_filtros):
        """Log da análise de filtros com resultados"""
        if not resultados_filtros:
            if self.nivel_verbosidade != "MINIMAL":
                print(f"\n🔍 ANÁLISE DE FILTROS")
                print(f"└─ ⚠️  Nenhum resultado para analisar")
            return
            
        aprovados = [r for r in resultados_filtros if r.get('aprovado', False)]
        reprovados = [r for r in resultados_filtros if not r.get('aprovado', False)]
        
        if self.nivel_verbosidade == "MINIMAL":
            print(f"🔍 Filtros: {len(aprovados)} aprovados, {len(reprovados)} reprovados")
            if aprovados:
                for resultado in aprovados:
                    jogador = resultado.get('jogador', 'N/A')[:20]
                    estrategia = resultado.get('estrategia', 'N/A')
                    print(f"✅ {jogador} ({estrategia})")
            return
            
        print(f"\n🔍 ANÁLISE DE FILTROS")
        
        if aprovados:
            print("┌─ APROVADOS ─────────────────────────────────┐")
            for resultado in aprovados:
                jogador = resultado.get('jogador', 'N/A')
                estrategia = resultado.get('estrategia', 'RIGOROSA')
                ev = resultado.get('ev', 0)
                ms = resultado.get('ms', 0)
                print(f"│ ✅ {jogador:<25} │")
                print(f"│    📊 EV: {ev:.3f} | MS: {ms}% • {estrategia} │")
            print("└─────────────────────────────────────────────┘")
        
        if reprovados and self.nivel_verbosidade == "DEBUG":
            print("┌─ REPROVADOS (DEBUG) ────────────────────────┐")
            for resultado in reprovados[:3]:  # Só primeiros 3
                jogador = resultado.get('jogador', 'N/A')
                motivo = resultado.get('motivo_reprovacao', 'N/A')
                print(f"│ ❌ {jogador:<25} │")
                print(f"│    📊 {motivo:<35} │")
            if len(reprovados) > 3:
                print(f"│    ... e mais {len(reprovados)-3} reprovados │")
            print("└─────────────────────────────────────────────┘")
    
    def log_oportunidades_encontradas(self, oportunidades):
        """Log das oportunidades finais encontradas"""
        if not oportunidades:
            if self.nivel_verbosidade != "MINIMAL":
                print(f"\n🎯 RESULTADO FINAL")
                print(f"└─ ❌ Nenhuma oportunidade encontrada")
            return
            
        print(f"\n🎯 OPORTUNIDADES ENCONTRADAS ({len(oportunidades)})")
        print("┌" + "─"*47 + "┐")
        
        for i, oportunidade in enumerate(oportunidades, 1):
            jogador = oportunidade.get('jogador', 'N/A')[:25]
            odd = oportunidade.get('odd', 0)
            estrategia = oportunidade.get('estrategia', 'RIGOROSA')
            confianca = oportunidade.get('confianca', 0)
            
            print(f"│ 🟢 {i}. {jogador:<25} │")
            print(f"│    💰 Odd: {odd:.2f} | {estrategia:<15} │")
            print(f"│    🎯 Confiança: {confianca}%{'   ' if confianca < 100 else ''}                  │")
            
            if i < len(oportunidades):
                print("├" + "─"*47 + "┤")
        
        print("└" + "─"*47 + "┘")
    
    def log_resumo_ciclo(self, stats):
        """Log do resumo final do ciclo"""
        tempo_execucao = ""
        if self.inicio_ciclo:
            duracao = datetime.now() - self.inicio_ciclo
            tempo_execucao = f"{duracao.seconds}s"
        
        if self.nivel_verbosidade == "MINIMAL":
            print(f"📈 {stats.get('analisadas', 0)} analisadas • {stats.get('oportunidades', 0)} oportunidades • {tempo_execucao}")
            print(f"⏰ Próximo ciclo: {stats.get('proximo_ciclo', 60)}s")
            return
            
        print(f"\n📈 RESUMO DO CICLO")
        print(f"├─ 🔍 Analisadas: {stats.get('partidas_analisadas', 0)} partidas")
        print(f"├─ ✅ Timing aprovado: {stats.get('timing_aprovadas', 0)} ({stats.get('taxa_timing', 0):.0f}%)")
        print(f"├─ 🎯 Oportunidades: {stats.get('oportunidades_encontradas', 0)} ({stats.get('taxa_conversao', 0):.1f}%)")
        print(f"├─ 📊 Requests API: {stats.get('requests_usados', 0)}/3600 por hora")
        print(f"├─ ⏱️  Tempo execução: {tempo_execucao}")
        print(f"├─ ⏰ Próximo ciclo: {stats.get('proximo_ciclo', 60)}s")
        print(f"└─ 📊 Sistema: {'🟢 ATIVO' if stats.get('sistema_ativo', True) else '🔴 INATIVO'}")
        print("=" * 50)
    
    def log_erro(self, mensagem, detalhes=None):
        """Log de erro com formatação adequada"""
        print(f"\n🚨 ERRO: {mensagem}")
        if detalhes and self.nivel_verbosidade == "DEBUG":
            print(f"💡 Detalhes: {detalhes}")
    
    def log_aviso(self, mensagem):
        """Log de aviso"""
        if self.nivel_verbosidade != "MINIMAL":
            print(f"⚠️  {mensagem}")
    
    def log_debug(self, mensagem):
        """Log apenas no modo DEBUG"""
        if self.nivel_verbosidade == "DEBUG":
            print(f"🔧 DEBUG: {mensagem}")
    
    def _get_emoji_prioridade(self, prioridade):
        """Retorna emoji baseado na prioridade"""
        if prioridade >= 5:
            return "🟢"
        elif prioridade >= 4:
            return "🔵"
        elif prioridade >= 3:
            return "🟡"
        else:
            return "🔴"
    
    def _get_estrategia_partida(self, partida):
        """Determina estratégia baseada na partida"""
        fase = partida.get('fase', '')
        if '3set' in fase or 'mid' in fase:
            return "ESTRATÉGIA INVERTIDA"
        return "ESTRATÉGIA RIGOROSA"

# Instância global
logger_formatado = LoggerFormatado()
