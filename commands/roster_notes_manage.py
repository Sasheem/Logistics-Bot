# commands/rosternotes_manage.py

from interactions import CommandContext
from config.google_sheets import client_gs
from config.constants import ROSTER_SHEET_ID
from utils.backup_roster_notes import backup_roster_notes
from utils.restore_roster_notes import restore_roster_notes
from utils.clear_backup_roster_notes import clear_backup_roster_notes

async def roster_notes_manage(ctx: CommandContext, clear_notes: bool = False, restore_backup: bool = False, clear_backup: bool = False):
    await ctx.defer()  # Acknowledge the interaction to avoid "Unknown Interaction" error

    # Check if more than one option is selected
    options_selected = sum([clear_notes, restore_backup, clear_backup])
    if options_selected > 1:
        await ctx.send("Please choose only one of the three options: clear_notes, restore_backup, or clear_backup.")
        return

    # Clear the backup if the option is set to true
    if clear_backup:
        await clear_backup_roster_notes()
        await ctx.send("Backup roster notes have been cleared.")
        return

    # Restore from backup if the option is set to true
    if restore_backup:
        await restore_roster_notes()
        await ctx.send("Roster notes have been restored from the backup.")
        return

    # Backup the current roster notes before clearing if the option is set to true
    if clear_notes:
        await backup_roster_notes()
        read_sheet = client_gs.open_by_key(ROSTER_SHEET_ID).worksheet("roster_notes")
        read_sheet.clear()
        await ctx.send("All roster notes have been cleared and backed up.")
        return

    await ctx.send("No action was taken. Please specify an option to manage the roster notes.")