# commands/list_name_changes.py

from interactions import CommandContext
from config.google_sheets import client_gs
from config.constants import WAR_SHEET_ID
from utils.fetch_data_with_cache import fetch_data_with_cache

async def list_name_changes(ctx: CommandContext):
    await ctx.defer()  # Acknowledge the interaction to avoid "Unknown Interaction" error
    name_changes_list = fetch_data_with_cache(client_gs, WAR_SHEET_ID, "recent_name_changes")
    if name_changes_list:
        header = "{:<20} {:<20}\n".format("Old Name", "New Name")
        separator = "=" * 36 + "\n"
        formatted_info = "```\n" + header + separator
        messages = []
        for entry in name_changes_list:
            date = entry['Date']
            old_name = entry['Old Name']
            new_name = entry['New Name']
            entry_info = f"{date}\n{old_name:<20} {new_name:<20}\n" + "-" * 30 + "\n"
            if len(formatted_info) + len(entry_info) + 3 > 2000:  # 2000 is the Discord message limit
                formatted_info += "```"
                messages.append(formatted_info)
                formatted_info = "```\n" + entry_info
            else:
                formatted_info += entry_info
        formatted_info += "```"
        messages.append(formatted_info)
        
        for message in messages:
            await ctx.send(message)
    else:
        await ctx.send("No recent name changes found.")