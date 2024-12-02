import discord
from discord.ext import commands
from interactions import Client, CommandContext
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import math
import os 
from dotenv import load_dotenv

load_dotenv()

# Discord bot token
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

# Google Sheet ID
WAR_SHEET_ID = os.getenv('WAR_SHEET_ID')
ATTACK_SHEET_ID = os.getenv('ATTACK_SHEET_ID')
DEFENSE_SHEET_ID = os.getenv('DEFENSE_SHEET_ID')
DRAGON_SHEET_ID = os.getenv('DRAGON_SHEET_ID')
credentials_path = os.getenv('GOOGLE_SHEETS_CREDENTIALS_PATH')

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
bot = commands.Bot(command_prefix="!", intents=intents)
client = Client(token=DISCORD_TOKEN)

# Google Sheets setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
client_gs = gspread.authorize(creds)

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

def get_hierarchy_info_from_sheet(sheet, player_name, team_name):
    data = sheet.get_all_records()
    hierarchy = {"Team": team_name, "T1": None, "T2": None, "T3": None, "T4": None}
    current_t1 = current_t2 = current_t3 = None
    player_name = player_name.strip()  # Remove leading and trailing spaces

    for row in data:
        position = row[f'Position {team_name}']
        name = row[f'Name {team_name}']
        if position == "T1":
            current_t1 = name
            current_t2 = current_t3 = None  # Reset T2 and T3 when a new T1 is found
        elif position == "T2":
            current_t2 = name
            current_t3 = None  # Reset T3 when a new T2 is found
        elif position == "T3":
            current_t3 = name
        if isinstance(name, str) and name.strip().lower() == player_name.lower():  # Case-insensitive comparison
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
        sheet = client_gs.open_by_key(spreadsheet_id).worksheet(sheet_name)
        hierarchy_info = get_hierarchy_info_from_sheet(sheet, player_name, sheet_name)
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
    hierarchy_info = get_hierarchy_info(spreadsheet_id, name)
    if hierarchy_info["T1"]:
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
        await ctx.send(f"Player {name} not found in the roster.")

# Combined STATS command
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
    if player_info:
        title = f"{type.replace('-', ' ').title()} Stats"
        formatted_info = []
        base_section = False
        glam_section = False
        for key, value in player_info.items():
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
        await ctx.send(f"# {title}:\n" + "\n".join(formatted_info))
    else:
        await ctx.send("Player not found.")

# Combined RANK command
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
        
        title = f"Dragon Ranks: {name}"
        formatted_info = [f"## {title}"]
        
        if attack_info or defense_info:
            troop = attack_info.get("Troop", "N/A") if attack_info else defense_info.get("Troop", "N/A")
            dragon_level = attack_info.get("Dragon Level", "N/A") if attack_info else defense_info.get("Dragon Level", "N/A")
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
        if player_info:
            title = f"{type.replace('-', ' ').title()} Ranks: {name}"
            formatted_info = [f"## {title}"]
            
            troop = player_info.get("Troop", "N/A")
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
            await ctx.send("Player not found.")

# Combined LIST RANKS command for attack and defense
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

# Separate LIST DRAGON RANKS command
@client.command(
    name="list-dragon-ranks",
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
async def list_dragon_ranks(ctx: CommandContext, type: str, limit: int = None):
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
        for entry in name_changes_list:
            date = entry['Date']
            old_name = entry['Old Name']
            new_name = entry['New Name']
            formatted_info += f"{date}\n{old_name:<20} {new_name:<20}\n" + "-" * 30 + "\n"
        formatted_info += "```"
        await ctx.send(formatted_info)
    else:
        await ctx.send("No recent name changes found.")

# ROSTER-STATS command
@client.command(
    name="roster-stats",
    description="Fetch the stats for a specific team and category.",
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
async def roster_stats(ctx: CommandContext, team: str, category: str, defense_type: str = None):
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
    player_entries = [entry for entry in player_stats_list if entry['Player'].lower() == player_name.lower()]

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
        await ctx.send("Player not found.")

client.start()