from interactions import CommandContext, Embed
from config.google_sheets import client_gs
from config.constants import ROSTER_SHEET_ID
from datetime import datetime, timedelta

async def list_roster_notes(ctx: CommandContext):
    await ctx.defer()  # Acknowledge the interaction to avoid "Unknown Interaction" error

    # Open the Google Sheet for reading data
    read_sheet = client_gs.open_by_key(ROSTER_SHEET_ID).worksheet("Roster Notes")
    
    # Get the current date and calculate the date range for the current week
    current_time = datetime.now()
    est_time = current_time - timedelta(hours=5)  # Convert to EST
    start_of_week = est_time - timedelta(days=est_time.weekday())  # Monday
    end_of_week = start_of_week + timedelta(days=6)  # Sunday

    # Fetch the roster notes
    roster_notes = read_sheet.get_all_records()

    # Filter notes for the current week
    filtered_notes = [
        note for note in roster_notes
        if start_of_week <= datetime.strptime(note["Date"], '%Y-%m-%d') <= end_of_week
    ]

    # Format the notes
    formatted_notes = ""
    for note in filtered_notes:
        date = note["Date"]
        subject = note["Subject"]
        note_content = note["Note"]
        author = note["Author"]
        entry = f"{date} | {subject}\n{note_content} - {author}\n" + "-" * 34 + "\n"
        formatted_notes += entry

    # Create the Embed
    embed = Embed(
        title="Roster Notes",
        description=f"Date Range: \n{start_of_week.strftime('%Y-%m-%d')} to {end_of_week.strftime('%Y-%m-%d')}\n\nTotal Notes: {len(filtered_notes)}\n\n{formatted_notes}",
        color=0x8B008B  # Deep magenta color
    )

    # Send the Embed
    await ctx.send(embeds=[embed])
