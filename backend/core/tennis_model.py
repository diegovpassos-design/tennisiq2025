"""
Sistema de dados e rankings para o modelo de probabilidades do TennisQ
"""

import json
import requests
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class PlayerStats:
    """Estatísticas de um jogador"""
    name: str
    ranking: int = 999  # ATP/WTA ranking
    elo_rating: float = 1500.0  # Elo geral
    elo_surface: Dict[str, float] = None  # Elo por superfície
    recent_form: float = 0.5  # Forma recente (0-1)
    matches_last_30d: int = 0  # Jogos últimos 30 dias
    win_rate_surface: Dict[str, float] = None  # Win rate por superfície
    last_updated: str = ""
    
    def __post_init__(self):
        if self.elo_surface is None:
            self.elo_surface = {
                "hard": 1500.0,
                "clay": 1500.0, 
                "grass": 1500.0,
                "indoor": 1500.0
            }
        if self.win_rate_surface is None:
            self.win_rate_surface = {
                "hard": 0.5,
                "clay": 0.5,
                "grass": 0.5, 
                "indoor": 0.5
            }

class PlayerDatabase:
    """Banco de dados de jogadores e estatísticas"""
    
    def __init__(self, db_path: str = "storage/database/players.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_database()
        
    def init_database(self):
        """Inicializa tabelas do banco"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Tabela de jogadores
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS players (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    ranking INTEGER DEFAULT 999,
                    elo_rating REAL DEFAULT 1500.0,
                    elo_hard REAL DEFAULT 1500.0,
                    elo_clay REAL DEFAULT 1500.0,
                    elo_grass REAL DEFAULT 1500.0,
                    elo_indoor REAL DEFAULT 1500.0,
                    recent_form REAL DEFAULT 0.5,
                    matches_last_30d INTEGER DEFAULT 0,
                    winrate_hard REAL DEFAULT 0.5,
                    winrate_clay REAL DEFAULT 0.5,
                    winrate_grass REAL DEFAULT 0.5,
                    winrate_indoor REAL DEFAULT 0.5,
                    last_updated TEXT
                )
            """)
            
            # Tabela de head-to-head
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS head_to_head (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player1 TEXT NOT NULL,
                    player2 TEXT NOT NULL,
                    player1_wins INTEGER DEFAULT 0,
                    player2_wins INTEGER DEFAULT 0,
                    last_match_date TEXT,
                    surface_breakdown TEXT,  -- JSON com breakdown por superfície
                    last_updated TEXT
                )
            """)
            
            # Tabela de resultados recentes
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS recent_matches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_name TEXT NOT NULL,
                    opponent TEXT,
                    result TEXT,  -- "W" ou "L"
                    surface TEXT,
                    tournament TEXT,
                    date TEXT,
                    score TEXT
                )
            """)
            
            # Índices
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_players_name ON players(name)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_h2h_players ON head_to_head(player1, player2)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_recent_player_date ON recent_matches(player_name, date)")
            
            conn.commit()
            logger.info("Banco de dados de jogadores inicializado")
    
    def get_or_create_player(self, name: str, use_real_data: bool = False, 
                           real_data_provider=None) -> PlayerStats:
        """Busca jogador no banco ou cria novo com valores padrão/reais"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM players WHERE name = ?", (name,))
            row = cursor.fetchone()
            
            if row:
                # Verifica se dados estão desatualizados (>7 dias)
                last_updated = row[14]
                try:
                    update_date = datetime.fromisoformat(last_updated)
                    days_old = (datetime.utcnow() - update_date).days
                    
                    # Se dados são antigos e temos provedor de dados reais, atualiza
                    if days_old > 7 and use_real_data and real_data_provider:
                        logger.info(f"Dados de {name} desatualizados ({days_old} dias). Atualizando...")
                        return real_data_provider.update_player_with_real_data(name, self)
                except:
                    pass  # Se erro na data, usa dados existentes
                
                # Converte dados do banco para PlayerStats
                return PlayerStats(
                    name=row[1],
                    ranking=row[2],
                    elo_rating=row[3],
                    elo_surface={
                        "hard": row[4],
                        "clay": row[5], 
                        "grass": row[6],
                        "indoor": row[7]
                    },
                    recent_form=row[8],
                    matches_last_30d=row[9],
                    win_rate_surface={
                        "hard": row[10],
                        "clay": row[11],
                        "grass": row[12],
                        "indoor": row[13]
                    },
                    last_updated=row[14]
                )
            else:
                # Jogador novo - busca dados reais se disponível
                if use_real_data and real_data_provider:
                    logger.info(f"Novo jogador {name} - buscando dados reais")
                    return real_data_provider.update_player_with_real_data(name, self)
                else:
                    # Cria novo jogador com valores simulados mais realísticos
                    import random
                    import hashlib
                    
                    # Usa hash do nome para gerar valores consistentes mas variados
                    name_hash = int(hashlib.md5(name.encode()).hexdigest()[:8], 16)
                    random.seed(name_hash)
                    
                    # Simula ranking realístico (top 10, top 50, top 100, etc.)
                    rank_tier = random.choices(
                        [random.randint(1, 10), random.randint(11, 50), random.randint(51, 150), 
                         random.randint(151, 300), random.randint(301, 800)],
                        weights=[5, 15, 30, 35, 15]  # Distribuição realística
                    )[0]
                    
                    # Elo baseado no ranking (top players = elo alto)
                    base_elo = 1800 - (rank_tier - 1) * 0.8  # Top 1 = ~1800, Rank 500 = ~1400
                    elo_variation = random.uniform(-50, 50)
                    
                    new_player = PlayerStats(
                        name=name,
                        ranking=rank_tier,
                        elo_rating=base_elo + elo_variation,
                        elo_surface={
                            "hard": base_elo + elo_variation + random.uniform(-30, 30),
                            "clay": base_elo + elo_variation + random.uniform(-30, 30),
                            "grass": base_elo + elo_variation + random.uniform(-30, 30),
                            "indoor": base_elo + elo_variation + random.uniform(-30, 30)
                        },
                        recent_form=random.uniform(0.3, 0.8),  # Forma entre 30% e 80%
                        matches_last_30d=random.randint(2, 12),  # Entre 2 e 12 jogos por mês
                        win_rate_surface={
                            "hard": random.uniform(0.4, 0.7),
                            "clay": random.uniform(0.4, 0.7),
                            "grass": random.uniform(0.4, 0.7),
                            "indoor": random.uniform(0.4, 0.7)
                        }
                    )
                    
                    self.save_player(new_player)
                    return new_player
    
    def save_player(self, player: PlayerStats):
        """Salva/atualiza jogador no banco"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO players (
                    name, ranking, elo_rating, elo_hard, elo_clay, elo_grass, elo_indoor,
                    recent_form, matches_last_30d, winrate_hard, winrate_clay, 
                    winrate_grass, winrate_indoor, last_updated
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                player.name, player.ranking, player.elo_rating,
                player.elo_surface["hard"], player.elo_surface["clay"],
                player.elo_surface["grass"], player.elo_surface["indoor"],
                player.recent_form, player.matches_last_30d,
                player.win_rate_surface["hard"], player.win_rate_surface["clay"],
                player.win_rate_surface["grass"], player.win_rate_surface["indoor"],
                datetime.utcnow().isoformat()
            ))
            conn.commit()
    
    def get_head_to_head(self, player1: str, player2: str) -> Dict:
        """Busca histórico head-to-head entre dois jogadores"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Tenta ambas as ordens
            cursor.execute("""
                SELECT player1_wins, player2_wins, surface_breakdown 
                FROM head_to_head 
                WHERE (player1 = ? AND player2 = ?) OR (player1 = ? AND player2 = ?)
            """, (player1, player2, player2, player1))
            
            row = cursor.fetchone()
            if row:
                return {
                    "player1_wins": row[0],
                    "player2_wins": row[1], 
                    "surface_breakdown": json.loads(row[2]) if row[2] else {}
                }
            else:
                return {"player1_wins": 0, "player2_wins": 0, "surface_breakdown": {}}

class SophisticatedTennisModel:
    """Modelo sofisticado de probabilidades para tênis"""
    
    def __init__(self, player_db: PlayerDatabase = None, use_real_data: bool = True, 
                 api_token: str = None, api_base: str = None):
        self.player_db = player_db or PlayerDatabase()
        self.use_real_data = use_real_data
        self.real_data_provider = None
        
        # Inicializa provedor de dados reais se disponível
        if use_real_data and api_token and api_base:
            try:
                from .real_data_provider import RealDataProvider
                self.real_data_provider = RealDataProvider(api_token, api_base)
                logger.info("RealDataProvider inicializado - usando dados reais da API")
            except Exception as e:
                logger.warning(f"Erro ao inicializar RealDataProvider: {e}")
                self.use_real_data = False
        
        # Pesos dos fatores (devem somar ~1.0)
        self.weights = {
            "ranking": 0.30,      # 30% - Diferença de ranking
            "elo_surface": 0.25,  # 25% - Elo na superfície específica
            "recent_form": 0.20,  # 20% - Forma recente
            "head_to_head": 0.15, # 15% - Histórico direto
            "fatigue": 0.10       # 10% - Fadiga/jogos recentes
        }
    
    def calculate_probability(self, home_player: str, away_player: str, 
                            surface: str = "hard", tournament_level: str = "regular") -> float:
        """
        Calcula probabilidade do home_player vencer
        
        Args:
            home_player: Nome do jogador 1
            away_player: Nome do jogador 2  
            surface: Superfície (hard, clay, grass, indoor)
            tournament_level: Nível do torneio (grand_slam, masters, regular)
            
        Returns:
            Probabilidade entre 0.05 e 0.95
        """
        try:
            # Busca dados dos jogadores (com dados reais se disponível)
            player1 = self.player_db.get_or_create_player(
                home_player, 
                use_real_data=self.use_real_data,
                real_data_provider=self.real_data_provider
            )
            player2 = self.player_db.get_or_create_player(
                away_player,
                use_real_data=self.use_real_data, 
                real_data_provider=self.real_data_provider
            )
            
            # Verifica se temos dados reais ou apenas padrões
            has_real_data = (self._has_real_player_data(player1) and 
                           self._has_real_player_data(player2))
            
            if has_real_data:
                # Usa método tradicional com dados reais
                result = self._calculate_with_real_data(player1, player2, surface)
                probability = result['final_probability']
            else:
                # Usa método alternativo baseado em análise de nomes e padrões
                result = self._calculate_with_name_analysis(player1, player2, surface)
                probability = result['final_probability']
            
            # Garantir que está no range válido
            return max(0.05, min(0.95, probability))
            
        except Exception as e:
            logger.warning(f"Erro no cálculo de probabilidade: {e}")
            return 0.50  # Default 50% em caso de erro
            
            # Ajuste por nível do torneio
            if tournament_level == "grand_slam":
                # Favoritos tendem a ser mais consistentes em Grand Slams
                probability = 0.5 + (probability - 0.5) * 1.1
            elif tournament_level == "masters":
                probability = 0.5 + (probability - 0.5) * 1.05
            
            # Limita entre 5% e 95%
            return max(0.05, min(0.95, probability))
            
        except Exception as e:
            logger.warning(f"Erro no cálculo de probabilidade: {e}")
            return 0.50  # Default 50% em caso de erro
    
    def _calculate_ranking_factor(self, player1: PlayerStats, player2: PlayerStats) -> float:
        """Calcula fator baseado na diferença de ranking"""
        # Converte rankings para escala logarítmica (ranking baixo = melhor)
        rank1_log = max(1, min(500, player1.ranking))
        rank2_log = max(1, min(500, player2.ranking))
        
        # Diferença logarítmica normalizada
        rank_diff = (rank2_log - rank1_log) / 200.0  # Normaliza diferença
        
        # Converte para probabilidade (sigmoide)
        probability = 1 / (1 + pow(10, -rank_diff))
        
        return probability
    
    def _calculate_elo_factor(self, player1: PlayerStats, player2: PlayerStats, surface: str) -> float:
        """Calcula fator baseado no Elo da superfície"""
        elo1 = player1.elo_surface.get(surface, 1500)
        elo2 = player2.elo_surface.get(surface, 1500)
        
        # Fórmula do Elo esperado
        expected = 1 / (1 + pow(10, (elo2 - elo1) / 400))
        
        return expected
    
    def _calculate_form_factor(self, player1: PlayerStats, player2: PlayerStats) -> float:
        """Calcula fator baseado na forma recente"""
        form1 = player1.recent_form
        form2 = player2.recent_form
        
        # Normaliza diferença de forma
        form_diff = (form1 - form2) / 2.0 + 0.5
        
        return max(0.1, min(0.9, form_diff))
    
    def _calculate_h2h_factor(self, player1: str, player2: str, surface: str) -> float:
        """Calcula fator baseado no head-to-head"""
        h2h = self.player_db.get_head_to_head(player1, player2)
        
        total_matches = h2h["player1_wins"] + h2h["player2_wins"]
        
        if total_matches == 0:
            return 0.5  # Sem histórico = 50%
        
        # Win rate do player1
        win_rate = h2h["player1_wins"] / total_matches
        
        # Reduz impacto se poucos jogos
        confidence = min(1.0, total_matches / 10.0)  # Máxima confiança com 10+ jogos
        
        # Interpola entre 50% (sem confiança) e win_rate real
        return 0.5 + (win_rate - 0.5) * confidence
    
    def _calculate_fatigue_factor(self, player1: PlayerStats, player2: PlayerStats) -> float:
        """Calcula fator de fadiga baseado em jogos recentes"""
        # Mais jogos = mais fadiga = menor probabilidade
        fatigue1 = min(0.2, player1.matches_last_30d / 15.0)  # Max 20% penalidade
        fatigue2 = min(0.2, player2.matches_last_30d / 15.0)
        
        # Player1 menos fatigado = maior probabilidade
        fatigue_advantage = (fatigue2 - fatigue1) / 0.4 + 0.5
        
        return max(0.3, min(0.7, fatigue_advantage))
    
    def update_player_stats_from_rankings(self, api_token: str = None):
        """
        Atualiza rankings dos jogadores usando APIs externas
        TODO: Implementar integração com APIs de rankings
        """
        # Placeholder para integração futura com:
        # - ATP/WTA official rankings
        # - Tennis data APIs  
        # - Resultados recentes
        pass
    
    def simulate_match_probabilities(self, player1: str, player2: str, surface: str = "hard"):
        """Simula probabilidades detalhadas para debug"""
        p1_stats = self.player_db.get_or_create_player(player1)
        p2_stats = self.player_db.get_or_create_player(player2)
        
        factors = {
            "ranking": self._calculate_ranking_factor(p1_stats, p2_stats),
            "elo_surface": self._calculate_elo_factor(p1_stats, p2_stats, surface),
            "recent_form": self._calculate_form_factor(p1_stats, p2_stats),
            "head_to_head": self._calculate_h2h_factor(player1, player2, surface),
            "fatigue": self._calculate_fatigue_factor(p1_stats, p2_stats)
        }
        
        final_prob = self.calculate_probability(player1, player2, surface)
        
        return {
            "player1": player1,
            "player2": player2,
            "surface": surface,
            "factors": factors,
            "weights": self.weights,
            "final_probability": final_prob,
            "player1_stats": p1_stats,
            "player2_stats": p2_stats
        }

    def _has_real_player_data(self, player: PlayerStats) -> bool:
        """Verifica se o jogador tem dados reais ou apenas valores padrão"""
        return (player.ranking != 999 and 
                player.recent_form != 0.50 and 
                player.elo_rating != 1500)
    
    def _calculate_with_real_data(self, player1: PlayerStats, player2: PlayerStats, surface: str) -> dict:
        """Cálculo original usando dados reais dos jogadores"""
        # Fator ranking
        ranking_diff = (player2.ranking - player1.ranking) / 200
        ranking_factor = max(0.4, min(1.6, 1.0 + ranking_diff))
        
        # ELO ratings por superfície
        elo1 = player1.elo_surface.get(surface, player1.elo_rating)
        elo2 = player2.elo_surface.get(surface, player2.elo_rating)
        elo_diff = elo1 - elo2
        elo_factor = 1 / (1 + 10 ** (-elo_diff / 400))
        
        # Forma recente
        form_factor = (player1.recent_form / (player1.recent_form + player2.recent_form))
        
        # Win rate na superfície
        winrate1 = player1.win_rate_surface.get(surface, 0.5)
        winrate2 = player2.win_rate_surface.get(surface, 0.5)
        surface_factor = winrate1 / (winrate1 + winrate2)
        
        # Combinação ponderada
        probability = (
            0.30 * ranking_factor + 
            0.35 * elo_factor + 
            0.20 * form_factor + 
            0.15 * surface_factor
        ) / 2
        
        return {
            'final_probability': probability,
            'factors': {
                'ranking': ranking_factor,
                'elo': elo_factor,
                'form': form_factor,
                'surface': surface_factor
            }
        }
    
    def _calculate_with_name_analysis(self, player1: PlayerStats, player2: PlayerStats, surface: str) -> dict:
        """Cálculo alternativo baseado em análise dos nomes e contexto"""
        # Análise básica dos nomes
        name1_score = self._analyze_player_name(player1.name)
        name2_score = self._analyze_player_name(player2.name)
        
        # Fatores de superfície baseados em padrões conhecidos
        surface_bonus1 = self._get_surface_bonus_by_name(player1.name, surface)
        surface_bonus2 = self._get_surface_bonus_by_name(player2.name, surface)
        
        # Probabilidade base ajustada
        base_prob = 0.5
        name_adjustment = (name1_score - name2_score) * 0.1
        surface_adjustment = (surface_bonus1 - surface_bonus2) * 0.05
        
        probability = max(0.2, min(0.8, base_prob + name_adjustment + surface_adjustment))
        
        return {
            'final_probability': probability,
            'factors': {
                'name_analysis': name1_score - name2_score,
                'surface_bonus': surface_bonus1 - surface_bonus2,
                'method': 'name_based_fallback'
            }
        }
    
    def _analyze_player_name(self, name: str) -> float:
        """Analisa o nome do jogador para inferir nível (método simplificado)"""
        # Nomes mais "reconhecidos" tendem a ter certas características
        name_lower = name.lower()
        
        # Padrões de nomes de top players
        if any(pattern in name_lower for pattern in ['djokovic', 'nadal', 'federer', 'alcaraz', 'medvedev']):
            return 0.9
        elif any(pattern in name_lower for pattern in ['sinner', 'rublev', 'tsitsipas', 'zverev']):
            return 0.8
        elif len(name.split()) >= 2 and len(name) > 10:  # Nomes completos tendem a ser mais estabelecidos
            return 0.6
        else:
            return 0.5
    
    def _get_surface_bonus_by_name(self, name: str, surface: str) -> float:
        """Bonus baseado em padrões conhecidos de superfície"""
        name_lower = name.lower()
        
        # Especialistas conhecidos em clay
        if surface == 'clay' and any(pattern in name_lower for pattern in ['nadal', 'alcaraz']):
            return 0.2
        # Especialistas em grass
        elif surface == 'grass' and any(pattern in name_lower for pattern in ['federer', 'djokovic']):
            return 0.15
        # Especialistas em hard court
        elif surface == 'hard' and any(pattern in name_lower for pattern in ['medvedev', 'sinner']):
            return 0.1
        
        return 0.0

# Função para popular banco com dados básicos
def populate_initial_data():
    """Popula banco com alguns jogadores conhecidos para testes"""
    db = PlayerDatabase()
    
    # Alguns jogadores top com dados aproximados
    top_players = [
        PlayerStats("Novak Djokovic", ranking=1, elo_rating=2100, 
                   elo_surface={"hard": 2120, "clay": 2050, "grass": 2100, "indoor": 2130},
                   recent_form=0.85, win_rate_surface={"hard": 0.87, "clay": 0.82, "grass": 0.85, "indoor": 0.88}),
        
        PlayerStats("Carlos Alcaraz", ranking=2, elo_rating=2080,
                   elo_surface={"hard": 2070, "clay": 2100, "grass": 2050, "indoor": 2060},
                   recent_form=0.90, win_rate_surface={"hard": 0.84, "clay": 0.89, "grass": 0.80, "indoor": 0.83}),
        
        PlayerStats("Daniil Medvedev", ranking=3, elo_rating=2050,
                   elo_surface={"hard": 2090, "clay": 1980, "grass": 2020, "indoor": 2100},
                   recent_form=0.75, win_rate_surface={"hard": 0.88, "clay": 0.65, "grass": 0.78, "indoor": 0.90}),
        
        PlayerStats("Jannik Sinner", ranking=4, elo_rating=2030,
                   elo_surface={"hard": 2040, "clay": 2020, "grass": 2000, "indoor": 2050},
                   recent_form=0.88, win_rate_surface={"hard": 0.85, "clay": 0.81, "grass": 0.77, "indoor": 0.87}),
        
        PlayerStats("Rafael Nadal", ranking=50, elo_rating=1950,  # Ranking baixo por lesões
                   elo_surface={"hard": 1920, "clay": 2150, "grass": 1880, "indoor": 1900},
                   recent_form=0.60, win_rate_surface={"hard": 0.78, "clay": 0.94, "grass": 0.70, "indoor": 0.75})
    ]
    
    for player in top_players:
        db.save_player(player)
    
    logger.info("Dados iniciais populados no banco")

if __name__ == "__main__":
    # Testa o modelo
    populate_initial_data()
    
    model = SophisticatedTennisModel()
    
    # Simula alguns matchups
    matchups = [
        ("Novak Djokovic", "Carlos Alcaraz", "hard"),
        ("Rafael Nadal", "Novak Djokovic", "clay"),
        ("Daniil Medvedev", "Jannik Sinner", "indoor")
    ]
    
    for p1, p2, surface in matchups:
        result = model.simulate_match_probabilities(p1, p2, surface)
        print(f"\n{p1} vs {p2} ({surface})")
        print(f"Probabilidade {p1}: {result['final_probability']:.1%}")
        print(f"Fatores: {result['factors']}")
