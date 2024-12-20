# commands/keep_logistics.py

from interactions import CommandContext
from rapidfuzz import process, fuzz
from config.google_sheets import client_gs
from config.constants import ROSTER_SHEET_ID
from utils.fetch_data_with_cache import fetch_data_with_cache

async def keep_logistics(ctx: CommandContext, keep_name: str = None, discord_name: str = None, clear_cache: bool = False):
    await ctx.defer()  # Acknowledge the interaction to avoid "Unknown Interaction" error
    keeps_list = fetch_data_with_cache(client_gs, ROSTER_SHEET_ID, "bot_keep_logistics", use_cache=not clear_cache)

    if keep_name and discord_name:
        await ctx.send("Please provide either a Keep name or a Discord name, not both.")
        return

    entries = []
    name_type = ""
    if keep_name:
        # Exact match
        entries = [record for record in keeps_list if str(record['Main Keep Name']).lower() == keep_name.lower()]

        # Soft match if no exact match found
        if not entries:
            # Ensure all elements in the list are strings
            names = [record['Main Keep Name'] for record in keeps_list if isinstance(record['Main Keep Name'], str)]
            soft_matches = process.extract(keep_name, names, scorer=fuzz.token_sort_ratio)
            best_match = soft_matches[0] if soft_matches else None
            if best_match and best_match[1] > 70:  # Threshold for a good match
                entries = [record for record in keeps_list if record['Main Keep Name'] == best_match[0]]
    elif discord_name:
        name_type = "discord username"
        # Exact match
        entries = [record for record in keeps_list if str(record['Discord Name']).lower() == discord_name.lower()]

        # Soft match if no exact match found
        if not entries:
            # Ensure all elements in the list are strings
            names = [record['Discord Name'] for record in keeps_list if isinstance(record['Discord Name'], str)]
            soft_matches = process.extract(discord_name, names, scorer=fuzz.token_sort_ratio)
            best_match = soft_matches[0] if soft_matches else None
            if best_match and best_match[1] > 70:  # Threshold for a good match
                entries = [record for record in keeps_list if record['Discord Name'] == best_match[0]]
    else:
        await ctx.send("Please provide either a Keep name or a Discord name.")
        return

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
        if keep_name:
            await ctx.send(f"## Oops, this is embarrassing..\n\nSearched by {name_type}.\nNo entries found for: **{keep_name}**.\nPlease check the spelling and try again.")
        else:
            await ctx.send(f"## Oops, this is embarrassing..\n\nSearched by {name_type}.\nNo entries found for: **{discord_name}**.\nPlease check the spelling and try again.")