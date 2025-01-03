from interactions import CommandContext
from config.google_sheets import client_gs
from config.constants import ROSTER_SHEET_ID
from datetime import datetime

async def roster_notes_add(ctx: CommandContext, subject: str, note: str, author: str):
    await ctx.defer()  # Acknowledge the interaction to avoid "Unknown Interaction" error

    # Open the Google Sheet
    sheet = client_gs.open_by_key(ROSTER_SHEET_ID).worksheet("roster_notes")
    
    # Check for duplicate subjects (case-insensitive)
    existing_notes = sheet.get_all_records()
    for entry in existing_notes:
        if entry["Subject"].lower() == subject.lower():
            await ctx.send(f"A note with the subject '{subject}' already exists. Please choose a different subject.\n\n**Note:** \n{note}\n")
            return

    # Add the new note
    current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    new_note = [current_date, subject, note, author]
    sheet.append_row(new_note)
    
    await ctx.send(f"Note added successfully:\n**Subject:** {subject}\n**Author:** {author}\n**Note:** \n{note}\n")