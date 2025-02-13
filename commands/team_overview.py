# commands/team_overview.py

from interactions import CommandContext
from utils.fetch_data_with_cache import fetch_data_with_cache
from config.google_sheets import client_gs
from config.constants import WAR_SHEET_ID

async def team_overview(ctx: CommandContext, category: str, type: str, clear_cache: bool = False):
    await ctx.defer()  # Acknowledge the interaction to avoid "Unknown Interaction" error
    await ctx.send("Command is down for maintenance. Please try again later.")
    # tab_name = f"{category}_overview"
    # team_data = fetch_data_with_cache(client_gs, WAR_SHEET_ID, tab_name, use_cache=not clear_cache)

    # if team_data:
    #     if type == "All Rosters":
    #         types = ["WHSKY", "TANGO", "FXTRT"]
    #     else:
    #         types = [type]

    #     formatted_info = []

    #     for team_type in types:
    #         title = f"{team_type} {category.replace('_', ' ').title()} Overview"
    #         formatted_info.append(f"## {title}")

    #         for entry in team_data:
    #             entry = {k.replace(f"{team_type} ", ""): v for k, v in entry.items() if k.startswith(team_type)}

    #             formatted_info.append(f"Total:  **{entry['Submissions']}**")
    #             formatted_info.append(f"**-- Troop Types --**")
    #             formatted_info.append(f"Infantry:  {entry['Infantry Totals']}")
    #             formatted_info.append(f"Cavalry:  {entry['Cavalry Totals']}")
    #             formatted_info.append(f"Range:  {entry['Range Totals']}")
    #             formatted_info.append(f"Siege:  {entry['Siege Totals']}")
    #             formatted_info.append(f"RCA:  {entry['RCA Totals']}")
    #             formatted_info.append(f"**-- Troop Tiers --**")
    #             formatted_info.append(f"T12s:  {entry['T12s Totals']}")
    #             formatted_info.append(f"T11s:  {entry['T11s Totals']}")
    #             formatted_info.append(f"T10s:  {entry['T10s Totals']}")
    #             formatted_info.append(f"T9s:  {entry['T9s Totals']}")
    #             formatted_info.append(f"T8s:  {entry['T8s Totals']}")

    #             if category in ["dragon_attack", "dragon_defense"]:
    #                 formatted_info.append(f"**-- Dragon Levels --**")
    #                 formatted_info.append(f"Lvl 69:  {entry['Lvl 69 Totals']}")
    #                 formatted_info.append(f"Lvl 65+:  {entry['Lvl 65+ Totals']}")

    #             if category in ["dragon_attack"]:
    #                 formatted_info.append(f"Lvl 41+:  {entry['Lvl 41+ Totals']}")

    #             # formatted_info.append("\n")

    #     await ctx.send("\n".join(formatted_info))
    # else:
    #     await ctx.send("No data found for the specified category and type.")