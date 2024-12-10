# utils/fetch_sheet_data.py

# Fetch sheet data from Google Sheets
def fetch_sheet_data(client_gs, spreadsheet_id, tab_name):
    sheet = client_gs.open_by_key(spreadsheet_id).worksheet(tab_name);
    data = sheet.get_all_records()
    return data