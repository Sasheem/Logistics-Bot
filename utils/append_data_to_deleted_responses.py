# utils/append_data_to_deleted_responses.py
from config.google_sheets import client_gs
import gspread.utils  # Import the gspread.utils module

# Utility function to append data to the "Deleted_Responses" tab
def append_data_to_deleted_responses(sheet_id, headers, data):
    sheet = client_gs.open_by_key(sheet_id).worksheet("Deleted_Responses")
    # Find the next available row
    next_row = len(sheet.get_all_values()) + 1
    cell_list = sheet.range(f"{gspread.utils.rowcol_to_a1(next_row, 1)}:{gspread.utils.rowcol_to_a1(next_row, len(headers))}")
    
    for i, cell in enumerate(cell_list):
        cell.value = data[i]
    
    sheet.update_cells(cell_list)