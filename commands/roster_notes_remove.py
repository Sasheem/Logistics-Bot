from interactions import CommandContext
from config.google_sheets import client_gs
from config.constants import ROSTER_SHEET_ID

async def roster_notes_remove(ctx: CommandContext, subject: str):
    await ctx.defer()  # Acknowledge the interaction to avoid "Unknown Interaction" error
    
    # Open the Google Sheet
    sheet = client_gs.open_by_key(ROSTER_SHEET_ID).worksheet("roster_notes")
    
    # Fetch the existing notes
    existing_notes = sheet.get_all_records()
    
    # Find the note with the matching subject (case-insensitive)
    row_to_remove = None
    removed_note = None
    for i, entry in enumerate(existing_notes):
        if entry["Subject"].lower() == subject.lower():
            row_to_remove = i + 2  # Adjust for header row
            removed_note = entry
            break
    
    if row_to_remove:
        # Remove the row
        sheet.delete_rows(row_to_remove)
        await ctx.send(f"Note removed successfully:\n**Subject:** {removed_note['Subject']}\n**Note:** {removed_note['Note']}\n**Author:** {removed_note['Author']}")
    else:
        await ctx.send(f"No note exists with the subject '{subject}'.")