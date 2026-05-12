"""
PolymarketFetcher.py
-------------
Fetches markets from the Polymarket API, filters them and saves results to a JSONL file.
"""
 
import json
import datetime
import logging
from pathlib import Path
import requests


# Configuration 
# -----------------------------------------------------------------
API_URL = "https://gamma-api.polymarket.com/markets"
OUTPUT_FILE = Path("data/gas_market_history.jsonl")
 
BLACKLIST = [
    "Grammy", "Album", "Billboard",
    "NBA", "NFL", "Soccer", "Champions League", "UFC", "UCL"
    "Rotten Tomatoes", "Divorce", "Dating", "Marriage",
    "Harvey Weinstein", "FIFA World Cup", "La Liga",
    "Bundesliga", "Premier League", "Bundesliga", "Ligue 1", "Serie A", "NHL Stanley Cup"
]
 
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


# API
# -----------------------------------------------------------------

def fetch_markets(active: bool, closed: bool, limit: int) -> list[dict]:
    """Fetch raw market data from the Polymarket API."""
    response = requests.get(
        API_URL,
        params={"active": active, "closed": closed, "limit": limit},
        timeout=10,
    )
    response.raise_for_status()
    return response.json()
 
 
def apply_blacklist(markets: list[dict]) -> list[dict]:
    """Remove markets whose question contains a blacklisted keyword."""
    return [
        m for m in markets
        if not any(kw.lower() in m.get("question", "").lower() for kw in BLACKLIST)
    ]
 


def save_markets(markets: list[dict], scores: dict[str, tuple[int, str, str]]) -> None:
    """Append relevant markets to the JSONL history file.
    Only markets whose ID appears in scores are saved.
    """
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.datetime.now().isoformat()
    saved = 0
 
    with OUTPUT_FILE.open("a", encoding="utf-8") as f:
        for m in markets:
            if m["id"] not in scores:
                continue
            prices = json.loads(m["outcomePrices"]) if isinstance(m["outcomePrices"], str) else m["outcomePrices"]

            score, reasoning, impact = scores[m["id"]]
            record = {
                "timestamp": timestamp,
                "id": m["id"],
                "question": m["question"],
                "price_yes": prices[0] if prices else "N/A",
                "liquidity": m.get("liquidity"),
                "endDate": m.get("endDateIso"),
                "relevance_score": score,
                "reasoning":reasoning,
                "impact_type": impact
            }
            f.write(json.dumps(record) + "\n")
            saved += 1
 
    logger.info("Saved %d markets to %s", saved, OUTPUT_FILE)
