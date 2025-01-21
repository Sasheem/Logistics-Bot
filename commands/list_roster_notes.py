# commands/list_roster_notes.py

from interactions import CommandContext, Embed
from config.google_sheets import client_gs
from config.constants import ROSTER_SHEET_ID
from datetime import datetime, timedelta

async def list_roster_notes(ctx: CommandContext, filter: str):
    await ctx.defer()  # Acknowledge the interaction to avoid "Unknown Interaction" error

    # Open the Google Sheet for reading data
    read_sheet = client_gs.open_by_key(ROSTER_SHEET_ID).worksheet("roster_notes")

    # Get the current date and calculate the date range for the current week
    current_time = datetime.now()
    est_time = current_time - timedelta(hours=5)  # Convert to EST
    start_of_week = est_time - timedelta(days=(est_time.weekday() + 3) % 7)  # Thursday
    end_of_week = start_of_week + timedelta(days=6)  # Wednesday

    # Calculate the date range based on the selected filter
    if filter == "current":
        start_date = start_of_week
        end_date = end_of_week
    elif filter == "last_week":
        start_date = start_of_week - timedelta(days=7)
        end_date = end_of_week
    elif filter == "last_2_weeks":
        start_date = start_of_week - timedelta(days=14)
        end_date = end_of_week
    elif filter == "last_month":
        start_date = start_of_week - timedelta(days=30)
        end_date = end_of_week
    else:  # "all"
        start_date = datetime.min
        end_date = datetime.max

    # Fetch the roster notes
    roster_notes = read_sheet.get_all_records()

    # Filter the notes based on the selected date range
    filtered_notes = [
        note for note in roster_notes
        if start_date <= datetime.strptime(note["Date"], '%Y-%m-%d %H:%M:%S') <= end_date
    ]

    # Format the notes
    formatted_notes = ""
    for note in filtered_notes:
        date = datetime.strptime(note["Date"], '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
        subject = note["Subject"]
        note_content = note["Note"]
        author = note["Author"]
        entry = f"{date} | {subject}\n{note_content} - {author}\n" + "-" * 32 + "\n"
        formatted_notes += entry

    # Create the Embed
    embed = Embed(
        title="Roster Notes",
        description=f"Date Range: \n{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}\n\nTotal Notes: {len(filtered_notes)}\n\n{formatted_notes}\n\nTotal Notes: {len(filtered_notes)}\n\n",
        color=0x8B008B  # Deep magenta color
    )

    # Send the Embed
    await ctx.send(embeds=[embed])