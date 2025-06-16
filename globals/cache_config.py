# globals/cache_config.py

# Global cache
cache = {
    "data": {},
    "timestamp": 0
}

def is_cache_empty():
    return not cache["data"]

CACHE_DURATION = 300  # Cache duration in seconds (e.g., 5 minutes)