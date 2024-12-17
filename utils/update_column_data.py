# utils/update_column_data.py
from config.google_sheets import client_gs
import gspread.utils  # Import the gspread.utils module

# Utility function to update column data
def update_column_data(sheet_id, tab_name, column_index, data):
    sheet = client_gs.open_by_key(sheet_id).worksheet(tab_name)
    cell_list = sheet.range(f"{gspread.utils.rowcol_to_a1(2, column_index)}:{gspread.utils.rowcol_to_a1(len(data) + 1, column_index)}")
    for i, cell in enumerate(cell_list):
        cell.value = data[i]
    sheet.update_cells(cell_list)