# commands/list_ranks.py

from interactions import CommandContext
from config.google_sheets import client_gs
from config.constants import WAR_SHEET_ID
from utils.fetch_data_with_cache import fetch_data_with_cache

async def list_ranks(ctx: CommandContext, type: str, category: str, limit: int = None):
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
    players_info = fetch_data_with_cache(client_gs, WAR_SHEET_ID, rank_type)
    if players_info:
        if limit:
            players_info = players_info[:limit]
        title = f"{type.capitalize()} {category.capitalize()} Ranks"
        subtitle = f"**Showing top {limit} players**" if limit else ""
        header = "{:<20} {:<10} {:<10}\n".format(
            "Player Name", "Score", "Rank"
        )
        separator = "=" * 36 + "\n"
        formatted_info = f"# {title}\n{subtitle}\n```\n" + header + separator
        messages = []
        current_message = formatted_info

        for player in players_info:
            player_info = "{:<20} {:<10} {:<10}\n".format(
                player["Player Name"], player["Score"], player["Rank"]
            )
            if len(current_message) + len(player_info) + 3 > 2000:  # +3 for closing ```
                current_message += "```"
                messages.append(current_message)
                current_message = "```\n" + header + separator + player_info
            else:
                current_message += player_info

        current_message += "```"
        messages.append(current_message)

        for message in messages:
            await ctx.send(message)
    else:
        await ctx.send("No player data found.")