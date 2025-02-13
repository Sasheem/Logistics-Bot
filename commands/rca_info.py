# commands/rca_info.py

from interactions import CommandContext
from rapidfuzz import process, fuzz
from config.google_sheets import client_gs
from config.constants import RCA_SHEET_ID
from utils.fetch_data_with_cache import fetch_data_with_cache

async def rca_info(ctx: CommandContext, name: str, clear_cache: bool = False):
    await ctx.defer()  # Acknowledge the interaction to avoid "Unknown Interaction" error
    await ctx.send("Command is down for maintenance. Please try again later.")
    # rca_list = fetch_data_with_cache(client_gs, RCA_SHEET_ID, "bot_rca_info", use_cache=not clear_cache)
    
    # # Exact match
    # entries = [record for record in rca_list if str(record['Name']).lower() == name.lower()]

    # # Soft match if no exact match found
    # if not entries:
    #     # Ensure all elements in the list are strings
    #     names = [record['Name'] for record in rca_list if isinstance(record['Name'], str)]
    #     soft_matches = process.extract(name, names, scorer=fuzz.token_sort_ratio)
    #     best_match = soft_matches[0] if soft_matches else None
    #     if best_match and best_match[1] > 70:  # Threshold for a good match
    #         entries = [record for record in rca_list if record['Name'] == best_match[0]]

    # if entries:
    #     for i, entry in enumerate(entries, start=1):
    #         title = f"RCA Info {i}: {entry['Name']}"
    #         subtitle = f"Type: {entry['Type']}\nRein Cap: {entry['Rein Cap']}\nPower Level: {entry['Power Level']}"
    #         details = (
    #             f"**Email**: \n{entry['Email']}\n\n"
    #             f"**Password**: \n{entry['Password']}\n\n"
    #             f"**Facebook Name**: \n{entry['Facebook Name']}\n\n"
    #             f"**Access**: \n{entry['Access']}\n\n"
    #             f"**Force Logs**: \n{entry['Force Logs']}\n"
    #             f"**Notes**: \n{entry['Notes']}\n"
    #         )
    #         message = f"## {title}\n{subtitle}\n{'--' * 10}\n{details}"
    #         await ctx.send(message)
    # else:
    #     await ctx.send(f"**Oops, this is embarrassing..**\n\nNo entries found for: **{name}**.\nPlease check the spelling and try again.")