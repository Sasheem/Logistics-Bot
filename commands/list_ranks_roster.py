# commands/list_ranks_roster.py

from interactions import CommandContext, Embed
from config.google_sheets import client_gs
from config.constants import WAR_SHEET_ID
from utils.fetch_data_with_cache import fetch_data_with_cache
from utils.last_updated import last_updated

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
            title = f"{team.upper()} {defense_type.title()} Defense"
        else:
            title = f"{team.upper()} {category.replace('_', ' ').title()}"

        # Determine the emoji and color based on the team
        if team.lower() in ["whsky", "tango"]:
            icon = "⚔️"  # Crossed swords emoji
            color = 0x0000FF if team.lower() == "whsky" else 0xFF0000  # Blue for Whsky, Red for Tango
        elif team.lower() == "fxtrt":
            icon = "🛡️"  # Shield emoji
            color = 0x00FF00  # Green color
        else:
            icon = ""
            color = 0xFFFFFF  # White color

        # Add additional emojis based on the category
        if category in ["dragon_attack", "dragon_defense"]:
            icon += " 🐉"  # Dragon emoji
        elif category == "rally_caps":
            icon += " 🪓"  # Battering ram emoji
        elif category == "rein_caps":
            icon += " 🏰"  # Castle wall emoji

        if category in ["troops_attack", "dragon_attack", "dragon_defense"]:
            header = "{:<18} {:<8} {:<16}\n".format("Player", "Troop", "Score")
            separator = "=" * 34 + "\n"
            formatted_info = header + separator
        elif category == "troops_defense":
            if defense_type == "base":
                header = "{:<18} {:<8} {:<16}\n".format("Player", "Troop", "Base")
            elif defense_type == "glam":
                header = "{:<18} {:<8} {:<16}\n".format("Player", "Troop", "Glam")
            separator = "=" * 34 + "\n"
            formatted_info = header + separator
        elif category in ["rally_caps", "rein_caps"]:
            header = "{:<18} {:<8} {:<16}\n".format("Player", "Troop", "Cap")
            separator = "=" * 34 + "\n"
            formatted_info = header + separator

        for entry in team_stats_list:
            player_info = ""
            if category in ["troops_attack", "dragon_attack", "dragon_defense"]:
                player_info = "{:<18} {:<8} {:<16}\n".format(entry['Player'], entry['Troop'], entry['Score'])
            elif category in "troops_defense":
                if defense_type == "base":
                    player_info = "{:<18} {:<8} {:<16}\n".format(entry['Player'], entry['Troop'], entry['Base'])
                elif defense_type == "glam":
                    player_info = "{:<18} {:<8} {:<16}\n".format(entry['Player'], entry['Troop'], entry['Glam'])
            elif category in ["rally_caps", "rein_caps"]:
                player_info = "{:<18} {:<8} {:<16}\n".format(entry['Player'], entry['Troop'], entry['Cap'])

            formatted_info += player_info

        # Split the formatted_info into chunks if it exceeds the Discord limit
        chunks = [formatted_info[i:i + 4000] for i in range(0, len(formatted_info), 4000)]

        embeds = []
        for chunk in chunks:
            embed = Embed(
                title=f"{title} {icon}",
                description=f"```\n{chunk}```\n\nLast Updated: **{last_updated()}**",
                color=color
            )
            embeds.append(embed)

        for embed in embeds:
            await ctx.send(embeds=[embed])
    else:
        await ctx.send(f"No data found for the specified team and category: {tab_name}")