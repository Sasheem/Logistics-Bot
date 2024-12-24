# commands/list_name_changes.py

from interactions import CommandContext, Embed
from config.google_sheets import client_gs
from config.constants import WAR_SHEET_ID
from utils.fetch_data_with_cache import fetch_data_with_cache

async def list_name_changes(ctx: CommandContext, clear_cache: bool = False):
    await ctx.defer()  # Acknowledge the interaction to avoid "Unknown Interaction" error
    name_changes_list = fetch_data_with_cache(client_gs, WAR_SHEET_ID, "recent_name_changes", use_cache=not clear_cache)
    if name_changes_list:
        title = "Recent Name Changes"
        icon = "📖"  # Open book emoji
        color = 0x800080  # Purple color

        header = "{:<18} {:<18}\n".format("Old Name", "New Name")
        separator = "=" * 34 + "\n"
        formatted_info = header + separator

        for entry in name_changes_list:
            date = entry['Date']
            old_name = entry['Old Name']
            new_name = entry['New Name']
            entry_info = f"{date}\n{old_name:<18} {new_name:<18}\n" + "-" * 30 + "\n"
            formatted_info += entry_info

        # Split the formatted_info into chunks if it exceeds the Discord limit
        chunks = [formatted_info[i:i + 4000] for i in range(0, len(formatted_info), 4000)]

        embeds = []
        for chunk in chunks:
            embed = Embed(
                title=f"{title} {icon}",
                description=f"```\n{chunk}```",
                color=color
            )
            embeds.append(embed)

        for embed in embeds:
            await ctx.send(embeds=[embed])
    else:
        await ctx.send("No recent name changes found.")