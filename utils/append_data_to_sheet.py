# utils/append_data_to_sheet.py
from config.google_sheets import client_gs
import gspread.utils  # Import the gspread.utils module

# Utility function to append data to a sheet
def append_data_to_sheet(sheet_id, tab_name, data):
    sheet = client_gs.open_by_key(sheet_id).worksheet(tab_name)
    # Find the next available row
    next_row = len(sheet.get_all_values()) + 1
    cell_list = sheet.range(f"{gspread.utils.rowcol_to_a1(next_row, 1)}:{gspread.utils.rowcol_to_a1(next_row + len(data) - 1, 1)}")
    for i, cell in enumerate(cell_list):
        cell.value = data[i][0]
    sheet.update_cells(cell_list)
