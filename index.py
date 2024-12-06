import discord
from discord.ext import commands
from interactions import Client, CommandContext
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import math
import os 
from dotenv import load_dotenv
from fuzzywuzzy import fuzz, process
import time
import random
from gspread.exceptions import APIError

load_dotenv()

# Discord bot token
# DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
# Determine the environment
environment = os.getenv('ENVIRONMENT', 'live')

# Set the token based on the environment
if environment == 'test':
    TOKEN = os.getenv('DISCORD_TOKEN_TEST')
    credentials_path = os.getenv('GOOGLE_SHEETS_CREDENTIALS_PATH_TEST')
    # Normalize the credentials path 
    credentials_path = os.path.normpath(credentials_path)
else:
    TOKEN = os.getenv('DISCORD_TOKEN_LIVE')
    credentials_path = os.getenv('GOOGLE_SHEETS_CREDENTIALS_PATH_LIVE')

# Google Sheet ID
WAR_SHEET_ID = os.getenv('WAR_SHEET_ID')
ATTACK_SHEET_ID = os.getenv('ATTACK_SHEET_ID')
DEFENSE_SHEET_ID = os.getenv('DEFENSE_SHEET_ID')
DRAGON_SHEET_ID = os.getenv('DRAGON_SHEET_ID')
ROSTER_SHEET_ID = os.getenv('ROSTER_SHEET_ID')
RCA_SHEET_ID = os.getenv('RCA_SHEET_ID')

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
bot = commands.Bot(command_prefix="!", intents=intents)
client = Client(token=TOKEN)

# Google Sheets setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
client_gs = gspread.authorize(creds)

# Global cache
cache = {
    "data": {},
    "timestamp": 0
}

CACHE_DURATION = 300  # Cache duration in seconds (e.g., 5 minutes)

def fetch_data_with_cache(spreadsheet_id, sheet_name):
    current_time = time.time()
    if sheet_name not in cache["data"] or (current_time - cache["timestamp"]) > CACHE_DURATION:
        # Fetch new data from the API
        sheet = client_gs.open_by_key(spreadsheet_id).worksheet(sheet_name)
        cache["data"][sheet_name] = sheet.get_all_records()
        cache["timestamp"] = current_time
    return cache["data"][sheet_name]

# Function to get all players info from a Google Sheets tab
def get_all_players_info(spreadsheet_id, sheet_name):
    # sheet = client_gs.open('War Sheet - WTF').worksheet(sheet_name)
    sheet = client_gs.open_by_key(spreadsheet_id).worksheet(sheet_name)
    return sheet.get_all_records()

# Function to get player stats info based on stats type
def get_player_stats_info(spreadsheet_id, stats_type, player_name):
    sheet = client_gs.open_by_key(spreadsheet_id).worksheet(stats_type)
    data = sheet.get_all_records()
    player_name = player_name.strip()  # Remove leading and trailing spaces

    for row in data:
        if isinstance(row['Player Name'], str) and row['Player Name'].strip().lower() == player_name.lower():  # Case-insensitive comparison
            return row
    return None

# Function to get player rank info based on rank type
def get_player_rank_info(spreadsheet_id, rank_type, player_name):
    sheet = client_gs.open_by_key(spreadsheet_id).worksheet(rank_type)
    data = sheet.get_all_records()
    player_name = player_name.strip()  # Remove leading and trailing spaces

    for row in data:
        if isinstance(row['Player Name'], str) and row['Player Name'].strip().lower() == player_name.lower():  # Case-insensitive comparison
            return row
    return None

# Helper functions
def get_hierarchy_info_from_sheet(data, player_name, team_name):
    hierarchy = {"Team": team_name, "T1": None, "T2": None, "T3": None, "T4": None}
    current_t1 = current_t2 = current_t3 = None
    player_name = str(player_name).strip()  # Convert to string and remove leading and trailing spaces

    for row in data:
        position = row[f'Position {team_name}']
        name = str(row[f'Name {team_name}']).strip()  # Convert to string and remove leading and trailing spaces
        if position == "T1":
            current_t1 = name
            current_t2 = current_t3 = None  # Reset T2 and T3 when a new T1 is found
        elif position == "T2":
            current_t2 = name
            current_t3 = None  # Reset T3 when a new T2 is found
        elif position == "T3":
            current_t3 = name
        if name.lower() == player_name.lower():  # Case-insensitive comparison
            hierarchy["T1"] = current_t1
            hierarchy["T2"] = current_t2
            hierarchy["T3"] = current_t3
            hierarchy["T4"] = name
            if position == "T1":
                hierarchy["T2"] = hierarchy["T3"] = hierarchy["T4"] = None
            elif position == "T2":
                hierarchy["T3"] = hierarchy["T4"] = None
            elif position == "T3":
                hierarchy["T4"] = None
            return hierarchy  # Return immediately when the player is found

    return None  # Return None if the player is not found in this sheet

