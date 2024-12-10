# utils/fetch_roster_info.py
from utils.fetch_data_with_cache import fetch_data_with_cache

# Helper functions
def find_player(data, player_name, team_name):
    roster = {"Team": team_name, "T1": None, "T2": None, "T3": None, "T4": None}
    current_t1 = current_t2 = current_t3 = None
    player_name = str(player_name).strip()  # Convert to string and remove leading and trailing spaces

    for row in data:
        position = row[f'Position {team_name}']
        name = str(row[f'Name {team_name}']).strip()  # Convert to string and remove leading and trailing spaces
        if position == "T1":
            current_t1 = name
            current_t2 = current_t3 = None  # Reset T2 and T3 when a new T1 is found
        elif position == "T2":
            current_t2 = name
            current_t3 = None  # Reset T3 when a new T2 is found
        elif position == "T3":
            current_t3 = name
        if name.lower() == player_name.lower():  # Case-insensitive comparison
            roster["T1"] = current_t1
            roster["T2"] = current_t2
            roster["T3"] = current_t3
            roster["T4"] = name
            if position == "T1":
                roster["T2"] = roster["T3"] = roster["T4"] = None
            elif position == "T2":
                roster["T3"] = roster["T4"] = None
            elif position == "T3":
                roster["T4"] = None
            return roster  # Return immediately when the player is found

    return None  # Return None if the player is not found in this sheet

# Function to get roster information for a player from multiple sheets
def fetch_roster_info(client_gs, spreadsheet_id, player_name):
    sheet_names = ['WHSKY', 'TANGO', 'FXTRT']  # List of sheet names
    for sheet_name in sheet_names:
        data = fetch_data_with_cache(client_gs, spreadsheet_id, sheet_name)
        roster_info = find_player(data, str(player_name), sheet_name)
        if roster_info:
            return roster_info  # Return the roster info if the player is found

    return {"Team": None, "T1": None, "T2": None, "T3": None, "T4": None}  # Return empty roster if the player is not found in any sheet