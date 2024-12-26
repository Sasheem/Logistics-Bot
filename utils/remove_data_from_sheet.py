# utils/remove_data_from_sheet.py
from config.google_sheets import client_gs
import gspread.utils  # Import the gspread.utils module

# Utility function to remove data from a sheet
def remove_data_from_sheet(sheet_id, tab_name, column_index, name):
    sheet = client_gs.open_by_key(sheet_id).worksheet(tab_name)
    data = sheet.col_values(column_index)[1:]  # Get all values in the column except the header
    print(f"Original data: {data}")  # Debug statement
    updated_data = [entry for entry in data if entry.lower() != name.lower()]
    print(f"Updated data: {updated_data}")  # Debug statement
    cell_list = sheet.range(f"{gspread.utils.rowcol_to_a1(2, column_index)}:{gspread.utils.rowcol_to_a1(len(data) + 1, column_index)}")
    for i, cell in enumerate(cell_list):
        cell.value = updated_data[i] if i < len(updated_data) else ""
    sheet.update_cells(cell_list)
    print("Data updated in sheet")  # Debug statement
