import discord
from interactions import Client, OptionType
import os 
from dotenv import load_dotenv

# Load the commands
from commands.team_overview import team_overview
from commands.roster_position import roster_position
from commands.roster_t4s import roster_t4s
from commands.roster_alts import roster_alts
from commands.list_roster_notes import list_roster_notes
from commands.roster_notes_add import roster_notes_add
from commands.roster_notes_remove import roster_notes_remove
from commands.roster_notes_manage import roster_notes_manage
from commands.stats_power import stats_power
from commands.stats_history import stats_history
from commands.rank import rank
from commands.list_ranks import list_ranks
from commands.list_ranks_dragon import list_ranks_dragon
from commands.list_ranks_roster import list_ranks_roster
from commands.keep_logistics import keep_logistics
from commands.rca_info import rca_info
from commands.list_rca_logs import list_rca_logs
from commands.name_change import name_change
from commands.stats_compare import stats_compare
from commands.stats_review import stats_review
from commands.stats_analysis import stats_analysis
from commands.list_name_changes import list_name_changes
from commands.list_old_stats import list_old_stats
from commands.active_alts import active_alts
from commands.remove_player import remove_player
from commands.war_prep import war_prep

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
    description="Breakdown of troop tier/types for team and rosters.",
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
                {"name": "All Rosters", "value": "All Rosters"},
                {"name": "WHSKY", "value": "WHSKY"},
                {"name": "TANGO", "value": "TANGO"},
                {"name": "FXTRT", "value": "FXTRT"},
            ],
        },
        {
            "name": "clear_cache",
            "description": "Clear cache and fetch fresh data",
            "type": 5,  # BOOLEAN type
            "required": False,
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
        {
            "name": "clear_cache",
            "description": "Clear cache and fetch fresh data",
            "type": 5,  # BOOLEAN type
            "required": False,
        },
    ],
)(roster_position)

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
        {
            "name": "clear_cache",
            "description": "Clear cache and fetch fresh data",
            "type": 5,  # BOOLEAN type
            "required": False,
        },
    ],
)(roster_t4s)

# ROSTER-ALTS command
@client.command(
    name="roster-alts",
    description="List roster alts for a specific team and type.",
    options=[
        {
            "name": "team",
            "description": "Select the team",
            "type": 3,  # STRING type
            "required": True,
            "choices": [
                {"name": "WHSKY", "value": "WHSKY"},
                {"name": "TANGO", "value": "TANGO"},
                {"name": "FXTRT", "value": "FXTRT"},
            ],
        },
        {
            "name": "type",
            "description": "Select the type",
            "type": 3,  # STRING type
            "required": True,
            "choices": [
                {"name": "All", "value": "All"},
                {"name": "RCA", "value": "RCA"},
                {"name": "Alt", "value": "Alt"},
                {"name": "X", "value": "X"},
            ],
        },
        {
            "name": "clear_cache",
            "description": "Clear cache and fetch fresh data",
            "type": 5,  # BOOLEAN type
            "required": False,
        },
    ],
)(roster_alts)

# ROSTER NOTES command
# Command registration for list_roster_notes

@client.command(
    name="rosternotes",
    description="List the roster notes for the current week"
)(list_roster_notes)

# ROSTERNOTES MANAGE command
@client.command(
    name="rosternotes-manage",
    description="Manage the roster notes",
    options=[
        {
            "name": "clear_notes",
            "description": "Clear all roster notes (true/false)",
            "type": OptionType.BOOLEAN,
            "required": False
        },
        {
            "name": "restore_backup",
            "description": "Restore roster notes from backup (true/false)",
            "type": OptionType.BOOLEAN,
            "required": False
        },
        {
            "name": "clear_backup",
            "description": "Clear the backup roster notes (true/false)",
            "type": OptionType.BOOLEAN,
            "required": False
        }
    ]
)(roster_notes_manage)


# ROSTER NOTES ADD command
@client.command(
    name="rosternotes-add",
    description="Add a note to the roster",
    options=[
        {
            "name": "subject",
            "description": "The subject of the note (max 50 characters)",
            "type": OptionType.STRING,
            "required": True,
            "max_length": 50
        },
        {
            "name": "note",
            "description": "The content of the note",
            "type": OptionType.STRING,
            "required": True,
        },
        {
            "name": "author",
            "description": "The author of the note (max 30 characters)",
            "type": OptionType.STRING,
            "required": True,
            "max_length": 30
        }
    ]
)(roster_notes_add)

