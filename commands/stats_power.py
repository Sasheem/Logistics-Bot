# commands/stats_power.py

from interactions import CommandContext
from rapidfuzz import process, fuzz
import math
from config.google_sheets import client_gs
from config.constants import WAR_SHEET_ID
from utils.fetch_player_info import fetch_player_info
from utils.fetch_data_with_cache import fetch_data_with_cache

async def stats_power(ctx: CommandContext, type: str, name: str, clear_cache: bool = False):
    await ctx.defer()  # Acknowledge the interaction to avoid "Unknown Interaction" error
    stats_types = {
        "attack": "player_stats",
        "defense": "player_defense_stats",
        "dragon-attack": "dragon_attack_stats",
        "dragon-defense": "dragon_defense_stats",
    }
    stats_type = stats_types.get(type)
    player_info = fetch_player_info(client_gs, WAR_SHEET_ID, stats_type, name.strip(), use_cache=not clear_cache)  # Remove leading and trailing spaces

    # Soft match if no exact match found
    if not player_info:
        soft_matches = process.extract(name, [entry['Player Name'] for entry in fetch_data_with_cache(client_gs, WAR_SHEET_ID, stats_type, use_cache=not clear_cache)], scorer=fuzz.token_sort_ratio)
        best_match = soft_matches[0] if soft_matches else None
        if best_match and best_match[1] > 70:
            player_info = fetch_player_info(client_gs, WAR_SHEET_ID, stats_type, best_match[0])

    if player_info:
        title = f"{type.replace('-', ' ').title()} Stats"
        date = player_info.get('Date', 'N/A')
        formatted_info = [f"# {title}\nDate: {date}"]
        base_section = False
        glam_section = False
        scoring_section = False
        ranking_section = False

        for key, value in player_info.items():
            if key in ['Date', 'Additional Details', 'Editor Notes']:
                continue
            if "(Base)" in key and not base_section:
                formatted_info.append("## Base")
                base_section = True
            if "(Glam)" in key and not glam_section:
                formatted_info.append("## Glam")
                glam_section = True
            if "Scoring" in key and not scoring_section:
                formatted_info.append("## Scoring")
                scoring_section = True
            if "Ranking" in key and not ranking_section:
                formatted_info.append("## Ranking")
                ranking_section = True
            formatted_key = key.replace("(Base)", "").replace("(Glam)", "").replace("Scoring", "").replace("Ranking", "").strip()
            if formatted_key.startswith("Total"):
                formatted_value = f"**{round(value):,}**" if isinstance(value, (int, float)) and math.isfinite(value) else f"**{value}**"
            else:
                formatted_value = f"{round(value):,}" if isinstance(value, (int, float)) and math.isfinite(value) else f"{value}"
            formatted_info.append(f"{formatted_key}: {formatted_value}")
        await ctx.send("\n".join(formatted_info))
    else:
        await ctx.send(f"## Oops, this is embarrassing..\n\nNo entries found for: **{name}**.\nPlease check the spelling and try again.")