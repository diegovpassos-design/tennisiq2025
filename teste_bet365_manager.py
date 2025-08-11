"""
Teste do Sistema de Gerenciamento de Links da Bet365
==================================================
Script para testar e validar o funcionamento do sistema automático
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.bet365_link_manager import Bet365LinkManager

def testar_sistema():
    """Testa todas as funcionalidades do sistema de links da Bet365"""
    
    print("🧪 TESTE DO SISTEMA BET365 LINK MANAGER")
    print("=" * 60)
    
    # Criar instância do gerenciador
    manager = Bet365LinkManager()
    
    # 1. Verificar status inicial
    print("\n1️⃣ VERIFICANDO STATUS INICIAL")
    print("-" * 40)
    status = manager.get_status()
    print(f"📊 Status completo: {status}")
    
    # 2. Testar captura automática
    print("\n2️⃣ TESTANDO CAPTURA AUTOMÁTICA")
    print("-" * 40)
    h_param = manager.update_h_param(force=True)
    print(f"🎯 Parâmetro capturado: {h_param[:30] if h_param else 'FALHOU'}...")
    
    # 3. Testar geração de links
    print("\n3️⃣ TESTANDO GERAÇÃO DE LINKS")
    print("-" * 40)
    
    # Link genérico
    link_generico = manager.generate_link()
    print(f"🔗 Link genérico: {link_generico}")
    
    # Link específico
    link_especifico = manager.generate_link("12345678")
    print(f"🎯 Link específico: {link_especifico}")
    
    # 4. Testar validação de links
    print("\n4️⃣ TESTANDO VALIDAÇÃO DE LINKS")
    print("-" * 40)
    
    if h_param:
        teste_link = manager.test_link()
        print(f"✅ Link funciona: {'SIM' if teste_link else 'NÃO'}")
    else:
        print("⚠️ Sem parâmetro para testar")
    
    # 5. Verificar configuração salva
    print("\n5️⃣ VERIFICANDO CONFIGURAÇÃO")
    print("-" * 40)
    if os.path.exists(manager.config_path):
        with open(manager.config_path, 'r', encoding='utf-8') as f:
            import json
            config = json.load(f)
            print(f"💾 Configuração salva: {config.get('h_param', 'N/A')[:30]}...")
            print(f"📅 Última atualização: {config.get('last_update', 'N/A')}")
    else:
        print("⚠️ Arquivo de configuração não encontrado")
    
    # 6. Status final
    print("\n6️⃣ STATUS FINAL")
    print("-" * 40)
    status_final = manager.get_status()
    print(f"🎭 Status final: {status_final}")
    
    print(f"\n{'✅ TESTE CONCLUÍDO' if status_final['h_param_available'] else '❌ TESTE FALHOU'}")
    print("=" * 60)

def comando_manual():
    """Interface de comando manual para gerenciar links"""
    
    print("🔧 GERENCIADOR MANUAL DE LINKS BET365")
    print("=" * 50)
    
    manager = Bet365LinkManager()
    
    while True:
        print("\nOpções disponíveis:")
        print("1. 📊 Ver status atual")
        print("2. 🔄 Atualizar parâmetro automaticamente")
        print("3. 🔧 Definir parâmetro manualmente")
        print("4. 🧪 Testar link atual")
        print("5. 🔗 Gerar link de teste")
        print("6. 📜 Ver histórico de atualizações")
        print("0. ❌ Sair")
        
        escolha = input("\nEscolha uma opção: ").strip()
        
        if escolha == "1":
            print("\n📊 STATUS ATUAL")
            print("-" * 30)
            status = manager.get_status()
            for key, value in status.items():
                print(f"{key}: {value}")
        
        elif escolha == "2":
            print("\n🔄 ATUALIZANDO AUTOMATICAMENTE...")
            print("-" * 40)
            novo_param = manager.update_h_param(force=True)
            if novo_param:
                print(f"✅ Atualizado: {novo_param[:30]}...")
            else:
                print("❌ Falha na atualização automática")
        
        elif escolha == "3":
            print("\n🔧 DEFINIR PARÂMETRO MANUAL")
            print("-" * 35)
            param = input("Digite o novo parâmetro _h: ").strip()
            if param:
                if manager.set_h_param_manual(param):
                    print("✅ Parâmetro definido com sucesso")
                else:
                    print("❌ Parâmetro inválido ou não funciona")
            else:
                print("⚠️ Parâmetro vazio")
        
        elif escolha == "4":
            print("\n🧪 TESTANDO LINK ATUAL")
            print("-" * 30)
            resultado = manager.test_link()
            print(f"Resultado: {'✅ FUNCIONANDO' if resultado else '❌ NÃO FUNCIONA'}")
        
        elif escolha == "5":
            print("\n🔗 GERANDO LINKS DE TESTE")
            print("-" * 35)
            event_id = input("ID do evento (ou Enter para link genérico): ").strip()
            link = manager.generate_link(event_id if event_id else None)
            print(f"Link gerado: {link}")
        
        elif escolha == "6":
            print("\n📜 HISTÓRICO DE ATUALIZAÇÕES")
            print("-" * 40)
            if hasattr(manager, 'update_history') and manager.update_history:
                for i, update in enumerate(manager.update_history[-5:], 1):
                    print(f"{i}. {update['timestamp'][:19]} - {update['reason']}")
                    print(f"   Antigo: {update['old_param'][:20] if update['old_param'] else 'N/A'}...")
                    print(f"   Novo: {update['new_param'][:20] if update['new_param'] else 'N/A'}...")
            else:
                print("⚠️ Nenhum histórico disponível")
        
        elif escolha == "0":
            print("👋 Saindo...")
            break
        
        else:
            print("❌ Opção inválida")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "manual":
        comando_manual()
    else:
        testar_sistema()
