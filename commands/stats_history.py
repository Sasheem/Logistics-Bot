from interactions import CommandContext
from rapidfuzz import process, fuzz
import math
from config.google_sheets import client_gs
from config.constants import ATTACK_SHEET_ID, DEFENSE_SHEET_ID, DRAGON_SHEET_ID
from utils.fetch_data_with_cache import fetch_data_with_cache
from utils.string_utils import normalize_string

async def stats_history(ctx: CommandContext, player_name: str, category: str, limit: int = None, clear_cache: bool = False):
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

    player_stats_list = fetch_data_with_cache(client_gs, spreadsheet_id, tab_name, use_cache=not clear_cache)

    # Normalize the input name
    normalized_player_name = normalize_string(player_name)

    # Exact match
    player_entries = [entry for entry in player_stats_list if normalize_string(entry['Player']) == normalized_player_name]

    # Soft match if no exact match found
    if not player_entries:
        soft_matches = process.extract(normalized_player_name, [normalize_string(entry['Player']) for entry in player_stats_list], scorer=fuzz.ratio)
        best_match = soft_matches[0] if soft_matches else None
        if best_match and best_match[1] > 80:  # Threshold for a good match
            original_name = next(entry['Player'] for entry in player_stats_list if normalize_string(entry['Player']) == best_match[0])
            player_entries = [entry for entry in player_stats_list if entry['Player'] == original_name]

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
        await ctx.send(f"**Oops, this is embarrassing..**\n\nNo entries found for: **{player_name}**.\nPlease check the spelling and try again.")