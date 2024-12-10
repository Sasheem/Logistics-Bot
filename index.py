import discord
from interactions import Client, CommandContext
import math
import os 
from dotenv import load_dotenv
from fuzzywuzzy import fuzz, process

# Load the client
from config.google_sheets import client_gs

# Load the constants
from config.constants import WAR_SHEET_ID, ATTACK_SHEET_ID, DEFENSE_SHEET_ID, DRAGON_SHEET_ID, ROSTER_SHEET_ID, RCA_SHEET_ID

# Load the helpers
from utils.fetch_sheets_data import fetch_sheets_data
from utils.fetch_data_with_cache import fetch_data_with_cache
from utils.fetch_roster_info import fetch_roster_info
from utils.fetch_player_info import fetch_player_info

# Load the commands
from commands.team_overview import team_overview
from commands.roster_position import roster_position
from commands.stats_power import stats_power
from commands.rank import rank

load_dotenv()

# Determine the environment
environment = os.getenv('ENVIRONMENT', 'live')

# Set the tokens based on the environment
if environment == 'test':
    TOKEN = os.getenv('DISCORD_TOKEN_TEST')
else:
    TOKEN = os.getenv('DISCORD_TOKEN_LIVE')

# Discord bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
client = Client(token=TOKEN)

# Event listener for when the bot is ready
@client.event
async def on_ready():
    print(f'We have logged in as {client.me}')

# TEAM-OVERVIEW command
@client.command(
    name="team-overview",
    description="Fetch the team overview for a specific category.",
    options=[
        {
            "name": "category",
            "description": "Select the category",
            "type": 3,  # STRING type
            "required": True,
            "choices": [
                {"name": "Attack", "value": "attack"},
                {"name": "Defense", "value": "defense"},
                {"name": "Dragon Attack", "value": "dragon_attack"},
                {"name": "Dragon Defense", "value": "dragon_defense"},
            ],
        },
    ],
)(team_overview)

# ROSTER POSITION command
@client.command(
    name="roster-position",
    description="Get the roster position for a player.",
    options=[
        {
            "name": "name",
            "description": "Enter player name exactly as it appears in the roster",
            "type": 3,  # STRING type
            "required": True,
        },
    ],
)(roster_position)

# STATS command
@client.command(
    name="stats-power",
    description="Find a player's total troop power and dragon stats.",
    options=[
        {
            "name": "type",
            "description": "Select the type of stats",
            "type": 3,  # STRING type
            "required": True,
            "choices": [
                {"name": "Attack", "value": "attack"},
                {"name": "Defense", "value": "defense"},
                {"name": "Dragon Attack", "value": "dragon-attack"},
                {"name": "Dragon Defense", "value": "dragon-defense"},
            ],
        },
        {
            "name": "name",
            "description": "Enter player name exactly as you submitted stats",
            "type": 3,  # STRING type
            "required": True,
        },
    ],
)(stats_power)

# RANK command
@client.command(
    name="rank",
    description="Find a player's rank and score for different categories.",
    options=[
        {
            "name": "type",
            "description": "Select the type of rank",
            "type": 3,  # STRING type
            "required": True,
            "choices": [
                {"name": "Attack", "value": "attack"},
                {"name": "Defense", "value": "defense"},
                {"name": "Dragon", "value": "dragon"},
            ],
        },
        {
            "name": "name",
            "description": "Enter player name exactly as you submitted stats",
            "type": 3,  # STRING type
            "required": True,
        },
    ],
)(rank)


# LIST RANKS command
@client.command(
    name="list-ranks",
    description="List all players' ranks and scores for different categories.",
    options=[
        {
            "name": "type",
            "description": "Select the type of ranks",
            "type": 3,  # STRING type
            "required": True,
            "choices": [
                {"name": "Attack", "value": "attack"},
                {"name": "Defense", "value": "defense"},
            ],
        },
        {
            "name": "category",
            "description": "Select the category",
            "type": 3,  # STRING type
            "required": True,
            "choices": [
                {"name": "Team", "value": "team"},
                {"name": "Infantry", "value": "inf"},
                {"name": "Cavalry", "value": "cav"},
                {"name": "Range", "value": "range"},
                {"name": "T12", "value": "t12"},
                {"name": "T11", "value": "t11"},
                {"name": "T10", "value": "t10"},
                {"name": "T9", "value": "t9"},
                {"name": "T8", "value": "t8"},
            ],
        },
        {
            "name": "limit",
            "description": "Enter the number of players to display (default is all)",
            "type": 4,  # INTEGER type
            "required": False,
        },
    ],
)
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

