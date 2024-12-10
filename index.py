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
from commands.stats_history import stats_history
from commands.rank import rank
from commands.list_ranks import list_ranks
from commands.list_ranks_dragon import list_ranks_dragon
from commands.list_ranks_roster import list_ranks_roster
from commands.list_name_changes import list_name_changes

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

# STATS POWER command
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
)(stats_history)

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
)(list_ranks)

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
)(list_ranks_dragon)

# ROSTER-RANKS command
@client.command(
    name="list-ranks-roster",
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
)(list_ranks_roster)

# LIST-NAME-CHANGES command
@client.command(
    name="list-name-changes",
    description="Fetch the list of recent name changes.",
)(list_name_changes)

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