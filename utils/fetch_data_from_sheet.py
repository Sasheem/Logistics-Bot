# utils/fetch_data_from_sheet.py
import time
from globals.cache_config import cache, CACHE_DURATION

def fetch_data_from_sheet(client_gs, spreadsheet_id, sheet_name):
    current_time = time.time()
    # Only refresh data if not stored or expired
    if sheet_name not in cache["data"] or (current_time - cache["timestamp"]) > CACHE_DURATION:
        sheet = client_gs.open_by_key(spreadsheet_id).worksheet(sheet_name)
        cache["data"][sheet_name] = sheet.get_all_records()
        cache["timestamp"] = current_time
    return cache["data"][sheet_name]
