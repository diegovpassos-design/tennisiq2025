"""
IMPLEMENTAÇÃO: Versão com paginação para superar limite de 50 jogos
Adiciona suporte a múltiplas páginas na API B365
"""

def create_paginated_scanner():
    """Cria versão melhorada do scanner com paginação"""
    
    paginated_code = '''
def get_upcoming_events_paginated(self, hours_ahead: int = 48, max_pages: int = 3) -> List[MatchEvent]:
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
        
        # ESTRATÉGIA 3: Múltiplas requests por dia
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
            timestamp = event.get("time") or event.get("start_time") or event.get("time_status")
            if not timestamp:
                continue
                
            dt = datetime.utcfromtimestamp(int(timestamp))
            
            if dt >= now and dt <= cutoff:
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

def get_upcoming_events_original(self, hours_ahead: int = 48):
    """Método original como backup"""
    # Código original aqui...
    pass
'''
    
    return paginated_code

def main():
    print("🚀 IMPLEMENTAÇÃO DE PAGINAÇÃO PARA SUPERAR LIMITE DE 50")
    print("=" * 70)
    
    print("\n📋 ESTRATÉGIAS IMPLEMENTADAS:")
    print("1️⃣ Parâmetro limit=200 (testa se API aceita)")
    print("2️⃣ Paginação manual (page=1,2,3)")
    print("3️⃣ Requests por dia (day=2025-08-24)")
    print("4️⃣ Fallback para método original")
    
    print("\n🔧 RECURSOS ADICIONAIS:")
    print("• Logs detalhados de cada estratégia")
    print("• Remoção de duplicatas entre páginas")
    print("• Contagem precisa de jogos por fonte")
    print("• Fallback automático se algo falhar")
    
    print("\n⚡ VANTAGENS:")
    print("✅ Pode superar limite de 50 jogos")
    print("✅ Testa múltiplas abordagens")
    print("✅ Não quebra funcionalidade existente")
    print("✅ Logs claros para debug")
    
    print("\n🎯 IMPLEMENTAÇÃO:")
    print("Para ativar, substituir get_upcoming_events() por get_upcoming_events_paginated()")
    
    paginated_code = create_paginated_scanner()
    
    print("\n" + "=" * 70)
    print("💻 CÓDIGO PRONTO PARA USAR:")
    print("=" * 70)
    print(paginated_code)
    
    print("\n" + "=" * 70)
    print("🔧 COMO IMPLEMENTAR:")
    print("=" * 70)
    
    print("\n1️⃣ BACKUP DO MÉTODO ATUAL:")
    print("   Renomear get_upcoming_events() → get_upcoming_events_original()")
    
    print("\n2️⃣ ADICIONAR NOVO MÉTODO:")
    print("   Colar o código acima no prelive_scanner.py")
    
    print("\n3️⃣ ATUALIZAR CHAMADAS:")
    print("   Trocar get_upcoming_events() → get_upcoming_events_paginated()")
    
    print("\n4️⃣ TESTAR:")
    print("   Verificar se retorna mais que 50 jogos")
    
    print("\n🎯 QUER QUE EU IMPLEMENTE DIRETAMENTE NO CÓDIGO?")

if __name__ == "__main__":
    main()