# LIST RANKS DRAGON command
@client.command(
    name="list-ranks-dragon",
    description="List all players' dragon ranks and scores.",
    options=[
        {
            "name": "type",
            "description": "Select the type of dragon ranks",
            "type": 3,  # STRING type
            "required": True,
            "choices": [
                {"name": "Dragon Attack", "value": "dragon-attack"},
                {"name": "Dragon Defense", "value": "dragon-defense"},
            ],
        },
        {
            "name": "limit",
            "description": "Enter the number of players to display (default is all)",
            "type": 4,  # INTEGER type
            "required": False,
        },
    ],
)
async def list_ranks_dragon(ctx: CommandContext, type: str, limit: int = None):
    await ctx.defer()  # Acknowledge the interaction to avoid "Unknown Interaction" error
    rank_types = {
        "dragon-attack": "dragon_attack_rank",
        "dragon-defense": "dragon_defense_rank",
    }
    rank_type = rank_types.get(type)
    players_info = fetch_data_with_cache(client_gs, WAR_SHEET_ID, rank_type)
    if players_info:
        if limit:
            players_info = players_info[:limit]
        title = f"{type.replace('-', ' ').title()} Ranks"
        subtitle = f"Showing top {limit} players" if limit else ""
        header = "{:<20} {:<10} {:<10}\n".format(
            "Player Name", "Score", "Rank"
        )
        separator = "=" * 36 + "\n"
        formatted_info = f"# {title} \n{subtitle}\n```\n" + header + separator
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

# LIST-NAME-CHANGES command
@client.command(
    name="list-name-changes",
    description="Fetch the list of recent name changes.",
)
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

# ROSTER-RANKS command
@client.command(
    name="roster-ranks",
    description="Fetch the ranks for a specific team and category.",
    options=[
        {
            "name": "team",
            "description": "Select the team",
            "type": 3,  # STRING type
            "required": True,
            "choices": [
                {"name": "WHSKY", "value": "whsky"},
                {"name": "TANGO", "value": "tango"},
                {"name": "FXTRT", "value": "fxtrt"},
            ],
        },
        {
            "name": "category",
            "description": "Select the category",
            "type": 3,  # STRING type
            "required": True,
            "choices": [
                {"name": "Troops Attack", "value": "troops_attack"},
                {"name": "Troops Defense", "value": "troops_defense"},
                {"name": "Rally Caps", "value": "rally_caps"},
                {"name": "Rein Caps", "value": "rein_caps"},
                {"name": "Dragon Attack", "value": "dragon_attack"},
                {"name": "Dragon Defense", "value": "dragon_defense"},
            ],
        },
        {
            "name": "defense_type",
            "description": "Select the defense type (only for Troops Defense)",
            "type": 3,  # STRING type
            "required": False,
            "choices": [
                {"name": "Base", "value": "base"},
                {"name": "Glam", "value": "glam"},
            ],
        },
    ],
)
async def roster_ranks(ctx: CommandContext, team: str, category: str, defense_type: str = None):
    await ctx.defer()  # Acknowledge the interaction to avoid "Unknown Interaction" error

    if category != "troops_defense" and defense_type:
        await ctx.send("The defense type option is only applicable for Troops Defense. Please select the correct category.")
        return

    if category == "troops_defense" and not defense_type:
        await ctx.send("Please select a defense type (Base or Glam) for Troops Defense.")
        return

    tab_name = f"{team}_{category}"
    team_stats_list = fetch_sheets_data(client_gs, WAR_SHEET_ID, tab_name)
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

