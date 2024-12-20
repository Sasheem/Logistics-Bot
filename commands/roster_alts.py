# commands/list_roster_alts.py

from interactions import CommandContext
from config.google_sheets import client_gs
from config.constants import WAR_SHEET_ID
from utils.fetch_data_with_cache import fetch_data_with_cache

async def roster_alts(ctx: CommandContext, team: str, type: str, clear_cache: bool = False):
    await ctx.defer()  # Defer the interaction to give more time
    spreadsheet_id = WAR_SHEET_ID
    sheet_name = f"{team}_type"
    type_column = f"Type {team}"

    formatted_info = []

    data = fetch_data_with_cache(client_gs, spreadsheet_id, sheet_name, use_cache=not clear_cache)

    current_t1 = current_t2 = current_t3 = None

    for entry in data:
        position = entry.get('Position ' + team)
        if position == "T1":
            current_t1 = entry.get('Name ' + team, 'N/A')
            current_t2 = current_t3 = None  # Reset T2 and T3 when a new T1 is found
        elif position == "T2":
            current_t2 = entry.get('Name ' + team, 'N/A')
            current_t3 = None  # Reset T3 when a new T2 is found
        elif position == "T3":
            current_t3 = entry.get('Name ' + team, 'N/A')

        if (type == "All" and entry[type_column] in ["RCA", "Alt", "X"]) or entry[type_column] == type:
            if position == "T4":  # Check if 'T4' key exists
                roster_entry = (
                    f"Team: {team}\n"
                    f"T1: {current_t1}\n"
                    f"T2: {current_t2}\n"
                    f"T3: {current_t3}\n"
                    f"T4: **{entry.get('Name ' + team, 'N/A')}**\n\n"
                )
                formatted_info.append(roster_entry)

    # Split the message into chunks to avoid Discord limit
    chunk_size = 2000
    message_chunks = []
    current_chunk = f"# {team} Roster Alts: {type}\n\n"

    for roster_entry in formatted_info:
        if len(current_chunk) + len(roster_entry) > chunk_size:
            message_chunks.append(current_chunk)
            current_chunk = f"# {team} Roster Alts: {type}\n\n"
        current_chunk += roster_entry

    if current_chunk.strip():
        message_chunks.append(current_chunk)

    for chunk in message_chunks:
        try:
            await ctx.send(chunk)
        except Exception as e:
            print(f"Error sending response: {e}")
            await ctx.send(f"An error occurred while sending the response. Please try again.")