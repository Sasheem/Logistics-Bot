from interactions import CommandContext
from rapidfuzz import process, fuzz
from config.google_sheets import client_gs
from config.constants import FRICE_ORG_SHEET_ID
from utils.fetch_roster_info import fetch_roster_info
from utils.fetch_data_with_cache import fetch_data_with_cache
from utils.string_utils import normalize_string
from utils.handle_clear_cache import handle_clear_cache

async def roster_position(ctx: CommandContext, name: str, clear_cache: bool = False):
    await ctx.defer()  # Defer the interaction to give more time
    spreadsheet_id = FRICE_ORG_SHEET_ID
    sheet_names = ['FIRE', 'ICE']

    # check permissions before clearing cache
    if clear_cache:
        success = await handle_clear_cache(ctx)

        if not success:
            return

    # Normalize the input name
    normalized_name = normalize_string(name)

    # Fetch data with or without cache based on clear_cache parameter
    roster_info = fetch_roster_info(client_gs, spreadsheet_id, normalized_name, use_cache=not clear_cache)

    # Soft match if no exact match found
    if not roster_info or not roster_info["T1"]:
        for sheet_name in sheet_names:
            data = fetch_data_with_cache(client_gs, spreadsheet_id, sheet_name, use_cache=not clear_cache)
            normalized_data = [normalize_string(entry[f'Name {sheet_name}']) for entry in data]
            soft_matches = process.extract(normalized_name, normalized_data, scorer=fuzz.ratio)
            best_match = soft_matches[0] if soft_matches else None
            if best_match and best_match[1] > 80:
                original_name = next(entry[f'Name {sheet_name}'] for entry in data if normalize_string(entry[f'Name {sheet_name}']) == best_match[0])
                roster_info = fetch_roster_info(client_gs, spreadsheet_id, original_name, use_cache=not clear_cache)
                break

    if roster_info and roster_info["T1"]:
        response = f"**Roster Position for {name}:**\n"
        if roster_info["Team"]:
            response += f"Team: {roster_info['Team']}\n"
        if roster_info["T1"]:
            response += f"T1: {roster_info['T1']}\n"
        if roster_info["T2"]:
            response += f"T2: {roster_info['T2']}\n"
        if roster_info["T3"]:
            response += f"T3: {roster_info['T3']}\n"
        if roster_info["T4"]:
            response += f"T4: {roster_info['T4']}\n"
        try:
            await ctx.send(response)
        except Exception as e:
            print(f"Error sending response: {e}")
            await ctx.send(f"An error occurred while sending the response for {name}. Please try again later.")
    else:
        await ctx.send(f"> Player not found: **{name}**.\n\nPlease check the spelling and try again.")