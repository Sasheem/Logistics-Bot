# utils/clear_backup_roster_notes.py

from config.google_sheets import client_gs
from config.constants import ROSTER_SHEET_ID

async def clear_backup_roster_notes():
    # Open the Google Sheet
    sheet = client_gs.open_by_key(ROSTER_SHEET_ID)
    backup_sheet = sheet.worksheet("roster_notes_backup")

    # Clear the backup sheet
    backup_sheet.clear()
    print("Backup cleared successfully.")
