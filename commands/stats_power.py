from interactions import CommandContext
from rapidfuzz import process, fuzz
import math
from config.google_sheets import client_gs
from config.constants import WAR_SHEET_ID
from utils.fetch_player_info import fetch_player_info
from utils.fetch_data_with_cache import fetch_data_with_cache
from utils.string_utils import normalize_string

async def stats_power(ctx: CommandContext, type: str, name: str, clear_cache: bool = False):
    await ctx.defer()  # Acknowledge the interaction to avoid "Unknown Interaction" error
    stats_types = {
        "attack": "player_stats",
        "defense": "player_defense_stats",
        "dragon": ["dragon_attack_stats", "dragon_defense_stats"]
    }
    stats_type = stats_types.get(type)
    
    # Normalize the input name
    normalized_name = normalize_string(name)

    if type == "dragon":
        player_info_attack = fetch_player_info(client_gs, WAR_SHEET_ID, "dragon_attack_stats", normalized_name, use_cache=not clear_cache)
        player_info_defense = fetch_player_info(client_gs, WAR_SHEET_ID, "dragon_defense_stats", normalized_name, use_cache=not clear_cache)
        player_info = player_info_attack or player_info_defense
    else:
        player_info = fetch_player_info(client_gs, WAR_SHEET_ID, stats_type, normalized_name, use_cache=not clear_cache)

    # Soft match if no exact match found
    if not player_info:
        if type == "dragon":
            soft_matches_attack = process.extract(normalized_name, [normalize_string(entry['Player Name']) for entry in fetch_data_with_cache(client_gs, WAR_SHEET_ID, "dragon_attack_stats", use_cache=not clear_cache)], scorer=fuzz.ratio)
            soft_matches_defense = process.extract(normalized_name, [normalize_string(entry['Player Name']) for entry in fetch_data_with_cache(client_gs, WAR_SHEET_ID, "dragon_defense_stats", use_cache=not clear_cache)], scorer=fuzz.ratio)
            best_match_attack = soft_matches_attack[0] if soft_matches_attack else None
            best_match_defense = soft_matches_defense[0] if soft_matches_defense else None
            if best_match_attack and best_match_attack[1] > 80:
                original_name_attack = next(entry['Player Name'] for entry in fetch_data_with_cache(client_gs, WAR_SHEET_ID, "dragon_attack_stats", use_cache=not clear_cache) if normalize_string(entry['Player Name']) == best_match_attack[0])
                player_info_attack = fetch_player_info(client_gs, WAR_SHEET_ID, "dragon_attack_stats", original_name_attack, use_cache=not clear_cache)
            if best_match_defense and best_match_defense[1] > 80:
                original_name_defense = next(entry['Player Name'] for entry in fetch_data_with_cache(client_gs, WAR_SHEET_ID, "dragon_defense_stats", use_cache=not clear_cache) if normalize_string(entry['Player Name']) == best_match_defense[0])
                player_info_defense = fetch_player_info(client_gs, WAR_SHEET_ID, "dragon_defense_stats", original_name_defense, use_cache=not clear_cache)
            player_info = player_info_attack or player_info_defense
        else:
            soft_matches = process.extract(normalized_name, [normalize_string(entry['Player Name']) for entry in fetch_data_with_cache(client_gs, WAR_SHEET_ID, stats_type, use_cache=not clear_cache)], scorer=fuzz.ratio)
            best_match = soft_matches[0] if soft_matches else None
            if best_match and best_match[1] > 80:
                original_name = next(entry['Player Name'] for entry in fetch_data_with_cache(client_gs, WAR_SHEET_ID, stats_type, use_cache=not clear_cache) if normalize_string(entry['Player Name']) == best_match[0])
                player_info = fetch_player_info(client_gs, WAR_SHEET_ID, stats_type, original_name, use_cache=not clear_cache)

    if player_info:
        title = f"{type.replace('-', ' ').title()} Stats"
        date = player_info.get('Date', 'N/A')
        formatted_info = [f"# {title}\nDate: {date}"]
        base_section = False
        glam_section = False
        scoring_section = False
        ranking_section = False

        if type == "dragon":
            player_name = player_info_attack.get("Player Name", "N/A") if player_info_attack else player_info_defense.get("Player Name", "N/A")
            troop = player_info_attack.get("Troop", "N/A") if player_info_attack else player_info_defense.get("Troop", "N/A")
            dragon_level = player_info_attack.get("Dragon Level", "N/A") if player_info_attack else player_info_defense.get("Dragon Level", "N/A")
            formatted_info.append(f"Player Name: {player_name}")
            formatted_info.append(f"Troop: {troop}")
            formatted_info.append(f"Dragon Level: {dragon_level}")

            formatted_info.append("## Dragon Attack")
            if player_info_attack:
                for key, value in player_info_attack.items():
                    if key in ['Date', 'Additional Details', 'Editor Notes', 'Player Name', 'Troop', 'Dragon Level']:
                        continue
                    formatted_key = key.replace("(Base)", "").replace("(Glam)", "").replace("Scoring", "").replace("Ranking", "").strip()
                    formatted_value = f"{round(value):,}" if isinstance(value, (int, float)) and math.isfinite(value) else f"{value}"
                    formatted_info.append(f"{formatted_key}: {formatted_value}")
            else:
                formatted_info.append("N/A")

            formatted_info.append("## Dragon Defense")
            if player_info_defense:
                for key, value in player_info_defense.items():
                    if key in ['Date', 'Additional Details', 'Editor Notes', 'Player Name', 'Troop', 'Dragon Level']:
                        continue
                    formatted_key = key.replace("(Base)", "").replace("(Glam)", "").replace("Scoring", "").replace("Ranking", "").strip()
                    formatted_value = f"{round(value):,}" if isinstance(value, (int, float)) and math.isfinite(value) else f"{value}"
                    formatted_info.append(f"{formatted_key}: {formatted_value}")
            else:
                formatted_info.append("N/A")
        else:
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
        await ctx.send(f"**Oops, this is embarrassing..**\n\nNo entries found for: **{name}**.\nPlease check the spelling and try again.")