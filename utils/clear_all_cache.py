# utils/clear_cache.py
from globals.cache_config import cache, is_cache_empty

def clear_all_cache() -> bool:
    if is_cache_empty():
        return False # Nothing to clear

    cache["data"].clear()  # Clears all stored sheet data
    cache["timestamp"] = 0  # Reset timestamp to ensure fresh data on next fetch
    return True # Successfully cleared