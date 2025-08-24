"""
Sistema de banco de dados para armazenar oportunidades e movimento de linha
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import asdict
import logging
from pathlib import Path

from .prelive_scanner import Opportunity

logger = logging.getLogger(__name__)

class PreLiveDatabase:
    def __init__(self, db_path: str = "storage/database/prelive.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_database()
    
    def init_database(self):
        """Inicializa as tabelas do banco de dados"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Tabela de oportunidades
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS opportunities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id TEXT NOT NULL,
                    match_name TEXT NOT NULL,
                    start_utc TEXT NOT NULL,
                    league TEXT,
                    side TEXT NOT NULL,
                    odd REAL NOT NULL,
                    p_model REAL NOT NULL,
                    ev REAL NOT NULL,
                    p_market REAL NOT NULL,
                    confidence TEXT,
                    created_at TEXT NOT NULL,
                    status TEXT DEFAULT 'ACTIVE'
                )
            """)
            
            # Tabela de movimento de linha
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS line_movements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id TEXT NOT NULL,
                    home_od REAL NOT NULL,
                    away_od REAL NOT NULL,
                    timestamp TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)
            
            # Tabela para controlar oportunidades já enviadas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sent_opportunities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    opportunity_hash TEXT UNIQUE NOT NULL,
                    event_id TEXT NOT NULL,
                    match_name TEXT NOT NULL,
                    side TEXT NOT NULL,
                    odd REAL NOT NULL,
                    ev REAL NOT NULL,
                    sent_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL
                )
            """)
            
            # Tabela de resultados (para calcular CLV posteriormente)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS match_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id TEXT UNIQUE NOT NULL,
                    winner TEXT,
                    home_score TEXT,
                    away_score TEXT,
                    completed_at TEXT,
                    created_at TEXT NOT NULL
                )
            """)
            
            # Índices para performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_opportunities_event_id ON opportunities(event_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_opportunities_created_at ON opportunities(created_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_line_movements_event_id ON line_movements(event_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_line_movements_timestamp ON line_movements(timestamp)")
            
            conn.commit()
            logger.info("Banco de dados inicializado com sucesso")
    
    def save_opportunities(self, opportunities: List[Opportunity]) -> int:
        """Salva uma lista de oportunidades no banco"""
        if not opportunities:
            return 0
            
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            created_at = datetime.utcnow().isoformat()
            
            saved_count = 0
            for opp in opportunities:
                try:
                    cursor.execute("""
                        INSERT INTO opportunities (
                            event_id, match_name, start_utc, league, side,
                            odd, p_model, ev, p_market, confidence, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        opp.event_id, opp.match, opp.start_utc, opp.league,
                        opp.side, opp.odd, opp.p_model, opp.ev, 
                        opp.p_market, opp.confidence, created_at
                    ))
                    saved_count += 1
                except sqlite3.Error as e:
                    logger.warning(f"Erro ao salvar oportunidade {opp.match}: {e}")
            
            conn.commit()
            logger.info(f"Salvas {saved_count} oportunidades no banco")
            return saved_count
    
    def save_line_movement(self, event_id: str, home_od: float, away_od: float, 
                          timestamp: str = None) -> bool:
        """Salva movimento de linha de um evento"""
        if not timestamp:
            timestamp = datetime.utcnow().isoformat()
            
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO line_movements (event_id, home_od, away_od, timestamp, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (event_id, home_od, away_od, timestamp, datetime.utcnow().isoformat()))
                conn.commit()
                return True
        except sqlite3.Error as e:
            logger.error(f"Erro ao salvar movimento de linha: {e}")
            return False
    
    def get_active_opportunities(self, min_hours_ahead: int = 1) -> List[Dict]:
        """Busca oportunidades ativas (jogos que ainda não começaram)"""
        cutoff_time = (datetime.utcnow().replace(microsecond=0) + 
                      timedelta(hours=min_hours_ahead)).isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT event_id, match_name, start_utc, league,
                       side, odd, p_model, ev, p_market, confidence, created_at
                FROM opportunities 
                WHERE status = 'ACTIVE' AND start_utc > ?
                ORDER BY ev DESC, created_at DESC
            """, (cutoff_time,))
            
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def get_opportunities_for_notification(self, min_hours_ahead: int = 24) -> List[Dict]:
        """
        Busca oportunidades para NOTIFICAÇÃO (com tempo mínimo antes do jogo)
        Usado apenas para envio inicial via Telegram
        """
        cutoff_time = (datetime.utcnow().replace(microsecond=0) + 
                      timedelta(hours=min_hours_ahead)).isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT event_id, match_name, start_utc, league,
                       side, odd, p_model, ev, p_market, confidence, created_at
                FROM opportunities 
                WHERE status = 'ACTIVE' 
                  AND start_utc > ?
                  AND event_id NOT IN (
                      SELECT DISTINCT event_id FROM sent_opportunities
                  )
                ORDER BY ev DESC, created_at DESC
            """, (cutoff_time,))
            
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def get_line_movements(self, event_id: str) -> List[Dict]:
        """Busca histórico de movimento de linha de um evento"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT home_od, away_od, timestamp, created_at
                FROM line_movements 
                WHERE event_id = ?
                ORDER BY timestamp ASC
            """, (event_id,))
            
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def calculate_clv(self, event_id: str, side: str, original_odd: float) -> Optional[float]:
        """Calcula o Closing Line Value de uma oportunidade"""
        movements = self.get_line_movements(event_id)
        if not movements:
            return None
            
        # Pega a última odd (closing line)
        last_movement = movements[-1]
        closing_odd = last_movement["home_od"] if side == "HOME" else last_movement["away_od"]
        
        # CLV = (Closing Odd / Opening Odd) - 1
        clv = (closing_odd / original_odd) - 1
        return clv
    
    def get_statistics(self) -> Dict:
        """Retorna estatísticas gerais do sistema"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Total de oportunidades
            cursor.execute("SELECT COUNT(*) FROM opportunities")
            total_opportunities = cursor.fetchone()[0]
            
            # Oportunidades ativas
            cursor.execute("""
                SELECT COUNT(*) FROM opportunities 
                WHERE status = 'ACTIVE' AND start_utc > ?
            """, (datetime.utcnow().isoformat(),))
            active_opportunities = cursor.fetchone()[0]
            
            # EV médio das oportunidades ativas
            cursor.execute("""
                SELECT AVG(ev) FROM opportunities 
                WHERE status = 'ACTIVE' AND start_utc > ?
            """, (datetime.utcnow().isoformat(),))
            avg_ev = cursor.fetchone()[0] or 0
            
            # Distribuição por confiança
            cursor.execute("""
                SELECT confidence, COUNT(*) FROM opportunities 
                WHERE status = 'ACTIVE' AND start_utc > ?
                GROUP BY confidence
            """, (datetime.utcnow().isoformat(),))
            confidence_dist = dict(cursor.fetchall())
            
            return {
                "total_opportunities": total_opportunities,
                "active_opportunities": active_opportunities,
                "average_ev": round(avg_ev, 4),
                "confidence_distribution": confidence_dist
            }
    
    def mark_opportunity_expired(self, event_id: str):
        """Marca oportunidades como expiradas"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE opportunities 
                SET status = 'EXPIRED' 
                WHERE event_id = ? AND status = 'ACTIVE'
            """, (event_id,))
            conn.commit()
    
    def cleanup_old_data(self, days_old: int = 30):
        """Remove dados antigos do banco"""
        cutoff_date = (datetime.utcnow() - timedelta(days=days_old)).isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Remove oportunidades antigas
            cursor.execute("""
                DELETE FROM opportunities 
                WHERE created_at < ? AND status != 'ACTIVE'
            """, (cutoff_date,))
            
            # Remove movimentos de linha antigos
            cursor.execute("""
                DELETE FROM line_movements 
                WHERE created_at < ?
            """, (cutoff_date,))
            
            conn.commit()
            logger.info(f"Limpeza de dados antigos concluída (> {days_old} dias)")

    def is_opportunity_already_sent(self, opportunity: 'Opportunity') -> bool:
        """Verifica se uma oportunidade já foi enviada"""
        opportunity_hash = self._generate_opportunity_hash(opportunity)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM sent_opportunities 
                WHERE opportunity_hash = ? AND expires_at > ?
            """, (opportunity_hash, datetime.utcnow().isoformat()))
            
            return cursor.fetchone()[0] > 0

    def mark_opportunity_as_sent(self, opportunity: 'Opportunity', expires_hours: int = 24):
        """Marca uma oportunidade como enviada"""
        opportunity_hash = self._generate_opportunity_hash(opportunity)
        expires_at = datetime.utcnow() + timedelta(hours=expires_hours)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO sent_opportunities
                (opportunity_hash, event_id, match_name, side, odd, ev, sent_at, expires_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                opportunity_hash,
                opportunity.event_id,
                opportunity.match,
                opportunity.side,
                opportunity.odd,
                opportunity.ev,
                datetime.utcnow().isoformat(),
                expires_at.isoformat()
            ))
            
    def _generate_opportunity_hash(self, opportunity: 'Opportunity') -> str:
        """Gera hash único para uma oportunidade"""
        import hashlib
        
        # Cria identificador único baseado em event_id, side e odd aproximado
        hash_string = f"{opportunity.event_id}:{opportunity.side}:{round(opportunity.odd, 2)}"
        return hashlib.md5(hash_string.encode()).hexdigest()

    def cleanup_expired_sent_opportunities(self):
        """Remove oportunidades enviadas que já expiraram"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM sent_opportunities 
                WHERE expires_at < ?
            """, (datetime.utcnow().isoformat(),))
            
            deleted_count = cursor.rowcount
            if deleted_count > 0:
                logger.info(f"Removidas {deleted_count} oportunidades enviadas expiradas")
    
    def reset_sent_opportunities(self):
        """RESET: Remove todas as oportunidades enviadas para permitir reenvio"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM sent_opportunities")
            
            deleted_count = cursor.rowcount
            logger.info(f"RESET: Removidas {deleted_count} oportunidades da tabela anti-duplicatas")
            return deleted_count

# Funções utilitárias
from datetime import timedelta

def export_opportunities_to_json(db: PreLiveDatabase, 
                                filename: str = None) -> str:
    """Exporta oportunidades ativas para JSON"""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"storage/exports/opportunities_{timestamp}.json"
    
    opportunities = db.get_active_opportunities()
    
    Path(filename).parent.mkdir(parents=True, exist_ok=True)
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(opportunities, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Oportunidades exportadas para {filename}")
    return filename