# Function to get hierarchy information for a player from multiple sheets
def get_hierarchy_info(spreadsheet_id, player_name):
    sheet_names = ['WHSKY', 'TANGO', 'FXTRT']  # List of sheet names
    for sheet_name in sheet_names:
        data = fetch_data_with_cache(spreadsheet_id, sheet_name)
        hierarchy_info = get_hierarchy_info_from_sheet(data, str(player_name), sheet_name)
        if hierarchy_info:
            return hierarchy_info  # Return the hierarchy info if the player is found

    return {"Team": None, "T1": None, "T2": None, "T3": None, "T4": None}  # Return empty hierarchy if the player is not found in any sheet

# Function to get recent name changes from Google Sheets
def get_recent_name_changes():
    sheet = client_gs.open_by_key(WAR_SHEET_ID).worksheet('recent_name_changes')
    data = sheet.get_all_records()
    return data

# Function to get team stats from Google Sheets
# TO BE CONVERTED TO THE FUNCTION BELOW
def get_sheet_records(spreadsheet_id, tab_name):
    sheet = client_gs.open_by_key(spreadsheet_id).worksheet(tab_name)
    data = sheet.get_all_records()
    return data

# Function to fetch sheet data from Google Sheets
def fetch_sheet_data(spreadsheet_id, tab_name):
    # sheet = client_gs.open(sheet_name).worksheet(tab_name)
    sheet = client_gs.open_by_key(spreadsheet_id).worksheet(tab_name);
    data = sheet.get_all_records()
    return data

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
)
async def team_overview(ctx: CommandContext, category: str):
    await ctx.defer()  # Acknowledge the interaction to avoid "Unknown Interaction" error

    tab_name = f"{category}_overview"
    team_data = fetch_sheet_data(WAR_SHEET_ID, tab_name)

    if team_data:
        title = f"{category.replace('_', ' ').title()} Overview"
        formatted_info = [f"# {title}"]
        
        for entry in team_data:
            formatted_info.append(f"## Total:  {entry['Submissions']}")
            formatted_info.append(f"**-- Troop Types --**")
            formatted_info.append(f"Infantry:  {entry['Infantry Totals']}")
            formatted_info.append(f"Cavalry:  {entry['Cavalry Totals']}")
            formatted_info.append(f"Range:  {entry['Range Totals']}")
            formatted_info.append(f"Siege:  {entry['Siege Totals']}")
            formatted_info.append(f"RCA:  {entry['RCA Totals']}")
            formatted_info.append(f"**-- Troop Tiers --**")
            formatted_info.append(f"T12s:  {entry['T12s Totals']}")
            formatted_info.append(f"T11s:  {entry['T11s Totals']}")
            formatted_info.append(f"T10s:  {entry['T10s Totals']}")
            formatted_info.append(f"T9s:  {entry['T9s Totals']}")
            formatted_info.append(f"T8s:  {entry['T8s Totals']}")
            
            if category in ["dragon_attack", "dragon_defense"]:
                formatted_info.append(f"**-- Dragon Levels --**")
                formatted_info.append(f"Lvl 69:  {entry['Lvl 69 Totals']}")
                formatted_info.append(f"Lvl 65+:  {entry['Lvl 65+ Totals']}")
                
            if category in ["dragon_attack"]:
                formatted_info.append(f"Lvl 41+:  {entry['Lvl 41+ Totals']}")
            
            formatted_info.append("\n")

        await ctx.send("\n".join(formatted_info))
    else:
        await ctx.send("No data found for the specified category.")

# HIERARCHY command
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
)
async def roster_position(ctx: CommandContext, name: str):
    await ctx.defer()  # Defer the interaction to give more time
    spreadsheet_id = WAR_SHEET_ID
    sheet_names = ['WHSKY', 'TANGO', 'FXTRT']
    hierarchy_info = get_hierarchy_info(spreadsheet_id, str(name).strip())  # Convert to string and remove leading and trailing spaces

    # Soft match if no exact match found
    if not hierarchy_info or not hierarchy_info["T1"]:
        sheet_names = ['WHSKY', 'TANGO', 'FXTRT']
        for sheet_name in sheet_names:
            data = fetch_data_with_cache(spreadsheet_id, sheet_name)
            soft_matches = process.extract(str(name), [str(entry[f'Name {sheet_name}']) for entry in data], scorer=fuzz.token_sort_ratio)
            best_match = soft_matches[0] if soft_matches else None
            if best_match and best_match[1] > 70:
                hierarchy_info = get_hierarchy_info(spreadsheet_id, best_match[0])
                break

    if hierarchy_info and hierarchy_info["T1"]:
        response = f"**Roster Position for {name}:**\n"
        if hierarchy_info["Team"]:
            response += f"Team: {hierarchy_info['Team']}\n"
        if hierarchy_info["T1"]:
            response += f"T1: {hierarchy_info['T1']}\n"
        if hierarchy_info["T2"]:
            response += f"T2: {hierarchy_info['T2']}\n"
        if hierarchy_info["T3"]:
            response += f"T3: {hierarchy_info['T3']}\n"
        if hierarchy_info["T4"]:
            response += f"T4: {hierarchy_info['T4']}\n"
        try:
            await ctx.send(response)
        except Exception as e:
            print(f"Error sending response: {e}")
            await ctx.send(f"An error occurred while sending the response for {name}. Please try again.")
    else:
        await ctx.send(f"## Oops, this is embarrassing..\n\nPlayer not found: **{name}**.\nPlease check the spelling and try again.")

