# utils/clear_cache.py
from globals.cache_config import cache

def clear_all_cache():
    cache["data"].clear()  # Clears all stored sheet data
    cache["timestamp"] = 0  # Reset timestamp to ensure fresh data on next fetch