# ROSTER NOTES REMOVE command
@client.command(
    name="rosternotes-remove",
    description="Remove a note from the roster",
    options=[
        {
            "name": "subject",
            "description": "The subject of the note to remove (case-insensitive)",
            "type": OptionType.STRING,
            "required": True,
            "max_length": 50
        }
    ]
)(roster_notes_remove)

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
                {"name": "Dragon", "value": "dragon"},
            ],
        },
        {
            "name": "name",
            "description": "Enter player name exactly as you submitted stats",
            "type": 3,  # STRING type
            "required": True,
        },
        {
            "name": "clear_cache",
            "description": "Clear cache and fetch fresh data",
            "type": 5,  # BOOLEAN type
            "required": False,
        },
    ],
)(stats_power)

# STATS-HISTORY command
@client.command(
    name="stats-history",
    description="Fetch all stats submitted for a specific player.",
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
        {
            "name": "clear_cache",
            "description": "Clear cache and fetch fresh data",
            "type": 5,  # BOOLEAN type
            "required": False,
        },
    ],
)(stats_history)

# STATS COMPARE command
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
        {
            "name": "clear_cache",
            "description": "Clear cache and fetch fresh data",
            "type": 5,  # BOOLEAN type
            "required": False,
        },
    ],
)(stats_compare)

# STATS REVIEW command
@client.command(
    name="stats-review",
    description="Fetch list of submissions needing review.",
    options=[
        {
            "name": "type",
            "description": "Enter the type of stats (attack, defense, dragon)",
            "type": OptionType.STRING,
            "required": True,
            "choices": [
                {"name": "attack", "value": "attack"},
                {"name": "defense", "value": "defense"},
                {"name": "dragon", "value": "dragon"},
            ],
        },
        {
            "name": "filter_by",
            "description": "Filter the stats by a specific criterion",
            "type": OptionType.STRING,
            "required": True,
            "choices": [
                {"name": "New", "value": "New"},
                {"name": "Duplicates", "value": "Duplicates"},
                {"name": "Last Week", "value": "Last Week"},
                {"name": "Last Month", "value": "Last Month"},
                {"name": "Over a month", "value": "Over a month"}
            ]
        }
    ]
)(stats_review)

# STATS ANALYSIS command
@client.command(
    name="stats-analysis",
    description="Analyze the stats of a player against the average stats.",
    options=[
        {
            "name": "type",
            "description": "Enter the type of stats (attack, defense)",
            "type": 3,  # STRING type
            "required": True,
            "choices": [
                {"name": "attack", "value": "attack"},
                {"name": "defense", "value": "defense"},
            ],
        },
        {
            "name": "tier",
            "description": "Enter the troop tier (All, T12, T11, T10, T09, T08)",
            "type": 3,  # STRING type
            "required": True,
            "choices": [
                {"name": "All", "value": "All"},
                {"name": "T12", "value": "T12"},
                {"name": "T11", "value": "T11"},
                {"name": "T10", "value": "T10"},
                {"name": "T09", "value": "T09"},
                {"name": "T08", "value": "T08"},
            ],
        },
        {
            "name": "troop",
            "description": "Enter the troop type",
            "type": 3,  # STRING type
            "required": True,
            "choices": [
                {"name": "All", "value": "All"},
                {"name": "Inf", "value": "inf"},
                {"name": "Ranged", "value": "Ranged"},
                {"name": "Cav", "value": "Cav"},
            ],
        },
        {
            "name": "percentile",
            "description": "Enter the percentile rank (All, 1, 2, 3, 4)",
            "type": 3,  # STRING type
            "required": True,
            "choices": [
                {"name": "All", "value": "All"},
                {"name": "Top 25%", "value": "1"},
                {"name": "26% to 50%", "value": "2"},
                {"name": "51% to 75%", "value": "3"},
                {"name": "Bottom 25%", "value": "4"},
            ],
        },
        {
            "name": "name",
            "description": "Enter the player's name",
            "type": 3,  # STRING type
            "required": True,
        },
        {
            "name": "clear_cache",
            "description": "Clear cache and fetch fresh data",
            "type": 5,  # BOOLEAN type
            "required": False,
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
        {
            "name": "clear_cache",
            "description": "Clear cache and fetch fresh data",
            "type": 5,  # BOOLEAN type
            "required": False,
        },
    ],
)(rank)

# RANKS TROOPS command
@client.command(
    name="ranks-troops",
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
        {
            "name": "clear_cache",
            "description": "Clear cache and fetch fresh data",
            "type": 5,  # BOOLEAN type
            "required": False,
        },
    ],
)(list_ranks)

# RANKS DRAGONs command
@client.command(
    name="ranks-dragons",
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
        {
            "name": "clear_cache",
            "description": "Clear cache and fetch fresh data",
            "type": 5,  # BOOLEAN type
            "required": False,
        },
    ],
)(list_ranks_dragon)

