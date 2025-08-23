#!/usr/bin/env python3
"""
Script de limpeza automática do TennisQ
ATENÇÃO: Este script remove arquivos permanentemente!
"""

import os
import shutil
from pathlib import Path

def cleanup_project():
    """Remove arquivos desnecessários"""
    
    # Arquivos de teste para remover
    test_files = 'comprehensive_tests.py', 'debug_api.py', 'debug_model.py', 'debug_odds.py', 'final_test.py', 'quick_test.py', 'send_test_buttons.py', 'test_api.py', 'test_api_exploration.py', 'test_b365_api.py', 'test_compile.py', 'test_detailed_endpoints.py', 'test_endpoints.py', 'test_ev_calculation.py', 'test_final.py', 'test_final_message.py', 'test_fixed_api.py', 'test_known_players.py', 'test_new_features.py', 'test_new_format.py', 'test_odds.py', 'test_real_events.py', 'test_scanner.py', 'test_separate_messages.py', 'test_simplified_message.py', 'test_sophisticated_model.py', 'test_sport_ids.py', 'test_status.py', 'test_system.py', 'test_telegram_buttons.py', 'test_telegram_system.py'
    
    # Arquivos obsoletos para remover  
    obsolete_files = '.python-version', 'app_railway.py', 'check_data_source.py', 'como_detecta_oportunidades.py', 'comprehensive_tests.py', 'debug.py', 'final_test.py', 'main.py', 'monitor.py', 'nixpacks.toml', 'quick_test.py', 'run.py', 'send_test_buttons.py', 'validate.py', 'verify_real_data.py'
    
    removed_count = 0
    
    print("🧹 INICIANDO LIMPEZA DO PROJETO TENNISQ")
    print("=" * 50)
    
    # Remove arquivos de teste
    print("\n🧪 Removendo arquivos de teste...")
    for file in test_files:
        if os.path.exists(file):
            try:
                if os.path.isdir(file):
                    shutil.rmtree(file)
                else:
                    os.remove(file)
                print(f"   ✅ Removido: {file}")
                removed_count += 1
            except Exception as e:
                print(f"   ❌ Erro ao remover {file}: {e}")
    
    # Remove arquivos obsoletos
    print("\n🗑️ Removendo arquivos obsoletos...")
    for file in obsolete_files:
        if os.path.exists(file):
            try:
                if os.path.isdir(file):
                    shutil.rmtree(file)
                else:
                    os.remove(file)
                print(f"   ✅ Removido: {file}")
                removed_count += 1
            except Exception as e:
                print(f"   ❌ Erro ao remover {file}: {e}")
    
    print(f"\n🎉 LIMPEZA CONCLUÍDA!")
    print(f"📊 Total de arquivos removidos: {removed_count}")
    print(f"✨ Projeto organizado e limpo!")

if __name__ == "__main__":
    import sys
    
    response = input("⚠️ ATENÇÃO: Esta operação remove arquivos permanentemente! Continuar? (sim/não): ")
    if response.lower() in ['sim', 'yes', 's', 'y']:
        cleanup_project()
    else:
        print("❌ Operação cancelada.")
