# commands/list_ranks_dragon.py

from interactions import CommandContext, Embed
from config.google_sheets import client_gs
from config.constants import WAR_SHEET_ID
from utils.fetch_data_with_cache import fetch_data_with_cache
from utils.last_updated import last_updated

async def list_ranks_dragon(ctx: CommandContext, type: str, limit: str, clear_cache: bool = False):
    await ctx.defer()  # Acknowledge the interaction to avoid "Unknown Interaction" error
    rank_types = {
        "dragon-attack": "dragon_attack_rank",
        "dragon-defense": "dragon_defense_rank",
    }
    rank_type = rank_types.get(type)
    players_info = fetch_data_with_cache(client_gs, WAR_SHEET_ID, rank_type, use_cache=not clear_cache)
    if players_info:
        if limit != "all":
            limit = int(limit)
            players_info = players_info[:limit]
        title = f"{type.replace('-', ' ').title()} Ranks"
        subtitle = f"**Showing top {limit} players**" if limit != "all" else ""

        # Determine the emoji and color based on the type
        if type == "dragon-attack":
            icon = "⚔️ 🐉"  # Sword and dragon emoji
            color = 0xFF0000  # Red color
        elif type == "dragon-defense":
            icon = "🛡️ 🐉"  # Shield and dragon emoji
            color = 0x0000FF  # Blue color
        else:
            icon = ""
            color = 0xFFFFFF  # White color

        header = "{:<18} {:<10} {:<12}\n".format(
            "Player Name", "Score", "Rank"
        )
        separator = "=" * 32 + "\n"
        formatted_info = header + separator

        for player in players_info:
            player_info = "{:<18} {:<10} {:<12}\n".format(
                player["Player Name"], player["Score"], player["Rank"]
            )
            formatted_info += player_info

        # Split the formatted_info into chunks if it exceeds the Discord limit
        chunks = [formatted_info[i:i + 4000] for i in range(0, len(formatted_info), 4000)]

        embeds = []
        for chunk in chunks:
            embed = Embed(
                title=f"{title} {icon}",
                description=f"{subtitle}\n```\n{chunk}```\n\nLast Updated: **{last_updated()}**",
                color=color
            )
            embeds.append(embed)

        for embed in embeds:
            await ctx.send(embeds=[embed])
    else:
        await ctx.send("No player data found.")