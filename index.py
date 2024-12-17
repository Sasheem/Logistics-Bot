import discord
from interactions import Client
import os 
from dotenv import load_dotenv

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
from commands.keep_logistics import keep_logistics
from commands.rca_info import rca_info
from commands.list_rca_logs import list_rca_logs
from commands.roster_t4s import roster_t4s
from commands.name_change import name_change
from commands.stats_compare import stats_compare
from commands.stats_review import stats_review
from commands.stats_analysis import stats_analysis

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

# TEAM-OVERVIEW command
@client.command(
    name="team-overview",
    description="Fetch the team overview for a specific category and type.",
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
        {
            "name": "type",
            "description": "Select the type",
            "type": 3,  # STRING type
            "required": True,
            "choices": [
                {"name": "All", "value": "All"},
                {"name": "WHSKY", "value": "WHSKY"},
                {"name": "TANGO", "value": "TANGO"},
                {"name": "FXTRT", "value": "FXTRT"},
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

# Register the STATS COMPARE command
@client.command(
    name="stats-compare",
    description="Compare the stats of two players.",
    options=[
        {
            "name": "type",
            "description": "Enter the type of stats (attack, defense, dragon-attack, dragon-defense)",
            "type": 3,  # STRING type
            "required": True,
            "choices": [
                {"name": "attack", "value": "attack"},
                {"name": "defense", "value": "defense"},
                {"name": "dragon-attack", "value": "dragon-attack"},
                {"name": "dragon-defense", "value": "dragon-defense"},
            ],
        },
        {
            "name": "name1",
            "description": "Enter the first player's name",
            "type": 3,  # STRING type
            "required": True,
        },
        {
            "name": "name2",
            "description": "Enter the second player's name",
            "type": 3,  # STRING type
            "required": True,
        },
    ],
)(stats_compare)

# Register the STATS REVIEW command
@client.command(
    name="stats-review",
    description="Fetch list of submissions needing review. Unavaiable at the moment.",
    options=[
        {
            "name": "type",
            "description": "Enter the type of stats (attack, defense, dragon)",
            "type": 3,  # STRING type
            "required": True,
            "choices": [
                {"name": "attack", "value": "attack"},
                {"name": "defense", "value": "defense"},
                {"name": "dragon", "value": "dragon"},
            ],
        },
    ],
)(stats_review)

# Register the STATS ANALYSIS command
@client.command(
    name="stats-analysis",
    description="Calculate analysis vs team (or tier) for given player. Unavaiable at the moment.",
    options=[
        {
            "name": "type",
            "description": "Enter the type of stats (attack, defense, dragon)",
            "type": 3,  # STRING type
            "required": True,
            "choices": [
                {"name": "attack", "value": "attack"},
                {"name": "defense", "value": "defense"},
                {"name": "dragon", "value": "dragon"},
            ],
        },
    ],
)(stats_analysis)

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
)(keep_logistics)

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
)(rca_info)

# RCA-LOGS command
@client.command(
    name="list-rca-logs",
    description="Fetch the list of RCA logs.",
    options=[
        {
            "name": "filter_type",
            "description": "Filter the RCA logs by type",
            "type": 3,  # STRING type
            "required": True,
            "choices": [
                {"name": "All", "value": "All"},
                {"name": "RCA", "value": "RCA"},
                {"name": "Holder", "value": "Holder"},
                {"name": "RCA Banner", "value": "RCA Banner"},
            ],
        },
        {
            "name": "min_cap",
            "description": "Minimum Rein Cap to filter the logs",
            "type": 4,  # INTEGER type
            "required": False,
        },
    ],
)(list_rca_logs)

# ROSTER-T4S command
@client.command(
    name="roster-t4s",
    description="Fetch the T4s for a specific T3 player.",
    options=[
        {
            "name": "name",
            "description": "The T3 player name to search for",
            "type": 3,  # STRING type
            "required": True,
        },
    ],
)(roster_t4s)

# NAME CHANGE command
@client.command(
    name="name-change",
    description="Change a player's name in the specified sheet and tab.",
    options=[
        {
            "name": "old_name",
            "description": "The old name to be changed",
            "type": 3,  # STRING type
            "required": True,
        },
        {
            "name": "new_name",
            "description": "The new name to replace the old name",
            "type": 3,  # STRING type
            "required": True,
        },
        {
            "name": "option",
            "description": "Select the sheet and tab to update",
            "type": 3,  # STRING type
            "required": True,
            "choices": [
                {"name": "TEST", "value": "TEST"},
                {"name": "Active Keeps", "value": "Active Keeps"},
                {"name": "Keep Logistics", "value": "Keep Logistics"},
                {"name": "Attack 89", "value": "Attack 89"},
                {"name": "Defense 89", "value": "Defense 89"},
                {"name": "Dragon 89", "value": "Dragon 89"},
                {"name": "Attack 33", "value": "Attack 33"},
                {"name": "Defense 33", "value": "Defense 33"},
                {"name": "Dragon 33", "value": "Dragon 33"},
                {"name": "RCA", "value": "RCA"},
            ],
        },
    ],
)(name_change)

# Event listener for when the bot is ready
@client.event
async def on_ready():
    print(f'We have logged in as {client.me}')

client.start()