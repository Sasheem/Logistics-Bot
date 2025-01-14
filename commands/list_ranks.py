# commands/list_ranks.py

from interactions import CommandContext, Embed
from config.google_sheets import client_gs
from config.constants import WAR_SHEET_ID
from utils.fetch_data_with_cache import fetch_data_with_cache
from utils.last_updated import last_updated

async def list_ranks(ctx: CommandContext, type: str, category: str, limit: int = None, clear_cache: bool = False):
    await ctx.defer()  # Acknowledge the interaction to avoid "Unknown Interaction" error

    rank_types = {
        "attack": f"team_rank_{category}",
        "defense": f"team_defense_rank_{category}",
    }
    if category == "team":
        rank_types = {
            "attack": "team_rank",
            "defense": "team_defense_rank",
        }
    rank_type = rank_types.get(type)
    players_info = fetch_data_with_cache(client_gs, WAR_SHEET_ID, rank_type, use_cache=not clear_cache)
    if players_info:
        if limit:
            players_info = players_info[:limit]
        title = f"{type.capitalize()} {category.capitalize()} Ranks"
        subtitle = f"**Showing top {limit} players**" if limit else ""

        # Determine the emoji and color based on the category
        if category == "inf":
            icon = "🗡️"  # Sword emoji
            color = 0x0000FF  # Blue color
        elif category == "range":
            icon = "🏹"  # Bow emoji
            color = 0x00FF00  # Green color
        elif category == "cav":
            icon = "🐴"  # Horse emoji
            color = 0xFF0000  # Red color
        elif category == "t12":
            icon = "👑"  # Crown emoji
            color = 0xFFD700  # Gold color (Legendary)
        elif category == "t11":
            icon = "🔥"  # Fire emoji
            color = 0xFFA500  # Orange color (Epic)
        elif category == "t10":
            icon = "😈"  # Devil face smile emoji
            color = 0x800080  # Purple color (Exquisite)
        elif category == "t9":
            icon = "💎"  # Gem emoji
            color = 0x00FFFF  # Light blue color (Fine)
        elif category == "t8":
            icon = "🍀"  # Four-leaf clover emoji
            color = 0x00FF00  # Light green color (Common)
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
                description=f"{subtitle}\n\n```\n{chunk}```\n\nLast Updated: **{last_updated()}**",
                color=color
            )
            embeds.append(embed)

        for embed in embeds:
            await ctx.send(embeds=[embed])
    else:
        await ctx.send("No player data found.")
