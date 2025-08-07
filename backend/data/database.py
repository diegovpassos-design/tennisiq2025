"""
Database manager for TennisIQ - SQLite/JSON
"""
import os
import json
from datetime import datetime

class DatabaseManager:
    def __init__(self):
        # Usar JSON simples (funciona local e na nuvem)
        self.storage_path = "storage/database"
        self.init_storage()
    
    def init_storage(self):
        """Initialize storage directories"""
        try:
            os.makedirs(self.storage_path, exist_ok=True)
            os.makedirs("backend/results", exist_ok=True)
            print("✅ Storage inicializado com sucesso")
        except Exception as e:
            print(f"❌ Erro ao inicializar storage: {e}")
    
    def save_partida_analisada(self, partida_data):
        """Save analyzed match to database"""
        try:
            json_file = "storage/database/partidas_analisadas.json"
            os.makedirs(os.path.dirname(json_file), exist_ok=True)
            
            if os.path.exists(json_file):
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = []
            
            data.append({
                'timestamp': datetime.now().isoformat(),
                'partida': partida_data,
                'resultado': 'PENDENTE'
            })
            
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Erro ao salvar: {e}")
    
    def get_estatisticas(self):
        """Get statistics from database"""
        try:
            json_file = "backend/results/historico_apostas.json"
            if os.path.exists(json_file):
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    total = len(data)
                    greens = sum(1 for item in data if item.get('resultado') == 'GREEN')
                    taxa = (greens / total * 100) if total > 0 else 0
                    return {
                        'total_apostas': total,
                        'total_greens': greens,
                        'taxa_acerto': round(taxa, 1)
                    }
        except Exception as e:
            print(f"❌ Erro ao ler estatísticas: {e}")
        
        return {'total_apostas': 0, 'total_greens': 0, 'taxa_acerto': 0}

# Global instance
db_manager = DatabaseManager()
