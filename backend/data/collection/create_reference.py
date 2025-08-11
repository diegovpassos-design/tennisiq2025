#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Criador de Referência de Endpoints
==================================

Script para criar um arquivo JSON com dados de exemplo de todos os endpoints
da API de tênis para facilitar a visualização e escolha do endpoint correto.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Corrigir import para nova estrutura
from .tennis_collector import TennisDataCollector

def main():
    """Executa apenas a criação do arquivo de referência."""
    try:
        print("🔍 GERADOR DE REFERÊNCIA DE ENDPOINTS DA API DE TÊNIS")
        print("=" * 60)
        
        # Verificar se o token está configurado
        collector = TennisDataCollector()
        
        if not collector.api_token:
            print("⚠️  ATENÇÃO: API key não encontrada no arquivo config/config.json")
            print("   Verifique se o campo 'api_key' está configurado corretamente")
            return
        
        print(f"🔑 API Key configurada: {collector.api_token[:10]}...")
        print(f"🌐 Base URL: {collector.base_url}")
        print(f"🎾 Sport ID: {collector.sport_id}")
        print("")
        
        # Criar arquivo de referência
        success = collector.create_endpoints_data_reference()
        
        if success:
            print("\n✅ CONCLUÍDO COM SUCESSO!")
            print("📁 Arquivo criado: ../dados/endpoints_data_reference.json")
            print("\n📖 Use este arquivo para:")
            print("   • Ver exemplos de dados de cada endpoint")
            print("   • Entender quais campos estão disponíveis")
            print("   • Escolher o endpoint ideal para sua necessidade")
            print("   • Ver códigos de status e mercados de odds")
        else:
            print("\n❌ ERRO na criação do arquivo de referência")
            
    except KeyboardInterrupt:
        print("\n⏹️  Operação cancelada pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")

if __name__ == "__main__":
    main()