# STATS-HISTORY command
@client.command(
    name="stats-history",
    description="Fetch the stats history for a specific player.",
    options=[
        {
            "name": "player_name",
            "description": "Enter the player's name",
            "type": 3,  # STRING type
            "required": True,
        },
        {
            "name": "category",
            "description": "Select the category",
            "type": 3,  # STRING type
            "required": True,
            "choices": [
                {"name": "Attack", "value": "attack"},
                {"name": "Defense", "value": "defense"},
                {"name": "Dragon", "value": "dragon"},
            ],
        },
        {
            "name": "limit",
            "description": "Limit the number of entries returned",
            "type": 4,  # INTEGER type
            "required": False,
        },
    ],
)
async def stats_history(ctx: CommandContext, player_name: str, category: str, limit: int = None):
    await ctx.defer()  # Acknowledge the interaction to avoid "Unknown Interaction" error

    spreadsheet_id = ""
    tab_name = ""

    if category == "attack":
        spreadsheet_id = ATTACK_SHEET_ID
        tab_name = "attack_history"
    elif category == "defense":
        spreadsheet_id = DEFENSE_SHEET_ID
        tab_name = "defense_history"
    elif category == "dragon":
        spreadsheet_id = DRAGON_SHEET_ID
        tab_name = "dragon_history"

    player_stats_list = fetch_sheets_data(client_gs, spreadsheet_id, tab_name)
    
    # Exact match
    player_entries = [entry for entry in player_stats_list if entry['Player'].lower() == player_name.lower()]

    # Soft match if no exact match found
    if not player_entries:
        soft_matches = process.extract(player_name, [entry['Player'] for entry in player_stats_list], scorer=fuzz.token_sort_ratio)
        best_match = soft_matches[0] if soft_matches else None
        if best_match and best_match[1] > 70:  # Threshold for a good match
            player_entries = [entry for entry in player_stats_list if entry['Player'] == best_match[0]]

    if limit:
        player_entries = player_entries[:limit]

    if player_entries:
        title = f"Stats History for {player_name}"
        for index, entry in enumerate(player_entries, start=1):
            formatted_info = [f"## {category.title()} entry {index} on {entry['Date']}"]
            base_section = False
            glam_section = False
            buffs_section = False
            dvd_section = False
            defense_section = False
            for key, value in entry.items():
                if key in ['Date', 'Additional Details', 'Editor Notes']:
                    continue
                if "(Base)" in key and not base_section:
                    formatted_info.append("**-- Base --**")
                    base_section = True
                if "(Glam)" in key and not glam_section:
                    formatted_info.append("**-- Glam --**")
                    glam_section = True
                if "(Buffs)" in key and not buffs_section:
                    formatted_info.append("**-- Buffs --**")
                    buffs_section = True
                if "(DvD)" in key and not dvd_section:
                    formatted_info.append("**-- DvD --**")
                    dvd_section = True
                if "(Defense)" in key and not defense_section:
                    formatted_info.append("**-- Defense --**")
                    defense_section = True
                formatted_key = key.replace("(Base)", "").replace("(Glam)", "").replace("(Buffs)", "").replace("(DvD)", "").replace("(Defense)", "").strip()
                formatted_value = f"{round(value):,}" if isinstance(value, (int, float)) and math.isfinite(value) else f"{value}"
                formatted_info.append(f"{formatted_key}: {formatted_value}")
            if 'Additional Details' in entry:
                formatted_info.append(f"**-- Additional Details --**\n{entry['Additional Details']}")
            if 'Editor Notes' in entry:
                formatted_info.append(f"## Editor Notes:\n{entry['Editor Notes']}")
            await ctx.send(f"# {title}:\n" + "\n".join(formatted_info))
    else:
        await ctx.send(f"## Oops, this is embarrassing..\n\nNo entries found for: **{player_name}**.\nPlease check the spelling and try again.")

# KEEP-LOGISTICS command
@client.command(
    name="keep-logistics",
    description="Fetch the logistics for a specific keep or Discord name.",
    options=[
        {
            "name": "keep_name",
            "description": "Enter the Keep's name",
            "type": 3,  # STRING type
            "required": False,
        },
        {
            "name": "discord_name",
            "description": "Enter the Discord name",
            "type": 3,  # STRING type
            "required": False,
        },
    ],
)
async def keep_logistics(ctx: CommandContext, keep_name: str = None, discord_name: str = None):
    await ctx.defer()  # Acknowledge the interaction to avoid "Unknown Interaction" error
    keeps_list = fetch_sheets_data(client_gs, ROSTER_SHEET_ID, "bot_keep_logistics")

    if keep_name and discord_name:
        await ctx.send("Please provide either a Keep name or a Discord name, not both.")
        return

    entries = []
    name_type = ""
    if keep_name:
        name_type = "keep name"
        # Exact match
        entries = [record for record in keeps_list if str(record['Main Keep Name']).lower() == keep_name.lower()]
        # Soft match if no exact match found
        if not entries:
            soft_matches = process.extract(keep_name, [record['Main Keep Name'] for record in keeps_list], scorer=fuzz.token_sort_ratio)
            best_match = soft_matches[0] if soft_matches else None
            if best_match and best_match[1] > 70:  # Threshold for a good match
                entries = [record for record in keeps_list if record['Main Keep Name'] == best_match[0]]
    elif discord_name:
        name_type = "discord username"
        # Exact match
        entries = [record for record in keeps_list if str(record['Discord Name']).lower() == discord_name.lower()]
        # Soft match if no exact match found
        if not entries:
            soft_matches = process.extract(discord_name, [record['Discord Name'] for record in keeps_list], scorer=fuzz.token_sort_ratio)
            best_match = soft_matches[0] if soft_matches else None
            if best_match and best_match[1] > 70:  # Threshold for a good match
                entries = [record for record in keeps_list if record['Discord Name'] == best_match[0]]
    else:
        await ctx.send("Please provide either a Keep name or a Discord name.")
        return

    if entries:
        for i, entry in enumerate(entries, start=1):
            title = f"Keep Logistics Entry {i}"
            subtitle = f"Discord Name: {entry['Discord Name']}\nDate: {entry['Date']}"
            divider = "--" * 10  # Section divider
            details = (
                f"**Main Keep Name**: \n{entry['Main Keep Name']}\n"
                f"**Main Keep Access**: \n{entry['Main Keep Access']}\n"
                f"**Secondary Keep Names**: \n{entry['Secondary Keep Names']}\n"
                f"**Alt Keep Names**: \n{entry['Alt Keep Names']}\n"
                f"**Additional Details**: \n{entry['Additional Details']}\n"
            )
            message = f"# {title}\n{subtitle}\n{divider}\n{details}"
            await ctx.send(message)
    else:
        if keep_name:
            await ctx.send(f"## Oops, this is embarrassing..\n\nSearched by {name_type}.\nNo entries found for: **{keep_name}**.\nPlease check the spelling and try again.")
        else:
            await ctx.send(f"## Oops, this is embarrassing..\n\nSearched by {name_type}.\nNo entries found for: **{discord_name}**.\nPlease check the spelling and try again.")

