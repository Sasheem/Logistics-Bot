# utils/restore_roster_notes.py

from config.google_sheets import client_gs
from config.constants import ROSTER_SHEET_ID

async def restore_roster_notes():
    # Open the Google Sheet
    sheet = client_gs.open_by_key(ROSTER_SHEET_ID)
    roster_notes = sheet.worksheet("roster_notes")
    backup_sheet = sheet.worksheet("roster_notes_backup")

    # Get all records from the backup sheet
    backup_notes = backup_sheet.get_all_values()

    # Clear the roster_notes sheet and append the backup notes
    roster_notes.clear()
    roster_notes.append_rows(backup_notes)