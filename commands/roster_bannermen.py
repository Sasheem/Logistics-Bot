from interactions import CommandContext
from rapidfuzz import process, fuzz
from config.google_sheets import client_gs
from config.constants import FRICE_ORG_SHEET_ID
from utils.fetch_data_from_sheet import fetch_data_from_sheet
from utils.string_utils import normalize_string
from utils.check_permissions import check_permissions
from utils.clear_all_cache import clear_all_cache

async def roster_bannermen(ctx: CommandContext, name: str, clear_cache: bool = False):
    await ctx.defer()  # Defer the interaction to give more time
    spreadsheet_id = FRICE_ORG_SHEET_ID
    sheet_names = ['FIRE', 'ICE', 'STEAM']

    if clear_cache:
        success = await check_permissions(ctx)  # Call the helper function
        if not success:  # If clear cache failed, return early
            print(f"User {ctx.author} attempted to clear cache without permission.")
            return
        clear_all_cache()

    # Normalize the input name
    normalized_name = normalize_string(name)

    position_found = False
    position_type = None
    related_positions = []

    for sheet_name in sheet_names:
        data = fetch_data_from_sheet(client_gs, spreadsheet_id, sheet_name)
        normalized_data = [normalize_string(entry[f'Name {sheet_name}']) for entry in data]
        soft_matches = process.extract(normalized_name, normalized_data, scorer=fuzz.ratio)
        best_match = soft_matches[0] if soft_matches else None
        if best_match and best_match[1] > 80:
            index = next((i for i, entry in enumerate(data) if normalize_string(entry[f'Name {sheet_name}']) == best_match[0]), None)
            if index is not None:
                # Check the position of the matched name
                position = data[index][f'Position {sheet_name}']
                if position == 'T1':
                    position_found = True
                    position_type = "T2s"
                    related_positions = [
                        data[j][f'Name {sheet_name}'] for j in range(index + 1, len(data))
                        if data[j][f'Position {sheet_name}'] == 'T2'
                    ][:5]
                elif position == 'T2':
                    position_found = True
                    position_type = "T3s"
                    related_positions = [
                        data[j][f'Name {sheet_name}'] for j in range(index + 1, len(data))
                        if data[j][f'Position {sheet_name}'] == 'T3'
                    ][:5]
                elif position == 'T3':
                    position_found = True
                    position_type = "T4s"
                    related_positions = [
                        data[j][f'Name {sheet_name}'] for j in range(index + 1, len(data))
                        if data[j][f'Position {sheet_name}'] == 'T4'
                    ][:5]
                break

    if position_found:
        response = f"**{position_type} for {name}:**\n" + "\n".join(related_positions)
        await ctx.send(response)
    else:
        await ctx.send(f"> No bannermen found for: **{name}**. \n\nPlayer not found or is not a valid position (T1, T2, or T3)\nPlease check the spelling and try again.")