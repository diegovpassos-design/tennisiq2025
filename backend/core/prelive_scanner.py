"""
TennisQ - Sistema de Análise de Oportunidades Pré-Live
Escaneia jogos futuros de tênis para identificar odds desajustadas
"""

import requests
import json
import time
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass

# Importa o modelo simplificado
from .tennis_model_simple import SophisticatedTennisModel, PlayerDatabase

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MatchEvent:
    """Representa um jogo de tênis futuro"""
    event_id: str
    home: str
    away: str
    start_utc: datetime
    league: str
    surface: str = "hard"  # padrão
    
@dataclass
class OddsData:
    """Dados de odds de um jogo"""
    home_od: float
    away_od: float
    timestamp: str
    
@dataclass
class Opportunity:
    """Oportunidade de aposta identificada"""
    event_id: str
    match: str
    start_utc: str
    league: str
    side: str  # "HOME" ou "AWAY"
    odd: float
    p_model: float
    ev: float
    p_market: float
    confidence: str

class PreLiveScanner:
    def __init__(self, api_token: str, api_base: str):
        self.api_token = api_token
        self.api_base = api_base
        self.sport_id_tennis = 13  # ID do tênis na b365api (confirmado pelo teste)
        
        # Inicializa modelo sofisticado
        self.tennis_model = SophisticatedTennisModel(
            use_real_data=True,
            api_token=api_token,
            api_base=api_base
        )
        
        logger.info("PreLiveScanner inicializado com modelo sofisticado")
        
    def get_upcoming_events_original(self, hours_ahead: int = 48) -> List[MatchEvent]:
        """Busca jogos de tênis nas próximas X horas - MÉTODO ORIGINAL (backup)"""
        try:
            url = f"{self.api_base}/v3/events/upcoming"
            params = {
                "sport_id": self.sport_id_tennis,
                "token": self.api_token
            }
            
            logger.info(f"Buscando jogos futuros nas próximas {hours_ahead}h...")
            response = requests.get(url, params=params, timeout=20)
            response.raise_for_status()
            
            data = response.json()
            events = data.get("results", [])
            
            cutoff = datetime.utcnow() + timedelta(hours=hours_ahead)
            now = datetime.utcnow()
            matches = []
            
            for event in events:
                try:
                    # Tenta diferentes campos de timestamp
                    timestamp = event.get("time") or event.get("start_time") or event.get("time_status")
                    if not timestamp:
                        continue
                        
                    # Converte para datetime - simplifica para sempre usar unix timestamp
                    dt = datetime.utcfromtimestamp(int(timestamp))
                    
                    # Verifica se o evento está na janela de tempo (futuro e dentro de 72h)
                    if dt >= now and dt <= cutoff:
                        # Extrai nomes dos times
                        home_name = ""
                        away_name = ""
                        
                        if isinstance(event.get("home"), dict):
                            home_name = event["home"].get("name", "")
                        else:
                            home_name = str(event.get("home", ""))
                            
                        if isinstance(event.get("away"), dict):
                            away_name = event["away"].get("name", "")
                        else:
                            away_name = str(event.get("away", ""))
                        
                        # Liga
                        league_name = ""
                        if isinstance(event.get("league"), dict):
                            league_name = event["league"].get("name", "")
                        else:
                            league_name = str(event.get("league", ""))
                        
                        match = MatchEvent(
                            event_id=str(event.get("id", "")),
                            home=home_name,
                            away=away_name,
                            start_utc=dt,
                            league=league_name,
                            surface=self._detect_surface(league_name)
                        )
                        
                        if match.home and match.away and match.event_id:
                            matches.append(match)
                            
                except Exception as e:
                    logger.warning(f"Erro ao processar evento: {e}")
                    continue
                    
            logger.info(f"Encontrados {len(matches)} jogos nas próximas {hours_ahead}h")
            return matches
            
        except Exception as e:
            logger.error(f"Erro ao buscar jogos futuros: {e}")
            return []
    
    def get_upcoming_events(self, hours_ahead: int = 48, max_pages: int = 3) -> List[MatchEvent]:
        """
        Busca jogos de tênis com PAGINAÇÃO para superar limite de 50
        Testa diferentes estratégias para obter mais jogos
        """
        try:
            all_matches = []
            url = f"{self.api_base}/v3/events/upcoming"
            
            logger.info(f"🔍 Buscando jogos com paginação (até {max_pages} páginas, {hours_ahead}h ahead)")
            
            # ESTRATÉGIA 1: Testar parâmetro limit alto
            logger.info("🧪 TESTE 1: Parâmetro limit=200")
            params_limit = {
                "sport_id": self.sport_id_tennis,
                "token": self.api_token,
                "limit": 200
            }
            
            response = requests.get(url, params=params_limit, timeout=20)
            if response.status_code == 200:
                data = response.json()
                events = data.get("results", [])
                logger.info(f"📊 Com limit=200: {len(events)} eventos retornados")
                
                if len(events) > 50:
                    logger.info("✅ SUCESSO! Parâmetro limit funciona - usando este método")
                    return self._process_events_with_time_filter(events, hours_ahead)
            
            # ESTRATÉGIA 2: Paginação manual
            logger.info("🧪 TESTE 2: Paginação manual (page=1,2,3...)")
            
            for page in range(1, max_pages + 1):
                params_page = {
                    "sport_id": self.sport_id_tennis,
                    "token": self.api_token,
                    "page": page,
                    "limit": 100
                }
                
                logger.info(f"📄 Buscando página {page}...")
                response = requests.get(url, params=params_page, timeout=20)
                
                if response.status_code != 200:
                    logger.warning(f"⚠️ Erro na página {page}: {response.status_code}")
                    continue
                    
                data = response.json()
                events = data.get("results", [])
                
                logger.info(f"📊 Página {page}: {len(events)} eventos brutos")
                
                if not events:
                    logger.info(f"📭 Sem eventos na página {page} - fim da paginação")
                    break
                
                # Processa eventos desta página
                page_matches = self._process_events_with_time_filter(events, hours_ahead)
                all_matches.extend(page_matches)
                
                logger.info(f"✅ Página {page}: {len(page_matches)} jogos válidos adicionados")
                
                # Se retornou menos que o esperado, pode ser última página
                if len(events) < 50:
                    logger.info(f"📋 Página {page} retornou {len(events)} < 50 - provavelmente última página")
                    break
            
            # ESTRATÉGIA 3: Múltiplas requests por dia (se ainda temos poucos jogos)
            if len(all_matches) < 50:
                logger.info("🧪 TESTE 3: Requests separadas por dia")
                
                from datetime import datetime, timedelta
                today = datetime.utcnow().date()
                
                for day_offset in range(3):  # Próximos 3 dias
                    target_date = today + timedelta(days=day_offset)
                    day_str = target_date.strftime("%Y-%m-%d")
                    
                    params_day = {
                        "sport_id": self.sport_id_tennis,
                        "token": self.api_token,
                        "day": day_str
                    }
                    
                    logger.info(f"📅 Buscando dia {day_str}...")
                    response = requests.get(url, params=params_day, timeout=20)
                    
                    if response.status_code == 200:
                        data = response.json()
                        events = data.get("results", [])
                        
                        logger.info(f"📊 Dia {day_str}: {len(events)} eventos")
                        
                        day_matches = self._process_events_with_time_filter(events, hours_ahead)
                        
                        # Evita duplicatas
                        new_matches = []
                        existing_ids = {m.event_id for m in all_matches}
                        
                        for match in day_matches:
                            if match.event_id not in existing_ids:
                                new_matches.append(match)
                                existing_ids.add(match.event_id)
                        
                        all_matches.extend(new_matches)
                        logger.info(f"✅ Dia {day_str}: {len(new_matches)} novos jogos adicionados")
            
            logger.info(f"🎯 TOTAL FINAL: {len(all_matches)} jogos encontrados")
            return all_matches
            
        except Exception as e:
            logger.error(f"❌ Erro na busca paginada: {e}")
            # Fallback para método original
            logger.info("🔄 Usando método original como fallback...")
            return self.get_upcoming_events_original(hours_ahead)
    
    def _process_events_with_time_filter(self, events, hours_ahead):
        """Processa eventos aplicando filtro de tempo"""
        cutoff = datetime.utcnow() + timedelta(hours=hours_ahead)
        now = datetime.utcnow()
        matches = []
        
        for event in events:
            try:
                # Tenta diferentes campos de timestamp
                timestamp = event.get("time") or event.get("start_time") or event.get("time_status")
                if not timestamp:
                    continue
                    
                # Converte para datetime - simplifica para sempre usar unix timestamp
                dt = datetime.utcfromtimestamp(int(timestamp))
                
                # Verifica se o evento está na janela de tempo (futuro e dentro de 72h)
                if dt >= now and dt <= cutoff:
                    # Extrai nomes dos times
                    home_name = event.get("home", {}).get("name", "")
                    away_name = event.get("away", {}).get("name", "")
                    league_name = event.get("league", {}).get("name", "Unknown")
                    
                    match = MatchEvent(
                        event_id=str(event.get("id", "")),
                        home=home_name,
                        away=away_name,
                        start_utc=dt,
                        league=league_name,
                        surface=self._detect_surface(league_name)
                    )
                    
                    if match.home and match.away and match.event_id:
                        matches.append(match)
                        
            except Exception as e:
                logger.warning(f"⚠️ Erro ao processar evento: {e}")
                continue
        
        return matches
    
    def get_event_odds(self, event_id: str) -> Optional[OddsData]:
        """Busca as odds pré-jogo de um evento específico"""
        try:
            url = f"{self.api_base}/v2/event/odds"
            params = {
                "token": self.api_token,
                "event_id": event_id
            }
            
            response = requests.get(url, params=params, timeout=20)
            response.raise_for_status()
            
            data = response.json()
            results = data.get("results", {})
            
            if not results:
                return None
                
            odds_data = results.get("odds", {})
            
            # Mercado Match Winner para tênis (13_1)
            match_winner = odds_data.get("13_1", [])
            if not match_winner:
                return None
                
            # Pega as odds mais recentes
            latest_odds = match_winner[-1]
            
            try:
                home_od = float(latest_odds.get("home_od", 0))
                away_od = float(latest_odds.get("away_od", 0))
                
                if home_od <= 1.0 or away_od <= 1.0:
                    return None
                    
                return OddsData(
                    home_od=home_od,
                    away_od=away_od,
                    timestamp=latest_odds.get("add_time", "")
                )
                
            except (ValueError, TypeError):
                return None
                
        except Exception as e:
            logger.warning(f"Erro ao buscar odds do evento {event_id}: {e}")
            return None
    
    def normalize_probabilities(self, home_od: float, away_od: float) -> Tuple[float, float]:
        """Remove a margem da casa e normaliza as probabilidades"""
        inv_sum = (1.0 / home_od) + (1.0 / away_od)
        p_home = (1.0 / home_od) / inv_sum
        p_away = (1.0 / away_od) / inv_sum
        return p_home, p_away
    
    def calculate_model_probability(self, match: MatchEvent, odds_data: OddsData = None) -> float:
        """
        Usa o modelo sofisticado para estimar probabilidade do jogador da casa ganhar
        Agora integrado com odds do mercado para melhor calibração
        """
        try:
            # Detecta nível do torneio
            tournament_level = self._detect_tournament_level(match.league)
            
            # Usa o modelo sofisticado com odds quando disponível
            if odds_data and odds_data.home_od > 1.0 and odds_data.away_od > 1.0:
                probability = self.tennis_model.calculate_probability(
                    home_player=match.home,
                    away_player=match.away,
                    surface=match.surface,
                    tournament_level=tournament_level,
                    home_odds=odds_data.home_od,
                    away_odds=odds_data.away_od
                )
            else:
                # Fallback para método tradicional
                probability = self.tennis_model.calculate_probability(
                    home_player=match.home,
                    away_player=match.away,
                    surface=match.surface,
                    tournament_level=tournament_level
                )
            
            logger.debug(f"Modelo calculou {probability:.1%} para {match.home} vs {match.away} ({match.surface})")
            return probability
            
        except Exception as e:
            logger.warning(f"Erro no modelo sofisticado, usando fallback: {e}")
            return self._fallback_probability(match)
    
    def _detect_tournament_level(self, league_name: str) -> str:
        """Detecta o nível do torneio baseado no nome"""
        league_lower = league_name.lower()
        
        if any(term in league_lower for term in ["grand slam", "us open", "french open", "wimbledon", "australian open"]):
            return "grand_slam"
        elif any(term in league_lower for term in ["masters", "atp 1000", "wta 1000"]):
            return "masters"
        elif any(term in league_lower for term in ["atp 500", "wta 500"]):
            return "500_series"
        elif any(term in league_lower for term in ["atp 250", "wta 250"]):
            return "250_series"
        elif "challenger" in league_lower:
            return "challenger"
        elif "itf" in league_lower:
            return "itf"
        else:
            return "regular"
    
    def _fallback_probability(self, match: MatchEvent) -> float:
        """
        Modelo de fallback simples caso o modelo sofisticado falhe
        """
        base_prob = 0.50
        
        # Ajuste básico por superfície baseado em heurísticas
        surface_adjustment = 0.0
        if match.surface == "clay" and "nadal" in match.home.lower():
            surface_adjustment = 0.15  # Nadal favorito no clay
        elif match.surface == "clay" and "nadal" in match.away.lower():
            surface_adjustment = -0.15  # Oponente desfavorito contra Nadal no clay
        
        # Ajuste por ranking aproximado (baseado em nomes conhecidos)
        ranking_adjustment = self._estimate_ranking_difference(match.home, match.away)
        
        p_home = base_prob + surface_adjustment + ranking_adjustment
        
        return max(0.05, min(0.95, p_home))
    
    def _estimate_ranking_difference(self, home: str, away: str) -> float:
        """Estimativa grosseira de diferença de ranking baseada em nomes conhecidos"""
        # Lista de jogadores top com ajustes aproximados
        top_players = {
            "djokovic": 0.15,
            "alcaraz": 0.12,
            "medvedev": 0.10,
            "sinner": 0.08,
            "tsitsipas": 0.06,
            "rublev": 0.05,
            "fritz": 0.03,
            "nadal": 0.05,  # Reduzido por idade/lesões
            "federer": 0.02  # Aposentado praticamente
        }
        
        home_bonus = 0.0
        away_bonus = 0.0
        
        home_lower = home.lower()
        away_lower = away.lower()
        
        for player, bonus in top_players.items():
            if player in home_lower:
                home_bonus = bonus
            if player in away_lower:
                away_bonus = bonus
        
        return home_bonus - away_bonus
    
    def calculate_ev(self, odds: float, p_model: float) -> float:
        """Calcula o valor esperado de uma aposta"""
        return p_model * (odds - 1.0) - (1.0 - p_model)
    
    def _assess_opportunity_confidence(self, match: MatchEvent) -> float:
        """Avalia a confiança geral na oportunidade baseada nos dados dos jogadores"""
        try:
            # Busca dados dos jogadores
            player1 = self.tennis_model.player_db.get_or_create_player(
                match.home, 
                use_real_data=self.tennis_model.use_real_data,
                real_data_provider=self.tennis_model.real_data_provider
            )
            player2 = self.tennis_model.player_db.get_or_create_player(
                match.away,
                use_real_data=self.tennis_model.use_real_data, 
                real_data_provider=self.tennis_model.real_data_provider
            )
            
            # Usa o método do modelo para avaliar confidence
            return self.tennis_model._assess_data_confidence(player1, player2)
            
        except Exception as e:
            logger.warning(f"Erro ao avaliar confidence: {e}")
            return 0.0
    
    def _should_bet_simple_aggressive(self, ev: float, odds: float) -> bool:
        """
        Lógica AGRESSIVA simplificada: apenas EV + odds
        Sem dependência de ranking, form ou confidence
        
        Critérios:
        - Odds: 1.70 - 3.00
        - EV: 3% - 25%
        """
        # Filtro 1: Range de odds
        if odds < 1.70 or odds > 3.00:
            logger.info(f"Odds {odds:.2f} fora do range 1.70-3.00 - rejeitando")
            return False
        
        # Filtro 2: Range de EV  
        if ev < 0.03 or ev > 0.25:
            logger.info(f"EV {ev:.3f} fora do range 3%-25% - rejeitando")
            return False
        
        logger.info(f"✅ Aposta APROVADA (versão agressiva): EV {ev:.3f}, Odds {odds:.2f}")
        return True
    
    def scan_opportunities(self, 
                          hours_ahead: int = 48,
                          min_ev: float = 0.02,
                          odd_min: float = 1.80,
                          odd_max: float = 2.20) -> List[Opportunity]:
        """
        Escaneia oportunidades de apostas pré-live
        """
        logger.info("Iniciando escaneamento de oportunidades pré-live...")
        
        events = self.get_upcoming_events(hours_ahead)
        opportunities = []
        
        logger.info(f"🎾 Processando {len(events)} jogos individualmente...")
        
        for i, match in enumerate(events, 1):
            try:
                logger.info(f"📊 [{i}/{len(events)}] Analisando: {match.home} vs {match.away}")
                
                # 1. Buscar odds do jogo
                logger.info(f"  🔍 Buscando odds...")
                odds_data = self.get_event_odds(match.event_id)
                if not odds_data:
                    logger.info(f"  ❌ Odds não encontradas")
                    continue
                
                logger.info(f"  💰 Odds: Home {odds_data.home_od:.2f} | Away {odds_data.away_od:.2f}")
                
                # 2. Verificar se odds estão na faixa desejada
                home_in_range = odd_min <= odds_data.home_od <= odd_max
                away_in_range = odd_min <= odds_data.away_od <= odd_max
                
                if not (home_in_range or away_in_range):
                    logger.info(f"  ⏭️ Odds fora da faixa [{odd_min}-{odd_max}]")
                    continue
                
                # 3. Calcular probabilidades do mercado
                logger.info(f"  📈 Calculando probabilidades...")
                p_home_market, p_away_market = self.normalize_probabilities(
                    odds_data.home_od, odds_data.away_od
                )
                
                # 4. Calcular probabilidade do modelo (agora com odds para calibração)
                logger.info(f"  🧠 Calculando probabilidade do modelo...")
                p_home_model = self.calculate_model_probability(match, odds_data)
                p_away_model = 1.0 - p_home_model
                
                logger.info(f"  📊 Probabilidades - Modelo: {p_home_model:.3f} | Mercado: {p_home_market:.3f}")
                
                # 5. Avaliar confiança nos dados dos jogadores
                logger.info(f"  🔍 Avaliando confiança dos dados...")
                confidence = self._assess_opportunity_confidence(match)
                logger.info(f"  📈 Confidence score: {confidence:.2f}")
                
                # 6. Verificar oportunidades com filtros baseados em confidence
                candidates = []
                
                # Verifica lado HOME
                if home_in_range:
                    ev_home = self.calculate_ev(odds_data.home_od, p_home_model)
                    logger.info(f"  🏠 HOME EV: {ev_home:.3f}")
                    
                    # Aplica lógica simples agressiva (apenas EV + odds)
                    if self._should_bet_simple_aggressive(ev_home, odds_data.home_od):
                        candidates.append({
                            "side": "HOME",
                            "ev": ev_home,
                            "odd": odds_data.home_od,
                            "p_model": p_home_model,
                            "p_market": p_home_market,
                            "confidence": confidence
                        })
                        logger.info(f"  ✅ OPORTUNIDADE HOME encontrada! EV: {ev_home:.3f}, Odds: {odds_data.home_od:.2f}")
                    else:
                        logger.info(f"  ❌ HOME rejeitada por filtro simples agressivo")
                
                # Verifica lado AWAY  
                if away_in_range:
                    ev_away = self.calculate_ev(odds_data.away_od, p_away_model)
                    logger.info(f"  ✈️ AWAY EV: {ev_away:.3f}")
                    
                    # Aplica lógica simples agressiva (apenas EV + odds)
                    if self._should_bet_simple_aggressive(ev_away, odds_data.away_od):
                        candidates.append({
                            "side": "AWAY", 
                            "ev": ev_away,
                            "odd": odds_data.away_od,
                            "p_model": p_away_model,
                            "p_market": p_away_market,
                            "confidence": confidence
                        })
                        logger.info(f"  ✅ OPORTUNIDADE AWAY encontrada! EV: {ev_away:.3f}, Odds: {odds_data.away_od:.2f}")
                    else:
                        logger.info(f"  ❌ AWAY rejeitada por filtro simples agressivo")
                
                # 6. Adicionar oportunidades encontradas
                for candidate in candidates:
                    confidence_level = self._calculate_confidence_level(candidate["ev"], candidate["p_model"])
                    
                    opportunity = Opportunity(
                        event_id=match.event_id,
                        match=f"{match.home} vs {match.away}",
                        start_utc=match.start_utc.isoformat() + "Z",
                        league=match.league,
                        side=candidate["side"],
                        odd=round(candidate["odd"], 3),
                        p_model=round(candidate["p_model"], 3),
                        ev=round(candidate["ev"], 3),
                        p_market=round(candidate["p_market"], 3),
                        confidence=confidence_level
                    )
                    opportunities.append(opportunity)
                    logger.info(f"  💎 Oportunidade adicionada: {candidate['side']} EV: {candidate['ev']:.3f}")
                
                if not candidates:
                    logger.info(f"  📭 Nenhuma oportunidade encontrada")
                    
            except Exception as e:
                logger.error(f"  ❌ Erro processando jogo {match.home} vs {match.away}: {e}")
                continue
        
        # Ordena por EV decrescente
        opportunities.sort(key=lambda x: x.ev, reverse=True)
        
        logger.info(f"🎯 SCAN CONCLUÍDO: {len(opportunities)} oportunidades encontradas")
        return opportunities
    
    def _detect_surface(self, league_name: str) -> str:
        """Detecta o tipo de superfície baseado no nome do torneio"""
        league_lower = league_name.lower()
        
        if any(term in league_lower for term in ["clay", "terre", "roland", "french"]):
            return "clay"
        elif any(term in league_lower for term in ["grass", "wimbledon"]):
            return "grass"
        elif any(term in league_lower for term in ["indoor", "masters", "atp finals"]):
            return "indoor"
        else:
            return "hard"  # padrão
    def _calculate_confidence_level(self, ev: float, p_model: float) -> str:
        """Calcula nível de confiança na oportunidade"""
        if ev >= 0.05 and 0.3 <= p_model <= 0.7:
            return "ALTA"
        elif ev >= 0.03:
            return "MÉDIA"
        else:
            return "BAIXA"
    
    def analyze_match_factors(self, home_player: str, away_player: str, surface: str = "hard") -> Dict:
        """Analisa fatores detalhados de um confronto específico"""
        return self.tennis_model.simulate_match_probabilities(home_player, away_player, surface)
    
    def update_player_database(self):
        """Atualiza banco de dados de jogadores"""
        try:
            # TODO: Implementar atualização via APIs de rankings
            self.tennis_model.update_player_stats_from_rankings()
            logger.info("Banco de dados de jogadores atualizado")
        except Exception as e:
            logger.warning(f"Erro ao atualizar banco de jogadores: {e}")
    
    def get_model_statistics(self) -> Dict:
        """Retorna estatísticas do modelo"""
        return {
            "model_type": "sophisticated",
            "factors": list(self.tennis_model.weights.keys()),
            "weights": self.tennis_model.weights,
            "players_in_db": "TODO: implementar contagem"
        }

def main():
    """Função principal para testes"""
    # Configuração (substitua pela sua config real)
    with open("config/config.json", "r") as f:
        config = json.load(f)
    
    scanner = PreLiveScanner(
        api_token=config["api_key"],
        api_base=config["api_base_url"]
    )
    
    # Escaneia oportunidades
    opportunities = scanner.scan_opportunities(
        hours_ahead=72,
        min_ev=0.02,
        odd_min=1.80,
        odd_max=2.20
    )
    
    # Mostra resultados
    print(f"\n=== TOP 10 OPORTUNIDADES PRÉ-LIVE ===")
    for i, opp in enumerate(opportunities[:10], 1):
        print(f"{i}. {opp.match}")
        print(f"   Liga: {opp.league}")
        print(f"   Lado: {opp.side} | Odd: {opp.odd}")
        print(f"   P(Modelo): {opp.p_model:.1%} | P(Mercado): {opp.p_market:.1%}")
        print(f"   EV: {opp.ev:.1%} | Confiança: {opp.confidence}")
        print(f"   Início: {opp.start_utc}")
        print()

if __name__ == "__main__":
    main()
