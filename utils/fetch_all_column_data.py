# utils/fetch_all_column_data.py
from config.google_sheets import client_gs

# Utility function to fetch all column data
def fetch_all_column_data(spreadsheet_id, sheet_name):
    sheet = client_gs.open_by_key(spreadsheet_id).worksheet(sheet_name)
    all_data = sheet.get_all_values()
    return all_data
