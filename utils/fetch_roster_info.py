# utils/fetch_roster_info.py
from utils.fetch_data_from_sheet import fetch_data_from_sheet
from utils.clear_all_cache import clear_all_cache
from utils.find_player import find_player

# Function to get roster information for a player from multiple sheets
def fetch_roster_info(client_gs, spreadsheet_id, player_name, use_cache=True):
    sheet_names = ['FIRE', 'ICE', 'STEAM']  # List of sheet names

    if not use_cache:
        clear_all_cache()  # Clear all cached data before fetching fresh sheets

    for sheet_name in sheet_names:
        data = fetch_data_from_sheet(client_gs, spreadsheet_id, sheet_name)

        roster_info = find_player(data, str(player_name), sheet_name)
        if roster_info:
            return roster_info  # Return the roster info if the player is found

    return {"Team": None, "T1": None, "T2": None, "T3": None, "T4": None}  # Return default if no match is found