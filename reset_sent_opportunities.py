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