# STATS command
@client.command(
    name="stats",
    description="Find a player's most recent stats submitted for different categories.",
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
)
async def stats(ctx: CommandContext, type: str, name: str):
    await ctx.defer()  # Acknowledge the interaction to avoid "Unknown Interaction" error
    stats_types = {
        "attack": "player_stats",
        "defense": "player_defense_stats",
        "dragon-attack": "dragon_attack_stats",
        "dragon-defense": "dragon_defense_stats",
    }
    stats_type = stats_types.get(type)
    player_info = get_player_stats_info(WAR_SHEET_ID, stats_type, name.strip())  # Remove leading and trailing spaces

    # Soft match if no exact match found
    if not player_info:
        soft_matches = process.extract(name, [entry['Player Name'] for entry in fetch_sheet_data(WAR_SHEET_ID, stats_type)], scorer=fuzz.token_sort_ratio)
        best_match = soft_matches[0] if soft_matches else None
        if best_match and best_match[1] > 70:
            player_info = get_player_stats_info(WAR_SHEET_ID, stats_type, best_match[0])

    if player_info:
        title = f"{type.replace('-', ' ').title()} Stats"
        date = player_info.get('Date', 'N/A')
        formatted_info = [f"# {title}\nDate: {date}"]
        base_section = False
        glam_section = False
        for key, value in player_info.items():
            if key in ['Date', 'Additional Details', 'Editor Notes']:
                continue
            if "(Base)" in key and not base_section:
                formatted_info.append("## Base")
                base_section = True
            if "(Glam)" in key and not glam_section:
                formatted_info.append("## Glam")
                glam_section = True
            formatted_key = key.replace("(Base)", "").replace("(Glam)", "").strip()
            if formatted_key.startswith("Total"):
                formatted_value = f"**{round(value):,}**" if isinstance(value, (int, float)) and math.isfinite(value) else f"**{value}**"
            else:
                formatted_value = f"{round(value):,}" if isinstance(value, (int, float)) and math.isfinite(value) else f"{value}"
            formatted_info.append(f"{formatted_key}: {formatted_value}")
        await ctx.send("\n".join(formatted_info))
    else:
        await ctx.send(f"## Oops, this is embarrassing..\n\nNo entries found for: **{name}**.\nPlease check the spelling and try again.")

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
)
async def rank(ctx: CommandContext, type: str, name: str):
    await ctx.defer()  # Acknowledge the interaction to avoid "Unknown Interaction" error
    rank_types = {
        "attack": "player_rank",
        "defense": "player_defense_rank",
        "dragon-attack": "dragon_attack_rank",
        "dragon-defense": "dragon_defense_rank",
    }
    
    if type == "dragon":
        attack_info = get_player_rank_info(WAR_SHEET_ID, "dragon_attack_rank", name.strip())
        defense_info = get_player_rank_info(WAR_SHEET_ID, "dragon_defense_rank", name.strip())
        
        # Soft match if no exact match found
        if not attack_info and not defense_info:
            soft_matches_attack = process.extract(name, [entry['Player Name'] for entry in fetch_sheet_data(WAR_SHEET_ID, "dragon_attack_rank")], scorer=fuzz.token_sort_ratio)
            soft_matches_defense = process.extract(name, [entry['Player Name'] for entry in fetch_sheet_data(WAR_SHEET_ID, "dragon_defense_rank")], scorer=fuzz.token_sort_ratio)
            best_match_attack = soft_matches_attack[0] if soft_matches_attack else None
            best_match_defense = soft_matches_defense[0] if soft_matches_defense else None
            if best_match_attack and best_match_attack[1] > 70:
                attack_info = get_player_rank_info(WAR_SHEET_ID, "dragon_attack_rank", best_match_attack[0])
            if best_match_defense and best_match_defense[1] > 70:
                defense_info = get_player_rank_info(WAR_SHEET_ID, "dragon_defense_rank", best_match_defense[0])
        
        title = f"Dragon Ranks: {name}"
        formatted_info = [f"## {title}"]
        
        if attack_info or defense_info:
            player_name = attack_info.get("Player Name", "N/A") if attack_info else defense_info.get("Player Name", "N/A")
            troop = attack_info.get("Troop", "N/A") if attack_info else defense_info.get("Troop", "N/A")
            dragon_level = attack_info.get("Dragon Level", "N/A") if attack_info else defense_info.get("Dragon Level", "N/A")
            formatted_info.append(f"Player Name: {player_name}")
            formatted_info.append(f"Troop: {troop}")
            formatted_info.append(f"Dragon Level: {dragon_level}")
        
        if attack_info:
            formatted_info.append("**-- Dragon Attack --**")
            formatted_info.extend([
                f"{key}: {math.ceil(value):,}" if isinstance(value, (int, float)) and abs(value) >= 1000 and math.isfinite(value) else f"{key}: {value}"
                for key, value in attack_info.items() if key not in ["Player Name", "Troop", "Dragon Level"]
            ])
        else:
            formatted_info.append("**-- Dragon Attack --**\nNo attack rankings found")
        
        if defense_info:
            formatted_info.append("**-- Dragon Defense --**")
            formatted_info.extend([
                f"{key}: {math.ceil(value):,}" if isinstance(value, (int, float)) and abs(value) >= 1000 and math.isfinite(value) else f"{key}: {value}"
                for key, value in defense_info.items() if key not in ["Player Name", "Troop", "Dragon Level"]
            ])
        else:
            formatted_info.append("**-- Dragon Defense --**\nNo defense rankings found")
        
        await ctx.send("\n".join(formatted_info))
    else:
        rank_type = rank_types.get(type)
        player_info = get_player_rank_info(WAR_SHEET_ID, rank_type, name.strip())  # Remove leading and trailing spaces
        
        # Soft match if no exact match found
        if not player_info:
            soft_matches = process.extract(name, [entry['Player Name'] for entry in fetch_sheet_data(WAR_SHEET_ID, rank_type)], scorer=fuzz.token_sort_ratio)
            best_match = soft_matches[0] if soft_matches else None
            if best_match and best_match[1] > 70:
                player_info = get_player_rank_info(WAR_SHEET_ID, rank_type, best_match[0])
        
        if player_info:
            title = f"{type.replace('-', ' ').title()} Ranks: {name}"
            formatted_info = [f"## {title}"]
            
            player_name = player_info.get("Player Name", "N/A")
            troop = player_info.get("Troop", "N/A")
            formatted_info.append(f"Player Name: {player_name}")
            formatted_info.append(f"Troop: {troop}")
            
            base_info = [f"{key.replace('Base', '').strip()}: {math.ceil(value):,}" if isinstance(value, (int, float)) and abs(value) >= 1000 and math.isfinite(value) else f"{key.replace('Base', '').strip()}: {value}" for key, value in player_info.items() if "Base" in key]
            glam_info = [f"{key.replace('Glam', '').strip()}: {math.ceil(value):,}" if isinstance(value, (int, float)) and abs(value) >= 1000 and math.isfinite(value) else f"{key.replace('Glam', '').strip()}: {value}" for key, value in player_info.items() if "Glam" in key]
            team_info = [f"{key.replace('Team', '').strip()}: {math.ceil(value):,}" if isinstance(value, (int, float)) and abs(value) >= 1000 and math.isfinite(value) else f"{key.replace('Team', '').strip()}: {value}" for key, value in player_info.items() if "Team" in key]
            
            formatted_info.append("**-- Base --**")
            if base_info:
                formatted_info.extend(base_info)
            else:
                formatted_info.append("No rankings found")
            
            formatted_info.append("**-- Glam --**")
            if glam_info:
                formatted_info.extend(glam_info)
            else:
                formatted_info.append("No rankings found")
            
            formatted_info.append("**-- Team --**")
            if team_info:
                formatted_info.extend(team_info)
            else:
                formatted_info.append("No rankings found")
            
            await ctx.send("\n".join(formatted_info))
        else:
            await ctx.send(f"## Oops, this is embarrassing..\n\nNo entries found for: **{name}**.\nPlease check the spelling and try again.")

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
    players_info = get_all_players_info(WAR_SHEET_ID, rank_type)
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
    players_info = get_all_players_info(WAR_SHEET_ID, rank_type)
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
    name_changes_list = get_recent_name_changes()
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
    team_stats_list = get_sheet_records(WAR_SHEET_ID, tab_name)
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

    player_stats_list = fetch_sheet_data(spreadsheet_id, tab_name)
    
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
    keeps_list = fetch_sheet_data(ROSTER_SHEET_ID, "bot_keep_logistics")

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
    rca_list = fetch_sheet_data(RCA_SHEET_ID, "bot_rca_info")
    
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
    rca_logs_list = fetch_sheet_data(RCA_SHEET_ID, "bot_rca_info")
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