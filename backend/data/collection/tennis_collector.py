#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Coletor de Dados de Tênis - BetsAPI
=====================================

Este módulo coleta dados de tênis da API BetsAPI.com usando todos os endpoints disponíveis.
Sport ID para tênis: 13

Endpoints principais:
- InPlay Events (Jogos em andamento)
- Upcoming Events (Próximos jogos)
- Ended Events (Jogos finalizados)
- Event View (Detalhes do evento)
- Event Odds (Odds do evento)
- Tennis Rankings (Rankings)
- Player Info (Informações de jogadores)
- League Info (Informações de torneios)

Autor: Sistema de Coleta TennisQ
Data: 2025-08-03
"""

import json
import requests
import pandas as pd
import time
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
from pathlib import Path


class TennisDataCollector:
    """Coletor de dados de tênis da BetsAPI."""
    
    def __init__(self, config_file: str = "tennis_api_config.json", main_config_file: str = "../../config/config.json"):
        """
        Inicializa o coletor com configurações.
        
        Args:
            config_file: Caminho para arquivo de configuração da API de tênis
            main_config_file: Caminho para arquivo de configuração principal com API key
        """
        self.config_file = config_file
        self.main_config_file = main_config_file
        self.config = self._load_config()
        self.main_config = self._load_main_config()
        
        # Usar API key do arquivo principal
        self.api_token = self.main_config.get("api_key")
        self.base_url = self.main_config.get("api_base_url", self.config["api_config"]["base_url"])
        self.sport_id = self.config["api_config"]["sport_id"]
        self.timeout = self.config["api_config"]["timeout"]
        self.rate_limit_delay = self.config["api_config"]["rate_limit_delay"]
        
        # Controle de rate limiting
        self.requests_made = 0
        self.session_start_time = datetime.now()
        self.max_requests_per_session = self.config["collection_settings"].get("max_requests_per_session", 2000)
        self.requests_per_hour_limit = self.config["api_config"]["rate_limits"]["safe_requests_per_hour"]
        
        # Configurar logging
        self._setup_logging()
        
        # Criar diretórios de dados
        self._create_data_directories()
        
        # Sessão para reutilizar conexões
        self.session = requests.Session()
        
    def _load_config(self) -> Dict:
        """Carrega configurações do arquivo JSON."""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.error(f"Arquivo de configuração {self.config_file} não encontrado")
            raise
        except json.JSONDecodeError as e:
            self.logger.error(f"Erro ao decodificar JSON: {e}")
            raise
    
    def _load_main_config(self) -> Dict:
        """Carrega configurações principais do projeto."""
        try:
            with open(self.main_config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.error(f"Arquivo de configuração principal {self.main_config_file} não encontrado")
            raise
        except json.JSONDecodeError as e:
            self.logger.error(f"Erro ao decodificar JSON do arquivo principal: {e}")
            raise
    
    def _setup_logging(self):
        """Configura sistema de logging."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('tennis_collector.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _create_data_directories(self):
        """Cria diretórios para armazenar dados."""
        data_dir = Path(self.config["data_storage"]["output_dir"])
        subdirs = ["raw", "processed", "backup", "logs"]
        
        for subdir in subdirs:
            (data_dir / subdir).mkdir(parents=True, exist_ok=True)
    
    def _check_rate_limit(self) -> bool:
        """
        Verifica se ainda podemos fazer requisições sem exceder o limite.
        
        Returns:
            True se pode fazer requisição, False caso contrário
        """
        # Verificar limite por sessão
        if self.requests_made >= self.max_requests_per_session:
            self.logger.warning(f"Limite de {self.max_requests_per_session} requisições por sessão atingido")
            return False
        
        # Verificar limite por hora
        session_duration = datetime.now() - self.session_start_time
        hours_elapsed = session_duration.total_seconds() / 3600
        
        if hours_elapsed > 0:
            requests_per_hour = self.requests_made / hours_elapsed
            if requests_per_hour >= self.requests_per_hour_limit:
                self.logger.warning(f"Rate limit aproximado: {requests_per_hour:.1f} req/h (limite: {self.requests_per_hour_limit})")
                return False
        
        return True
    
    def _make_api_request(self, endpoint: str, params: Dict[str, Any]) -> Optional[Dict]:
        """
        Faz requisição para API com tratamento de erros e rate limiting.
        
        Args:
            endpoint: Endpoint da API
            params: Parâmetros da requisição
            
        Returns:
            Dados da API ou None em caso de erro
        """
        # Verificar rate limit antes da requisição
        if not self._check_rate_limit():
            self.logger.error("Rate limit atingido. Interrompendo coleta para proteger a API key.")
            return None
        
        params["token"] = self.api_token
        url = f"{self.base_url}{endpoint}"
        
        try:
            self.logger.info(f"Fazendo requisição {self.requests_made + 1}: {url}")
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            
            # Incrementar contador de requisições
            self.requests_made += 1
            
            # Verificar se há erro na resposta da API
            if not data.get("success", True):
                self.logger.error(f"Erro da API: {data.get('error', 'Erro desconhecido')}")
                return None
                
            # Rate limiting - usar delay configurado
            time.sleep(self.rate_limit_delay)
            
            # Log de progresso do rate limit
            if self.requests_made % 50 == 0:
                session_duration = datetime.now() - self.session_start_time
                hours_elapsed = session_duration.total_seconds() / 3600
                rate = self.requests_made / hours_elapsed if hours_elapsed > 0 else 0
                self.logger.info(f"Rate limit: {self.requests_made} req feitas, {rate:.1f} req/h")
            
            return data
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Erro de requisição: {e}")
            return None
        except json.JSONDecodeError as e:
            self.logger.error(f"Erro ao decodificar resposta JSON: {e}")
            return None
    
    def collect_inplay_events(self) -> List[Dict]:
        """Coleta eventos de tênis em andamento."""
        self.logger.info("Coletando eventos em andamento...")
        
        endpoint = self.config["endpoints"]["inplay_events"]["url"]
        params = {"sport_id": self.sport_id}
        
        data = self._make_api_request(endpoint, params)
        if data and "results" in data:
            self.logger.info(f"Coletados {len(data['results'])} eventos em andamento")
            return data["results"]
        return []
    
    def collect_upcoming_events(self, days_ahead: int = None, max_pages: int = None) -> List[Dict]:
        """
        Coleta próximos eventos de tênis.
        
        Args:
            days_ahead: Dias à frente para coletar (padrão do config)
            max_pages: Máximo de páginas para coletar (padrão do config)
            
        Returns:
            Lista de eventos
        """
        if days_ahead is None:
            days_ahead = self.config["collection_settings"]["days_future"]
        if max_pages is None:
            max_pages = self.config["collection_settings"]["max_pages_per_endpoint"]
            
        self.logger.info(f"Coletando eventos futuros ({days_ahead} dias, max {max_pages} páginas)...")
        
        all_events = []
        endpoint = self.config["endpoints"]["upcoming_events"]["url"]
        
        # Coletar por dia
        for i in range(days_ahead):
            if not self._check_rate_limit():
                self.logger.warning("Rate limit atingido durante coleta de eventos futuros")
                break
                
            date = datetime.now() + timedelta(days=i)
            day_param = date.strftime("%Y%m%d")
            
            for page in range(1, max_pages + 1):
                if not self._check_rate_limit():
                    self.logger.warning("Rate limit atingido durante paginação")
                    break
                    
                params = {
                    "sport_id": self.sport_id,
                    "day": day_param,
                    "page": page
                }
                
                data = self._make_api_request(endpoint, params)
                if data and "results" in data:
                    events = data["results"]
                    all_events.extend(events)
                    
                    if len(events) == 0:  # Não há mais eventos nesta página
                        break
                else:
                    break
        
        self.logger.info(f"Coletados {len(all_events)} eventos futuros")
        return all_events
    
    def collect_ended_events(self, days_back: int = None, max_pages: int = None) -> List[Dict]:
        """
        Coleta eventos finalizados.
        
        Args:
            days_back: Dias anteriores para coletar (padrão do config)
            max_pages: Máximo de páginas para coletar (padrão do config)
            
        Returns:
            Lista de eventos finalizados
        """
        if days_back is None:
            days_back = self.config["collection_settings"]["days_history"]
        if max_pages is None:
            max_pages = self.config["collection_settings"]["max_pages_per_endpoint"]
            
        self.logger.info(f"Coletando eventos finalizados ({days_back} dias, max {max_pages} páginas)...")
        
        all_events = []
        endpoint = self.config["endpoints"]["ended_events"]["url"]
        
        # Coletar por dia
        for i in range(days_back):
            if not self._check_rate_limit():
                self.logger.warning("Rate limit atingido durante coleta de eventos finalizados")
                break
                
            date = datetime.now() - timedelta(days=i)
            day_param = date.strftime("%Y%m%d")
            
            for page in range(1, max_pages + 1):
                if not self._check_rate_limit():
                    self.logger.warning("Rate limit atingido durante paginação")
                    break
                    
                params = {
                    "sport_id": self.sport_id,
                    "day": day_param,
                    "page": page
                }
                
                data = self._make_api_request(endpoint, params)
                if data and "results" in data:
                    events = data["results"]
                    all_events.extend(events)
                    
                    if len(events) == 0:
                        break
                else:
                    break
        
        self.logger.info(f"Coletados {len(all_events)} eventos finalizados")
        return all_events
    
    def collect_event_details(self, event_ids: List[str]) -> List[Dict]:
        """
        Coleta detalhes de eventos específicos.
        
        Args:
            event_ids: Lista de IDs de eventos
            
        Returns:
            Lista de detalhes dos eventos
        """
        self.logger.info(f"Coletando detalhes de {len(event_ids)} eventos...")
        
        all_details = []
        endpoint = self.config["endpoints"]["event_view"]["url"]
        
        # Processar em lotes de 10 (limite da API)
        for i in range(0, len(event_ids), 10):
            batch = event_ids[i:i+10]
            params = {"event_id": ",".join(batch)}
            
            data = self._make_api_request(endpoint, params)
            if data and "results" in data:
                all_details.extend(data["results"])
        
        self.logger.info(f"Coletados detalhes de {len(all_details)} eventos")
        return all_details
    
    def collect_event_odds(self, event_ids: List[str], sources: List[str] = None, max_events: int = 20) -> List[Dict]:
        """
        Coleta odds dos eventos (limitado para proteger rate limit).
        
        Args:
            event_ids: Lista de IDs de eventos
            sources: Lista de fontes de odds (opcional)
            max_events: Máximo de eventos para coletar odds (padrão: 20)
            
        Returns:
            Lista de odds dos eventos
        """
        if sources is None:
            sources = ["bet365", "bwin"]  # Apenas 2 fontes principais para economizar requisições
        
        # Limitar eventos para proteger rate limit
        limited_event_ids = event_ids[:max_events]
        self.logger.info(f"Coletando odds de {len(limited_event_ids)} eventos (limitado de {len(event_ids)})")
        
        all_odds = []
        endpoint = self.config["endpoints"]["event_odds"]["url"]
        
        for event_id in limited_event_ids:
            if not self._check_rate_limit():
                self.logger.warning("Rate limit atingido durante coleta de odds")
                break
                
            for source in sources:
                if not self._check_rate_limit():
                    self.logger.warning("Rate limit atingido durante coleta de odds por fonte")
                    break
                    
                params = {
                    "event_id": event_id,
                    "source": source
                }
                
                data = self._make_api_request(endpoint, params)
                if data and "results" in data:
                    odds_data = data["results"]
                    odds_data["event_id"] = event_id
                    odds_data["source"] = source
                    all_odds.append(odds_data)
        
        self.logger.info(f"Coletadas odds de {len(all_odds)} combinações evento-fonte")
        return all_odds
    
    def collect_tennis_rankings(self) -> Dict[str, List]:
        """
        Coleta rankings de tênis.
        
        Returns:
            Dicionário com rankings por categoria
        """
        self.logger.info("Coletando rankings de tênis...")
        
        rankings = {}
        endpoint = self.config["endpoints"]["tennis_ranking"]["url"]
        
        for type_id, description in self.config["tennis_ranking_types"].items():
            params = {"type_id": int(type_id)}
            
            data = self._make_api_request(endpoint, params)
            if data and "results" in data:
                rankings[description] = data["results"]
                self.logger.info(f"Coletado ranking: {description} ({len(data['results'])} jogadores)")
        
        return rankings
    
    def collect_all_data(self) -> Dict[str, Any]:
        """
        Coleta todos os dados disponíveis.
        
        Returns:
            Dicionário com todos os dados coletados
        """
        self.logger.info("Iniciando coleta completa de dados...")
        start_time = datetime.now()
        
        collected_data = {
            "collection_timestamp": start_time.isoformat(),
            "sport_id": self.sport_id,
            "sport_name": "tennis"
        }
        
        # 1. Eventos em andamento
        if self.config["collection_settings"]["collect_inplay"]:
            collected_data["inplay_events"] = self.collect_inplay_events()
        
        # 2. Próximos eventos
        if self.config["collection_settings"]["collect_upcoming"]:
            collected_data["upcoming_events"] = self.collect_upcoming_events()
        
        # 3. Eventos finalizados
        if self.config["collection_settings"]["collect_ended"]:
            collected_data["ended_events"] = self.collect_ended_events()
        
        # 4. Coletar IDs únicos de eventos para detalhes e odds
        all_event_ids = set()
        for key in ["inplay_events", "upcoming_events", "ended_events"]:
            if key in collected_data:
                for event in collected_data[key]:
                    if "id" in event:
                        all_event_ids.add(str(event["id"]))
        
        # Limitar eventos para proteger rate limit
        max_events = self.config["collection_settings"]["max_events_per_request"]
        event_ids_list = list(all_event_ids)[:max_events]
        self.logger.info(f"Processando {len(event_ids_list)} eventos (limitado de {len(all_event_ids)})")
        
        # 5. Detalhes dos eventos (processamento em lotes menores)
        if event_ids_list and not self._check_rate_limit():
            self.logger.warning("Rate limit próximo ao limite, pulando detalhes dos eventos")
        elif event_ids_list:
            collected_data["event_details"] = self.collect_event_details(event_ids_list[:20])  # Máximo 20 eventos
            
            # 6. Odds dos eventos (apenas para eventos prioritários)
            if self.config["collection_settings"]["collect_odds"] and not self._check_rate_limit():
                collected_data["event_odds"] = self.collect_event_odds(event_ids_list[:10])  # Máximo 10 eventos
        
        # 7. Rankings de tênis
        if self.config["collection_settings"]["collect_rankings"]:
            collected_data["tennis_rankings"] = self.collect_tennis_rankings()
        
        # Estatísticas da coleta
        end_time = datetime.now()
        duration = end_time - start_time
        hours_elapsed = duration.total_seconds() / 3600
        requests_per_hour = self.requests_made / hours_elapsed if hours_elapsed > 0 else 0
        
        collected_data["collection_stats"] = {
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_seconds": duration.total_seconds(),
            "total_events_collected": len(event_ids_list) if 'event_ids_list' in locals() else 0,
            "endpoints_used": len([k for k in collected_data.keys() if k not in ["collection_timestamp", "sport_id", "sport_name", "collection_stats"]]),
            "rate_limit_stats": {
                "requests_made": self.requests_made,
                "requests_per_hour": round(requests_per_hour, 2),
                "rate_limit_percentage": round((requests_per_hour / self.requests_per_hour_limit) * 100, 1) if self.requests_per_hour_limit > 0 else 0,
                "remaining_requests": max(0, self.max_requests_per_session - self.requests_made)
            }
        }
        
        self.logger.info(f"Coleta completa finalizada em {duration.total_seconds():.2f} segundos")
        return collected_data
    
    def save_data(self, data: Dict[str, Any], filename_prefix: str = "tennis_data") -> str:
        """
        Salva dados coletados em arquivo JSON.
        
        Args:
            data: Dados para salvar
            filename_prefix: Prefixo do nome do arquivo
            
        Returns:
            Caminho do arquivo salvo
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{filename_prefix}_{timestamp}.json"
        filepath = Path(self.config["data_storage"]["output_dir"]) / "raw" / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"Dados salvos em: {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar dados: {e}")
            raise
    
    def export_to_csv(self, data: Dict[str, Any], output_dir: str = None) -> List[str]:
        """
        Exporta dados para arquivos CSV.
        
        Args:
            data: Dados para exportar
            output_dir: Diretório de saída (opcional)
            
        Returns:
            Lista de arquivos CSV criados
        """
        if output_dir is None:
            output_dir = Path(self.config["data_storage"]["output_dir"]) / "processed"
        else:
            output_dir = Path(output_dir)
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        csv_files = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Exportar cada tipo de dados para CSV separado
        for data_type, data_list in data.items():
            if isinstance(data_list, list) and data_list:
                try:
                    df = pd.json_normalize(data_list)
                    filename = f"{data_type}_{timestamp}.csv"
                    filepath = output_dir / filename
                    
                    df.to_csv(filepath, index=False, encoding='utf-8')
                    csv_files.append(str(filepath))
                    self.logger.info(f"Exportado CSV: {filepath}")
                    
                except Exception as e:
                    self.logger.error(f"Erro ao exportar {data_type} para CSV: {e}")
        
        return csv_files

    def create_endpoints_data_reference(self, output_file: str = "../dados/endpoints_data_reference.json") -> bool:
        """
        Cria um arquivo JSON com dados de exemplo de todos os endpoints para referência.
        
        Args:
            output_file: Caminho para o arquivo de saída
            
        Returns:
            bool: True se bem-sucedido
        """
        print("🔍 CRIANDO REFERÊNCIA DE DADOS DOS ENDPOINTS...")
        print("=" * 60)
        
        reference_data = {
            "tennis_api_endpoints_data": {
                "data_extraction_timestamp": datetime.now().isoformat(),
                "api_base_url": self.main_config.get('api_base_url', 'https://api.b365api.com'),
                "sport_id": 13,
                "endpoints": {}
            }
        }
        
        try:
            # 1. InPlay Events
            print("📡 Coletando dados de eventos ao vivo...")
            inplay_data = self.collect_inplay_events()
            if inplay_data and len(inplay_data) > 0:
                sample_event = inplay_data[0]
                reference_data["tennis_api_endpoints_data"]["endpoints"]["inplay_events"] = {
                    "endpoint": "/v2/events/inplay",
                    "description": "Eventos ao vivo",
                    "total_events_found": len(inplay_data),
                    "sample_data": sample_event,
                    "useful_fields": [
                        "id - ID único do evento",
                        "time - Timestamp do início",
                        "league.name - Nome do torneio",
                        "home.name - Jogador 1",
                        "away.name - Jogador 2",
                        "ss - Score atual",
                        "time_status - Status da partida"
                    ]
                }
            
            time.sleep(1.5)  # Rate limiting
            
            # 2. Upcoming Events
            print("📡 Coletando dados de próximos eventos...")
            upcoming_data = self.collect_upcoming_events()
            if upcoming_data and len(upcoming_data) > 0:
                sample_upcoming = upcoming_data[0]
                reference_data["tennis_api_endpoints_data"]["endpoints"]["upcoming_events"] = {
                    "endpoint": "/v2/events/upcoming",
                    "description": "Próximos eventos",
                    "total_events_found": len(upcoming_data),
                    "sample_data": sample_upcoming,
                    "useful_fields": [
                        "id - ID único do evento",
                        "time - Timestamp do início programado",
                        "league.name - Nome do torneio",
                        "home.name - Jogador 1",
                        "away.name - Jogador 2"
                    ]
                }
            
            time.sleep(1.5)  # Rate limiting
            
            # 3. Ended Events (últimas 24h)
            print("📡 Coletando dados de eventos finalizados...")
            ended_data = self.collect_ended_events(days_back=1)
            if ended_data and len(ended_data) > 0:
                sample_ended = ended_data[0]
                reference_data["tennis_api_endpoints_data"]["endpoints"]["ended_events"] = {
                    "endpoint": "/v2/events/ended",
                    "description": "Eventos finalizados",
                    "total_events_found": len(ended_data),
                    "sample_data": sample_ended,
                    "useful_fields": [
                        "id - ID único do evento",
                        "time - Timestamp do início",
                        "league.name - Nome do torneio",
                        "home.name - Jogador",
                        "away.name - Jogador",
                        "ss - Score final",
                        "winner - 1 para casa, 2 para visitante"
                    ]
                }
            
            time.sleep(1.5)  # Rate limiting
            
            # 4. Event Odds (se houver eventos)
            if inplay_data and len(inplay_data) > 0:
                print("📡 Coletando dados de odds...")
                event_id = inplay_data[0].get('id')
                if event_id:
                    odds_data = self.collect_event_odds([event_id], sources=['bet365'], max_events=1)
                    sample_odds = odds_data[0] if odds_data and len(odds_data) > 0 else None
                    reference_data["tennis_api_endpoints_data"]["endpoints"]["event_odds"] = {
                        "endpoint": "/v2/event/odds",
                        "description": "Odds de um evento específico",
                        "parameters": {
                            "event_id": "ID do evento",
                            "source": "bet365, bovada, pinnacle",
                            "odds_market": "13_1 (Match Winner)"
                        },
                        "sample_data": sample_odds,
                        "useful_fields": [
                            "odds.13_1.values[0].odd - Odd do jogador 1",
                            "odds.13_1.values[1].odd - Odd do jogador 2",
                            "odds.13_1.values[0].name - Nome do jogador 1",
                            "odds.13_1.values[1].name - Nome do jogador 2"
                        ],
                        "note": "Nem todos os eventos têm odds disponíveis - especialmente torneios menores (ITF, Challenger)"
                    }
            
            time.sleep(1.5)  # Rate limiting
            
            # 5. Tennis Rankings
            print("📡 Coletando dados de rankings...")
            rankings_data = self.collect_tennis_rankings()
            if rankings_data:
                reference_data["tennis_api_endpoints_data"]["endpoints"]["tennis_rankings"] = {
                    "endpoint": "/v2/tennis/rankings",
                    "description": "Rankings de tênis",
                    "sample_data": rankings_data,
                    "useful_fields": [
                        "rankings[].name - Nome do jogador",
                        "rankings[].pos - Posição no ranking",
                        "rankings[].points - Pontos no ranking"
                    ]
                }
            
            # Adicionar metadados e informações úteis
            reference_data["tennis_api_endpoints_data"]["odds_markets"] = {
                "13_1": "Match Winner (Vencedor da Partida)",
                "13_2": "Set Betting (Resultado por Sets)",
                "13_3": "Total Games (Total de Games)",
                "13_4": "Handicap Games",
                "13_5": "Set 1 Winner (Vencedor do 1º Set)",
                "13_6": "Set 2 Winner (Vencedor do 2º Set)",
                "13_7": "Set 3 Winner (Vencedor do 3º Set)"
            }
            
            reference_data["tennis_api_endpoints_data"]["time_status_codes"] = {
                "0": "Não iniciado",
                "1": "Ao vivo - 1º Set",
                "2": "Ao vivo - 2º Set", 
                "3": "Ao vivo - 3º Set",
                "4": "Ao vivo - 4º Set",
                "5": "Ao vivo - 5º Set",
                "99": "Finalizado",
                "100": "Cancelado",
                "110": "Adiado"
            }
            
            reference_data["tennis_api_endpoints_data"]["api_usage_notes"] = {
                "rate_limit": "3600 requests per hour",
                "recommended_safe_limit": "2880 requests per hour (80%)",
                "delay_between_requests": "1.5 seconds",
                "best_odds_sources": ["bet365", "pinnacle", "bovada"],
                "tournaments_with_odds": ["ATP Tour", "WTA Tour", "Grand Slams", "Masters 1000"],
                "tournaments_without_odds": ["ITF", "Challenger (alguns)", "Qualifiers"]
            }
            
            reference_data["tennis_api_endpoints_data"]["recommended_endpoints_by_use_case"] = {
                "live_monitoring": {
                    "primary": "/v2/events/inplay",
                    "secondary": "/v2/event/odds",
                    "fields": ["id", "league.name", "home.name", "away.name", "ss", "time_status"]
                },
                "betting_analysis": {
                    "primary": "/v2/event/odds", 
                    "secondary": "/v2/events/upcoming",
                    "fields": ["odds.13_1.values", "event_id", "source"]
                },
                "historical_analysis": {
                    "primary": "/v2/events/ended",
                    "secondary": "/v2/tennis/rankings", 
                    "fields": ["winner", "scores", "ss", "league.name"]
                },
                "player_research": {
                    "primary": "/v2/tennis/rankings",
                    "secondary": "/v2/team/image",
                    "fields": ["rankings[].name", "rankings[].pos", "rankings[].points", "image"]
                }
            }
            
            # Salvar arquivo
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(reference_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Arquivo de referência criado: {output_file}")
            print(f"📊 Endpoints documentados: {len(reference_data['tennis_api_endpoints_data']['endpoints'])}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao criar arquivo de referência: {e}")
            logging.error(f"Erro ao criar referência de endpoints: {e}")
            return False


def main():
    """Função principal para executar coleta de dados."""
    try:
        # Verificar se o token está configurado
        collector = TennisDataCollector()
        
        if not collector.api_token:
            print("⚠️  ATENÇÃO: API key não encontrada no arquivo config/config.json")
            print("   Verifique se o campo 'api_key' está configurado corretamente")
            return
        
        print("🎾 Iniciando coleta de dados de tênis...")
        print(f"Sport ID: {collector.sport_id}")
        print(f"Base URL: {collector.base_url}")
        print(f"API Key: {collector.api_token[:10]}...")  # Mostrar apenas os primeiros caracteres
        
        # Perguntar se deve criar arquivo de referência
        print("\n📚 Opções de execução:")
        print("1. Coletar todos os dados (padrão)")
        print("2. Criar arquivo de referência dos endpoints")
        print("3. Ambos")
        
        choice = input("\nEscolha uma opção (1-3) [padrão: 1]: ").strip()
        if not choice:
            choice = "1"
        
        if choice in ["2", "3"]:
            print("\n" + "="*60)
            collector.create_endpoints_data_reference()
            print("="*60)
        
        if choice in ["1", "3"]:
            print("\n" + "="*60)
            # Coletar todos os dados
            all_data = collector.collect_all_data()
            
            # Salvar dados em JSON
            json_file = collector.save_data(all_data)
            print(f"✅ Dados salvos em JSON: {json_file}")
            
            # Exportar para CSV
            csv_files = collector.export_to_csv(all_data)
            if csv_files:
                print(f"✅ Dados exportados para {len(csv_files)} arquivos CSV")
        
        # Mostrar estatísticas
        stats = all_data.get("collection_stats", {})
        rate_stats = stats.get("rate_limit_stats", {})
        
        print(f"📊 Estatísticas da coleta:")
        print(f"   - Duração: {stats.get('duration_seconds', 0):.2f} segundos")
        print(f"   - Eventos coletados: {stats.get('total_events_collected', 0)}")
        print(f"   - Endpoints utilizados: {stats.get('endpoints_used', 0)}")
        print(f"🔒 Rate Limit:")
        print(f"   - Requisições feitas: {rate_stats.get('requests_made', 0)}")
        print(f"   - Taxa atual: {rate_stats.get('requests_per_hour', 0)} req/h")
        print(f"   - Uso do limite: {rate_stats.get('rate_limit_percentage', 0)}%")
        print(f"   - Requisições restantes: {rate_stats.get('remaining_requests', 0)}")
        
    except Exception as e:
        print(f"❌ Erro durante a execução: {e}")
        logging.error(f"Erro na função main: {e}")


if __name__ == "__main__":
    main()
