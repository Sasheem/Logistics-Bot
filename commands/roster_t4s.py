from interactions import CommandContext
from rapidfuzz import process, fuzz
from config.google_sheets import client_gs
from config.constants import WAR_SHEET_ID
from utils.fetch_data_with_cache import fetch_data_with_cache
from utils.string_utils import normalize_string

async def roster_t4s(ctx: CommandContext, name: str, clear_cache: bool = False):
    await ctx.defer()  # Defer the interaction to give more time
    spreadsheet_id = WAR_SHEET_ID
    sheet_names = ['WHSKY', 'TANGO', 'FXTRT']

    # Normalize the input name
    normalized_name = normalize_string(name)

    t3_found = False
    t4s = []

    for sheet_name in sheet_names:
        data = fetch_data_with_cache(client_gs, spreadsheet_id, sheet_name, use_cache=not clear_cache)
        normalized_data = [normalize_string(entry[f'Name {sheet_name}']) for entry in data]
        soft_matches = process.extract(normalized_name, normalized_data, scorer=fuzz.partial_ratio)
        best_match = soft_matches[0] if soft_matches else None
        if best_match and best_match[1] > 70:
            t3_index = next((i for i, entry in enumerate(data) if normalize_string(entry[f'Name {sheet_name}']) == best_match[0]), None)
            if t3_index is not None:
                # Check if the found player is a T3
                if data[t3_index][f'Position {sheet_name}'] == 'T3':
                    t3_found = True
                    t4s = [data[i][f'Name {sheet_name}'] for i in range(t3_index + 1, t3_index + 6)]
                break

    if t3_found:
        response = f"**T4s for {name}:**\n" + "\n".join(t4s)
        await ctx.send(response)
    else:
        await ctx.send(f"**Oops, this is embarrassing..**\n\nPlayer not found or is not a T3: **{name}**.\nPlease check the spelling and try again.")