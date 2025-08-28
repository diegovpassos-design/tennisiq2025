"""
Script para resetar oportunidades enviadas
Permite que as oportunidades sejam enviadas novamente
"""

import sqlite3
import logging
from pathlib import Path

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Reseta todas as oportunidades enviadas"""
    logger.info("🔄 Iniciando reset das oportunidades enviadas...")
    
    try:
        # Caminho do banco de dados
        db_path = Path("storage/database/prelive.db")
        
        # Garante que o diretório existe
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Conecta ao banco
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Cria a tabela se não existir
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sent_opportunities (
                event_id TEXT PRIMARY KEY,
                match_info TEXT,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Conta quantas oportunidades existem
        cursor.execute("SELECT COUNT(*) FROM sent_opportunities")
        count_before = cursor.fetchone()[0]
        logger.info(f"📊 Oportunidades enviadas atualmente: {count_before}")
        
        # Remove todas as oportunidades enviadas
        cursor.execute("DELETE FROM sent_opportunities")
        
        # Confirma as mudanças
        conn.commit()
        
        # Verifica se foi limpo
        cursor.execute("SELECT COUNT(*) FROM sent_opportunities")
        count_after = cursor.fetchone()[0]
        
        conn.close()
        
        logger.info(f"✅ Reset concluído! Removidas: {count_before}, Restantes: {count_after}")
        logger.info("🎯 Sistema pronto para detectar novas oportunidades!")
        
        if not db_path.exists():
            logger.warning("⚠️ Banco de dados não encontrado - criando novo")
            db_path.parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Conta quantas oportunidades estão marcadas como enviadas
            cursor.execute("SELECT COUNT(*) FROM sent_opportunities")
            count_before = cursor.fetchone()[0]
            
            logger.info(f"📊 Oportunidades enviadas atualmente: {count_before}")
            
            if count_before == 0:
                logger.info("✅ Nenhuma oportunidade para resetar")
                return
            
            # Reseta as oportunidades enviadas
            cursor.execute("DELETE FROM sent_opportunities")
            conn.commit()
            
            # Confirma o reset
            cursor.execute("SELECT COUNT(*) FROM sent_opportunities")
            count_after = cursor.fetchone()[0]
            
            logger.info(f"✅ Reset concluído!")
            logger.info(f"📊 Antes: {count_before} enviadas")
            logger.info(f"📊 Depois: {count_after} enviadas")
            logger.info("🚀 Agora as oportunidades podem ser enviadas novamente!")
        
    except Exception as e:
        logger.error(f"❌ Erro durante reset: {e}")
        raise

if __name__ == "__main__":
    main()
