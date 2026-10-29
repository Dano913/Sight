from cachetools import TTLCache

query_cache = TTLCache(
    maxsize=100,
    ttl=300
)