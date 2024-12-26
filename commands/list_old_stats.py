# commands/list_old_stats.py

from interactions import CommandContext, Embed
from config.google_sheets import client_gs
from config.constants import WAR_SHEET_ID
from utils.fetch_data_with_cache import fetch_data_with_cache
from datetime import datetime, timedelta

async def list_old_stats(ctx: CommandContext, months: int, tier: str = None):
    await ctx.defer()  # Acknowledge the interaction to avoid "Unknown Interaction" error
    old_stats_list = fetch_data_with_cache(client_gs, WAR_SHEET_ID, "old_stats")
    active_alts_list = fetch_data_with_cache(client_gs, WAR_SHEET_ID, "active_alts")

    if old_stats_list:
        title = "Old Stats"
        icon = "🪦"  # Tombstone emoji
        color = 0x8B4513  # Brown color

        header = "{:<18} {:<6} {:<6}\n".format("Name", "Tier", "Troop")
        separator = "=" * 34 + "\n"
        formatted_info = header + separator

        cutoff_date = datetime.now() - timedelta(days=months * 30)
        active_alts_names = [entry['Name'].lower() for entry in active_alts_list]

        for entry in old_stats_list:
            date_str = entry['Date']
            date = datetime.strptime(date_str, "%Y-%m-%d")
            if date < cutoff_date:
                name = entry['Name']
                entry_tier = entry['Tier']
                troop = entry['Troop']

                if name.lower() not in active_alts_names and troop not in ["RCA", "Alt"] and (tier is None or entry_tier == tier):
                    entry_info = f"{date_str:<10} \n{name:<18} {entry_tier:<6} {troop:<6}\n" + "-" * 34 + "\n"
                    formatted_info += entry_info

        # Split the formatted_info into chunks if it exceeds the Discord limit
        chunks = [formatted_info[i:i + 4000] for i in range(0, len(formatted_info), 4000)]

        embeds = []
        for chunk in chunks:
            embed = Embed(
                title=f"{title} {icon}",
                description=f"Stats older than {months} months\n\n```\n{chunk}```",
                color=color
            )
            embeds.append(embed)

        for embed in embeds:
            await ctx.send(embeds=[embed])
    else:
        await ctx.send("No old stats found.")
