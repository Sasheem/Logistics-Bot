
# utils/fetch_data-with_cache.py
import time

# Global cache
cache = {
    "data": {},
    "timestamp": 0
}

CACHE_DURATION = 300  # Cache duration in seconds (e.g., 5 minutes)

def fetch_data_with_cache(client_gs, spreadsheet_id, sheet_name):
    current_time = time.time()
    if sheet_name not in cache["data"] or (current_time - cache["timestamp"]) > CACHE_DURATION:
        # Fetch new data from the API
        sheet = client_gs.open_by_key(spreadsheet_id).worksheet(sheet_name)
        cache["data"][sheet_name] = sheet.get_all_records()
        cache["timestamp"] = current_time
    return cache["data"][sheet_name]