# RANKS ROSTER command
@client.command(
    name="ranks-roster",
    description="Fetch ranks for WHSKY, TANGO, or FXTRT by category.",
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
        {
            "name": "clear_cache",
            "description": "Clear cache and fetch fresh data",
            "type": 5,  # BOOLEAN type
            "required": False,
        },
    ],
)(list_ranks_roster)

# KEEP-LOGISTICS command
@client.command(
    name="keep-logistics",
    description="Fetch the keep logistics by Keep Name or Discord Name.",
    options=[
        {
            "name": "name",
            "description": "Enter the Keep's name or Discord name",
            "type": 3,  # STRING type
            "required": True,
        },
        {
            "name": "clear_cache",
            "description": "Clear cache and fetch fresh data",
            "type": 5,  # BOOLEAN type
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
        {
            "name": "clear_cache",
            "description": "Clear cache and fetch fresh data",
            "type": 5,  # BOOLEAN type
            "required": False,
        },
    ],
)(rca_info)

# LIST RCA-LOGS command
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
        {
            "name": "clear_cache",
            "description": "Clear cache and fetch fresh data",
            "type": 5,  # BOOLEAN type
            "required": False,
        },
    ],
)(list_rca_logs)

# NAME CHANGE command
@client.command(
    name="name-change",
    description="Change a player's name in the specified stat sheet.",
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

# RECENT NAME-CHANGES command
@client.command(
    name="recent-name-changes",
    description="Fetch the list of recent name changes.",
    options=[
        {
            "name": "clear_cache",
            "description": "Clear cache and fetch fresh data",
            "type": 5,  # BOOLEAN type
            "required": False,
        },
    ],
)(list_name_changes)

# LIST OLD-STATS command
@client.command(
    name="old-stats",
    description="List players with old stats based on the provided month category and optional tier filter.",
    options=[
        {
            "name": "months",
            "description": "Number of months to filter stats older than.",
            "type": 4,  # INTEGER type
            "required": True,
        },
        {
            "name": "tier",
            "description": "Optional tier to filter by (T12, T11, T10, T09, T08).",
            "type": 3,  # STRING type
            "required": False,
            "choices": [
                {"name": "T12", "value": "T12"},
                {"name": "T11", "value": "T11"},
                {"name": "T10", "value": "T10"},
                {"name": "T09", "value": "T09"},
                {"name": "T08", "value": "T08"}
            ],
        },
    ],
)(list_old_stats)

# ACTIVE ALTS command
@client.command(
    name="active-alts",
    description="Add or remove a name from the active alts list and display the updated list.",
    options=[
        {
            "name": "name",
            "description": "Name of the alt to add or remove (accepts spaces).",
            "type": 3,  # STRING type
            "required": True,
        },
        {
            "name": "action",
            "description": "Action to perform (Add or Remove).",
            "type": 3,  # STRING type
            "required": True,
            "choices": [
                {"name": "Add", "value": "Add"},
                {"name": "Remove", "value": "Remove"}
            ],
        }
    ]
)(active_alts)

# REMOVE PLAYER command
@client.command(
    name="remove-player",
    description="Remove a player from the specified stat sheet.",
    options=[
        {
            "name": "name",
            "description": "The name of the player to be removed",
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
                {"name": "Attack 89", "value": "Attack 89"},
                {"name": "Defense 89", "value": "Defense 89"},
                {"name": "Dragon 89", "value": "Dragon 89"},
                {"name": "Attack 33", "value": "Attack 33"},
                {"name": "Defense 33", "value": "Defense 33"},
                {"name": "Dragon 33", "value": "Dragon 33"},
            ],
        },
        {
            "name": "editor_note",
            "description": "Optional note to append to the removal message",
            "type": 3,  # STRING type
            "required": False,
        },
    ],
)(remove_player)

# WARPLANS command
@client.command(
    name="warprep",
    description="List war plans for seat swaps or tier placement.",
    options=[
        {
            "name": "type",
            "description": "Select the type of war plan",
            "type": 3,  # STRING type
            "required": True,
            "choices": [
                {"name": "Seat Swaps", "value": "seat_swaps"},
                {"name": "Tier Placement", "value": "tier_placement"},
            ],
        },
        {
            "name": "clear_cache",
            "description": "Clear cache and fetch fresh data",
            "type": 5,  # BOOLEAN type
            "required": False,
        },
    ],
)(war_prep)

# Event listener for when the bot is ready
@client.event
async def on_ready():
    print(f'We have logged in as {client.me}')

client.start()