# utils/fetch_column_data.py
from config.google_sheets import client_gs

# Utility function to fetch column data
def fetch_column_data(spreadsheet_id, sheet_name, column_index):
    sheet = client_gs.open_by_key(spreadsheet_id).worksheet(sheet_name)
    column_data = sheet.col_values(column_index)
    return column_data[1:]  # Exclude the header