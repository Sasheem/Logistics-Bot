# commands/list_ranks_rcas.py

from interactions import CommandContext, Embed
from config.google_sheets import client_gs
from config.constants import RCA_SHEET_ID
from utils.fetch_data_with_cache import fetch_data_with_cache
from utils.last_updated import last_updated

async def list_ranks_rcas(ctx: CommandContext, limit: str, clear_cache: bool = False):
    await ctx.defer()  # Acknowledge the interaction to avoid "Unknown Interaction" error

    rca_info = fetch_data_with_cache(client_gs, RCA_SHEET_ID, "bot_rca_info", use_cache=not clear_cache)
    if rca_info:
        # Sort players by Rein Cap in descending order
        rca_info.sort(key=lambda x: convert_to_number(x["Rein Cap"]), reverse=True)

        # Calculate ranks
        for idx, player in enumerate(rca_info, start=1):
            player["Rank"] = idx

        if limit != "all":
            limit = int(limit)
            rca_info = rca_info[:limit]
        title = "RCA Ranks 🐣"
        subtitle = f"**Showing top {limit} players**" if limit != "all" else ""

        header = "{:<18} {:<10} {:<12}\n".format(
            "Player Name", "Rein Cap", "Rank"
        )
        separator = "=" * 32 + "\n"
        formatted_info = header + separator

        for player in rca_info:
            player_info = "{:<18} {:<10} {:<12}\n".format(
                player["Name"], player["Rein Cap"], player["Rank"]
            )
            formatted_info += player_info

        # Split the formatted_info into chunks if it exceeds the Discord limit
        chunks = [formatted_info[i:i + 4000] for i in range(0, len(formatted_info), 4000)]

        embeds = []
        for chunk in chunks:
            embed = Embed(
                title=f"{title}",
                description=f"{subtitle}\n\n```\n{chunk}```\n\nLast Updated: **{last_updated()}**",
                color=0xADD8E6  # Baby blue color
            )
            embeds.append(embed)

        for embed in embeds:
            await ctx.send(embeds=[embed])
    else:
        await ctx.send("No RCA data found.")

def convert_to_number(value):
    if isinstance(value, str) and value.endswith('K'):
        return int(float(value[:-1]) * 1000)
    return int(value)