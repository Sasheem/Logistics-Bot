from interactions import CommandContext
from rapidfuzz import process, fuzz
from config.google_sheets import client_gs
from config.constants import ROSTER_SHEET_ID
from utils.fetch_data_with_cache import fetch_data_with_cache
from utils.string_utils import normalize_string

async def keep_logistics(ctx: CommandContext, name: str, clear_cache: bool = False):
    await ctx.defer()  # Acknowledge the interaction to avoid "Unknown Interaction" error
    keeps_list = fetch_data_with_cache(client_gs, ROSTER_SHEET_ID, "bot_keep_logistics", use_cache=not clear_cache)

    # Normalize the input name
    normalized_name = normalize_string(name)

    # Search by keep name
    entries = [record for record in keeps_list if normalize_string(record['Main Keep Name']) == normalized_name]

    # Soft match if no exact match found
    if not entries:
        names = [normalize_string(record['Main Keep Name']) for record in keeps_list if isinstance(record['Main Keep Name'], str)]
        soft_matches = process.extract(normalized_name, names, scorer=fuzz.ratio)
        best_match = soft_matches[0] if soft_matches else None
        if best_match and best_match[1] > 80:  # Threshold for a good match
            original_name = next(record['Main Keep Name'] for record in keeps_list if normalize_string(record['Main Keep Name']) == best_match[0])
            entries = [record for record in keeps_list if record['Main Keep Name'] == original_name]

    # If no entries found by keep name, search by discord name
    if not entries:
        names = [normalize_string(record['Discord Name']) for record in keeps_list if isinstance(record['Discord Name'], str)]
        soft_matches = process.extract(normalized_name, names, scorer=fuzz.ratio)
        best_match = soft_matches[0] if soft_matches else None
        if best_match and best_match[1] > 80:  # Threshold for a good match
            original_name = next(record['Discord Name'] for record in keeps_list if normalize_string(record['Discord Name']) == best_match[0])
            entries = [record for record in keeps_list if record['Discord Name'] == original_name]

    if entries:
        for i, entry in enumerate(entries, start=1):
            title = f"Keep Logistics Entry {i}"
            subtitle = f"Discord Name: {entry['Discord Name']}\nDate: {entry['Date']}"
            divider = "--" * 10  # Section divider
            details = (
                f"**Main Keep Name**: \n{entry['Main Keep Name']}\n\n"
                f"**Main Keep Access**: \n{entry['Main Keep Access']}\n\n"
                f"**Secondary Keep Names**: \n{entry['Secondary Keep Names']}\n\n"
                f"**Alt Keep Names**: \n{entry['Alt Keep Names']}\n\n"
                f"**Additional Details**: \n{entry['Additional Details']}\n\n"
            )
            message = f"# {title}\n{subtitle}\n{divider}\n{details}"
            await ctx.send(message)
    else:
        await ctx.send(f"**Oops, this is embarrassing..**\n\nNo entries found for: **{name}**.\nPlease check the spelling and try again.")