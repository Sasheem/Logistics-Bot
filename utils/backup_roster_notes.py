# utils/backup_roster_notes.py

from config.google_sheets import client_gs
from config.constants import ROSTER_SHEET_ID

async def backup_roster_notes():
    # Open the Google Sheet
    sheet = client_gs.open_by_key(ROSTER_SHEET_ID)
    roster_notes = sheet.worksheet("roster_notes")
    backup_sheet = sheet.worksheet("roster_notes_backup")

    # Get all records from the roster_notes sheet
    notes = roster_notes.get_all_values()

    # Clear the backup sheet and append the notes
    backup_sheet.clear()
    backup_sheet.append_rows(notes)
