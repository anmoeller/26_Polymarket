from PolymarketFetcher import fetch_markets, apply_blacklist, save_markets
from AiFilter import AiFilterFunction

markets = fetch_markets(active=True, closed=False, limit=20000)
markets = apply_blacklist(markets)
scores = AiFilterFunction(markets)
save_markets(markets, scores)


