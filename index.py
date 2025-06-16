from interactions import Client
import os 
from dotenv import load_dotenv

# Load the commands
from commands.roster_position import roster_position
from commands.roster_bannermen import roster_bannermen
from commands.clear_roster_cache import clear_roster_cache

load_dotenv()

# Determine the environment
environment = os.getenv('ENVIRONMENT', 'live')

# Set the tokens based on the environment
if environment == 'test':
    TOKEN = os.getenv('DISCORD_TOKEN_TEST')
else:
    TOKEN = os.getenv('DISCORD_TOKEN_LIVE')

# Token safety fallback
if not TOKEN:
    raise RuntimeError("No Discord token found for the selected environment.")

# Discord bot setup
client = Client(token=TOKEN)

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

# ROSTER-BANNERMEN command
@client.command(
    name="roster-bannermen",
    description="Fetch the banners for a specific player.",
    options=[
        {
            "name": "name",
            "description": "The player name to search for",
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
)(roster_bannermen)

# CLEAR-ROSTER-CACHE command
@client.command(
    name="clear-roster-cache",
    description="Clear cached roster for bot.",
)(clear_roster_cache)

# Event listener for when the bot is ready
@client.event
async def on_ready():
    print(f'We have logged in as {client.me}')
    print(f"Running bot in '{environment}' environment.")

client.start()