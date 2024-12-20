# utils/fetch_player_info.py
from utils.fetch_data_with_cache import fetch_data_with_cache

# Function to get player stats info based on stats type
def fetch_player_info(client_gs, spreadsheet_id, tab_name, player_name, use_cache=True):
    data = fetch_data_with_cache(client_gs, spreadsheet_id, tab_name, use_cache=use_cache)
    player_name = player_name.strip()  # Remove leading and trailing spaces

    for row in data:
        if isinstance(row['Player Name'], str) and row['Player Name'].strip().lower() == player_name.lower():  # Case-insensitive comparison
            return row
    return None