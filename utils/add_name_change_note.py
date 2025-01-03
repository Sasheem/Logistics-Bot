# utils/add_name_change_note.py

from config.google_sheets import client_gs
from config.constants import ROSTER_SHEET_ID
from datetime import datetime

async def add_name_change_note(ctx, old_name: str, new_name: str, author: str):
    # Open the Google Sheet
    sheet = client_gs.open_by_key(ROSTER_SHEET_ID).worksheet("roster_notes")

    # Get all existing notes to determine the next unique subject number
    existing_notes = sheet.get_all_records()
    name_change_count = sum(1 for entry in existing_notes if entry["Subject"].startswith("Name Change"))

    # Generate a unique subject for the name change note
    subject = f"Name Change {name_change_count + 1}"

    # Create the note content
    note = f"Name changed from {old_name} to {new_name}"

    # Add the new note
    current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    new_note = [current_date, subject, note, author]
    sheet.append_row(new_note)

    await ctx.send(f"Name change note added successfully:\n**Subject:** {subject}\n**Author:** {author}\n**Note:** \n{note}\n")