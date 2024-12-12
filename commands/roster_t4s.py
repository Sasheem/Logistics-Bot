# commands/roster_position.py

from interactions import CommandContext
from rapidfuzz import process, fuzz
from config.google_sheets import client_gs
from config.constants import WAR_SHEET_ID
from utils.fetch_data_with_cache import fetch_data_with_cache

async def roster_t4s(ctx: CommandContext, name: str):
    await ctx.defer()  # Defer the interaction to give more time
    spreadsheet_id = WAR_SHEET_ID
    sheet_names = ['WHSKY', 'TANGO', 'FXTRT']
    t3_name = str(name).strip()  # Convert to string and remove leading and trailing spaces

    t3_found = False
    t4s = []

    for sheet_name in sheet_names:
        data = fetch_data_with_cache(client_gs, spreadsheet_id, sheet_name)
        soft_matches = process.extract(t3_name, [str(entry[f'Name {sheet_name}']) for entry in data], scorer=fuzz.token_sort_ratio)
        best_match = soft_matches[0] if soft_matches else None
        if best_match and best_match[1] > 70:
            t3_index = next((i for i, entry in enumerate(data) if entry[f'Name {sheet_name}'] == best_match[0]), None)
            if t3_index is not None:
                t3_found = True
                t4s = [data[i][f'Name {sheet_name}'] for i in range(t3_index + 1, t3_index + 6)]
                break

    if t3_found:
        response = f"**T4s for {t3_name}:**\n" + "\n".join(t4s)
        await ctx.send(response)
    else:
        await ctx.send(f"## Oops, this is embarrassing..\n\nT3 player not found: **{t3_name}**.\nPlease check the spelling and try again.")