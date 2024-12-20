# utils/fetch_data_with_cache.py
import time
from globals.cache_config import cache, CACHE_DURATION

def fetch_data_with_cache(client_gs, spreadsheet_id, sheet_name, use_cache=True):
    current_time = time.time()
    if not use_cache or sheet_name not in cache["data"] or (current_time - cache["timestamp"]) > CACHE_DURATION:
        # Fetch new data from the API
        sheet = client_gs.open_by_key(spreadsheet_id).worksheet(sheet_name)
        cache["data"][sheet_name] = sheet.get_all_records()
        cache["timestamp"] = current_time
    return cache["data"][sheet_name]