# commands/list_ranks_roster.py

from interactions import CommandContext
from config.google_sheets import client_gs
from config.constants import WAR_SHEET_ID
from utils.fetch_data_with_cache import fetch_data_with_cache

async def list_ranks_roster(ctx: CommandContext, team: str, category: str, defense_type: str = None, clear_cache: bool = False):
    await ctx.defer()  # Acknowledge the interaction to avoid "Unknown Interaction" error

    if category != "troops_defense" and defense_type:
        await ctx.send("The defense type option is only applicable for Troops Defense. Please select the correct category.")
        return

    if category == "troops_defense" and not defense_type:
        await ctx.send("Please select a defense type (Base or Glam) for Troops Defense.")
        return

    tab_name = f"{team}_{category}"
    team_stats_list = fetch_data_with_cache(client_gs, WAR_SHEET_ID, tab_name, use_cache=not clear_cache)
    formatted_info = ""
    if team_stats_list:
        if category == "troops_defense" and defense_type:
            title = f"## {team.upper()} {defense_type.title()} Defense"
        else:
            title = f"## {team.upper()} {category.replace('_', ' ').title()}"
        
        if category in ["troops_attack", "dragon_attack", "dragon_defense"]:
            header = "{:<20} {:<10} {:<10}\n".format("Player", "Troop", "Score")
            separator = "=" * 36 + "\n"
            formatted_info = f"{title}\n\n```\n" + header + separator
        elif category == "troops_defense":
            if defense_type == "base":
                header = "{:<20} {:<10} {:<10}\n".format("Player", "Troop", "Base")
            elif defense_type == "glam":
                header = "{:<20} {:<10} {:<10}\n".format("Player", "Troop", "Glam")
            separator = "=" * 36 + "\n"
            formatted_info = f"{title}\n\n```\n" + header + separator
        elif category in ["rally_caps", "rein_caps"]:
            header = "{:<20} {:<10} {:<10}\n".format("Player", "Troop", "Cap")
            separator = "=" * 36 + "\n"
            formatted_info = f"{title}\n\n```\n" + header + separator

        messages = []
        current_message = formatted_info

        for entry in team_stats_list:
            player_info = ""
            if category in ["troops_attack", "dragon_attack", "dragon_defense"]:
                player_info = "{:<20} {:<10} {:<10}\n".format(entry['Player'], entry['Troop'], entry['Score'])
            elif category == "troops_defense":
                if defense_type == "base":
                    player_info = "{:<20} {:<10} {:<10}\n".format(entry['Player'], entry['Troop'], entry['Base'])
                elif defense_type == "glam":
                    player_info = "{:<20} {:<10} {:<10}\n".format(entry['Player'], entry['Troop'], entry['Glam'])
            elif category in ["rally_caps", "rein_caps"]:
                player_info = "{:<20} {:<10} {:<10}\n".format(entry['Player'], entry['Troop'], entry['Cap'])

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
        await ctx.send(f"No data found for the specified team and category: {tab_name}")