# RCA-INFO command
@client.command(
    name="rca-info",
    description="Fetch the RCA info for a specific name.",
    options=[
        {
            "name": "name",
            "description": "Enter the name",
            "type": 3,  # STRING type
            "required": True,
        },
    ],
)
async def rca_info(ctx: CommandContext, name: str):
    await ctx.defer()  # Acknowledge the interaction to avoid "Unknown Interaction" error
    rca_list = fetch_sheets_data(client_gs, RCA_SHEET_ID, "bot_rca_info")
    
    # Exact match
    entries = [record for record in rca_list if str(record['Name']).lower() == name.lower()]

    # Soft match if no exact match found
    if not entries:
        soft_matches = process.extract(name, [record['Name'] for record in rca_list], scorer=fuzz.token_sort_ratio)
        best_match = soft_matches[0] if soft_matches else None
        if best_match and best_match[1] > 70:  # Threshold for a good match
            entries = [record for record in rca_list if record['Name'] == best_match[0]]

    if entries:
        for i, entry in enumerate(entries, start=1):
            title = f"RCA Info {i}: {entry['Name']}"
            subtitle = f"Type: {entry['Type']}\nRein Cap: {entry['Rein Cap']}\nPower Level: {entry['Power Level']}"
            details = (
                f"**Email**: \n{entry['Email']}\n\n"
                f"**Password**: \n{entry['Password']}\n\n"
                f"**Facebook Name**: \n{entry['Facebook Name']}\n\n"
                f"**Access**: \n{entry['Access']}\n\n"
                f"**Force Logs**: \n{entry['Force Logs']}\n"
                f"**Notes**: \n{entry['Notes']}\n"
            )
            message = f"## {title}\n{subtitle}\n{'--' * 10}\n{details}"
            await ctx.send(message)
    else:
        await ctx.send(f"## Oops, this is embarrassing..\n\nNo entries found for: **{name}**.\nPlease check the spelling and try again.")

# RCA-LOGS command
@client.command(
    name="rca-logs",
    description="Fetch the RCA logs.",
)
async def rca_logs(ctx: CommandContext):
    await ctx.defer()  # Acknowledge the interaction to avoid "Unknown Interaction" error
    rca_logs_list = fetch_sheets_data(client_gs, RCA_SHEET_ID, "bot_rca_info")
    if rca_logs_list:
        messages = []
        chunk_counter = 1
        formatted_info = f"# RCA Logs {chunk_counter}\n" + "```\n"
        for entry in rca_logs_list:
            name = entry['Name']
            rein_cap = entry['Rein Cap']
            type_ = entry['Type']
            power_level = entry['Power Level']
            facebook_name = entry['Facebook Name']
            email = entry['Email']
            password = entry['Password']
            entry_info = (
                f"{name:<20}\n"
                f"{rein_cap} | {type_} | {power_level}\n"
                f"{'-' * 5}\n"
                f"FB: {facebook_name:<20}\n"
                f"{email} | {password}\n"
                + "-" * 30 + "\n"
            )
            if len(formatted_info) + len(entry_info) + 3 > 2000:  # 2000 is the Discord message limit
                formatted_info += "```"
                messages.append(formatted_info)
                chunk_counter += 1
                formatted_info = f"# RCA Logs {chunk_counter}\n" + "```\n" + entry_info
            else:
                formatted_info += entry_info
        formatted_info += "```"
        messages.append(formatted_info)
        
        for message in messages:
            await ctx.send(message)
    else:
        await ctx.send("No RCA logs found.")


client.start()