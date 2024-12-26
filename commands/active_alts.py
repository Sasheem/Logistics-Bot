# commands/active_alts.py

from interactions import CommandContext, Embed
from config.google_sheets import client_gs
from config.constants import WAR_SHEET_ID
from utils.fetch_data_with_cache import fetch_data_with_cache
from utils.append_data_to_sheet import append_data_to_sheet
from utils.remove_data_from_sheet import remove_data_from_sheet
from rapidfuzz import process, fuzz

async def active_alts(ctx: CommandContext, name: str, action: str):
    await ctx.defer()  # Acknowledge the interaction to avoid "Unknown Interaction" error

    # Fetch the current list of active alts
    active_alts_list = fetch_data_with_cache(client_gs, WAR_SHEET_ID, "active_alts", use_cache=False) 

    # Check for similar names using rapidfuzz, ignoring case
    existing_names = [entry['Name'].lower() for entry in active_alts_list]
    similar_name = process.extractOne(name.lower(), existing_names, scorer=fuzz.ratio, score_cutoff=80)

    if action == "Add":
        if similar_name:
            message = f"{name} already exists as {similar_name[0]}\n"
        else:
            # Append the name to the "active_alts" sheet
            append_data_to_sheet(WAR_SHEET_ID, "active_alts", [[name]])
            message = f"Successfully added: {name}\n"
    elif action == "Remove":
        if similar_name:
            # Remove the name from the "active_alts" sheet
            remove_data_from_sheet(WAR_SHEET_ID, "active_alts", 1, name)
            message = f"Successfully removed: {name}\n"
        else:
            message = f"{name} not found in the list.\n"

    # Fetch the updated list of active alts
    active_alts_list = fetch_data_with_cache(client_gs, WAR_SHEET_ID, "active_alts", use_cache=False)

    if active_alts_list:
        title = "Active Alts"
        color = 0xFFFFFF  # White color

        header = "Name\n"
        separator = "=" * 20 + "\n"
        formatted_info = header + separator

        for entry in active_alts_list:
            entry_info = f"{entry['Name']}\n" + "-" * 20 + "\n"
            formatted_info += entry_info

        # Split the formatted_info into chunks if it exceeds the Discord limit
        chunks = [formatted_info[i:i + 4000] for i in range(0, len(formatted_info), 4000)]

        total_alts = len(active_alts_list)
        description = f"Total Active Alts: {total_alts}"

        embeds = []
        for chunk in chunks:
            embed = Embed(
                title=title,
                description=f"{description}\n\n```\n{chunk}```",
                color=color
            )
            embeds.append(embed)

        await ctx.send(message)
        for embed in embeds:
            await ctx.send(embeds=[embed])
    else:
        await ctx.send("No active alts found.")