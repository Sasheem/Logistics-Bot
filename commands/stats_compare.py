# commands/stats_compare.py

from interactions import CommandContext
from rapidfuzz import process, fuzz
import math
from config.google_sheets import client_gs
from config.constants import WAR_SHEET_ID
from utils.fetch_player_info import fetch_player_info
from utils.fetch_data_with_cache import fetch_data_with_cache
from utils.string_utils import normalize_string

# use this
async def stats_compare(ctx: CommandContext, type: str, name1: str, name2: str, clear_cache: bool = False):
    await ctx.defer()  # Acknowledge the interaction to avoid "Unknown Interaction" error
    
    stats_types = {
        "attack": "player_stats",
        "defense": "player_defense_stats",
        "dragon-attack": "dragon_attack_stats",
        "dragon-defense": "dragon_defense_stats",
    }
    stats_type = stats_types.get(type)

    # Check if the same name is entered for both players
    if name1.strip().lower() == name2.strip().lower():
        await ctx.send("**Oops, this is embarrassing..**\n\nYou entered the same name for both players. Please enter different names and try again.")
        return

    # Normalize the input names
    normalized_name1 = normalize_string(name1)
    normalized_name2 = normalize_string(name2)

    # Fetch player info for both players
    player_info1 = fetch_player_info(client_gs, WAR_SHEET_ID, stats_type, normalized_name1, use_cache=not clear_cache)
    player_info2 = fetch_player_info(client_gs, WAR_SHEET_ID, stats_type, normalized_name2, use_cache=not clear_cache)

    # Soft match if no exact match found for player 1
    if not player_info1:
        soft_matches = process.extract(normalized_name1, [normalize_string(entry['Player Name']) for entry in fetch_data_with_cache(client_gs, WAR_SHEET_ID, stats_type, use_cache=not clear_cache)], scorer=fuzz.token_sort_ratio)

        best_match = soft_matches[0] if soft_matches else None
        if best_match and best_match[1] > 80:
            original_name1 = next(entry['Player Name'] for entry in fetch_data_with_cache(client_gs, WAR_SHEET_ID, stats_type, use_cache=not clear_cache) if normalize_string(entry['Player Name']) == best_match[0])
            player_info1 = fetch_player_info(client_gs, WAR_SHEET_ID, stats_type, original_name1, use_cache=not clear_cache)

    # Soft match if no exact match found for player 2
    if not player_info2:
        soft_matches = process.extract(normalized_name2, [normalize_string(entry['Player Name']) for entry in fetch_data_with_cache(client_gs, WAR_SHEET_ID, stats_type, use_cache=not clear_cache)], scorer=fuzz.token_sort_ratio)

        best_match = soft_matches[0] if soft_matches else None
        if best_match and best_match[1] > 80:
            original_name2 = next(entry['Player Name'] for entry in fetch_data_with_cache(client_gs, WAR_SHEET_ID, stats_type, use_cache=not clear_cache) if normalize_string(entry['Player Name']) == best_match[0])
            player_info2 = fetch_player_info(client_gs, WAR_SHEET_ID, stats_type, original_name2, use_cache=not clear_cache)


    if player_info1 and player_info2:
        title = f"{type.replace('-', ' ').title()} Stats Comparison"
        date1 = player_info1.get('Date', 'N/A')
        date2 = player_info2.get('Date', 'N/A')
        display_name1 = player_info1.get('Player Name', name1)
        display_name2 = player_info2.get('Player Name', name2)
        formatted_info = [f"# {title} \nPlayers: **{display_name1}** vs **{display_name2}**"]
        if type not in ["dragon-attack", "dragon-defense"]:
            formatted_info.append(f"Date: {date1} vs {date2}")

        if type in ["attack", "defense"]:
            base_section = False
            glam_section = False
            scoring_section = False
            ranking_section = False

            for key in player_info1.keys():
                if key in ['Date', 'Additional Details', 'Editor Notes', 'Player Name']:
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
                value1 = player_info1.get(key, 0)
                value2 = player_info2.get(key, 0)
                if value1 == 0 or value2 == 0:
                    continue
                if isinstance(value1, (int, float)) and math.isfinite(value1) and isinstance(value2, (int, float)) and math.isfinite(value2):
                    if "Rank" in key:
                        if value1 < value2:
                            formatted_value1 = f"**{round(value1):,}**"
                            formatted_value2 = f"{round(value2):,}"
                        else:
                            formatted_value1 = f"{round(value1):,}"
                            formatted_value2 = f"**{round(value2):,}**"
                    else:
                        if value1 > value2:
                            percentage_diff = round(((value1 - value2) / value2) * 100) if value2 != 0 else "N/A"
                            formatted_value1 = f"**{round(value1):,}**"
                            formatted_value2 = f"{round(value2):,} | {percentage_diff}%"
                        else:
                            percentage_diff = round(((value2 - value1) / value1) * 100) if value1 != 0 else "N/A"
                            formatted_value1 = f"{round(value1):,}"
                            formatted_value2 = f"**{round(value2):,}** | {percentage_diff}%"
                    formatted_info.append(f"{formatted_key}: {formatted_value1} vs {formatted_value2}")

            # Fetch average scores from the sheet
            avg_base1 = player_info1.get("Scoring Base", 0)
            avg_base2 = player_info2.get("Scoring Base", 0)
            avg_glam1 = player_info1.get("Scoring Glam", 0)
            avg_glam2 = player_info2.get("Scoring Glam", 0)
            avg_overall1 = player_info1.get("Scoring Overall", 0)
            avg_overall2 = player_info2.get("Scoring Overall", 0)

            # Determine winners
            base_winner = display_name1 if avg_base1 > avg_base2 else display_name2
            glam_winner = display_name1 if avg_glam1 > avg_glam2 else display_name2
            overall_winner = display_name1 if avg_overall1 > avg_overall2 else display_name2

            formatted_info.append("## Final Results")
            
            formatted_info.append(f"\nBase Winner: **{base_winner}**")
            formatted_info.append(f"Glam Winner: **{glam_winner}**")
            formatted_info.append(f"Overall Winner: **{overall_winner}**")

        elif type == "dragon-attack":
            attack1 = player_info1.get("Attack", 0)
            attack2 = player_info2.get("Attack", 0)
            if attack1 > attack2:
                percentage_diff = round(((attack1 - attack2) / attack2) * 100) if attack2 != 0 else float('inf')
                formatted_info.append(f"Attack Score: **{round(attack1):,}** vs {round(attack2):,} | {percentage_diff}%")
                overall_winner = display_name1
            else:
                percentage_diff = round(((attack2 - attack1) / attack1) * 100) if attack1 != 0 else float('inf')
                formatted_info.append(f"Attack Score: {round(attack1):,} vs **{round(attack2):,}** | {percentage_diff}%")
                overall_winner = display_name2

            formatted_info.append("## Final Results")
            formatted_info.append(f"\nOverall Winner: **{overall_winner}**")

        elif type == "dragon-defense":
            defense1 = player_info1.get("Defense", 0)
            health1 = player_info1.get("Health", 0)
            defense2 = player_info2.get("Defense", 0)
            health2 = player_info2.get("Health", 0)
            total1 = defense1 + health1
            total2 = defense2 + health2
            if total1 > total2:
                percentage_diff = round(((total1 - total2) / total2) * 100) if total2 != 0 else float('inf')
                formatted_info.append(f"Defense Score: **{round(total1):,}** vs {round(total2):,} | {percentage_diff}%")
                overall_winner = display_name1
            else:
                percentage_diff = round(((total2 - total1) / total1) * 100) if total1 != 0 else float('inf')
                formatted_info.append(f"Defense Score: {round(total1):,} vs **{round(total2):,}** | {percentage_diff}%")
                overall_winner = display_name2

            formatted_info.append("## Final Results")
            formatted_info.append(f"\nOverall Winner: **{overall_winner}**")

        await ctx.send("\n".join(formatted_info))
    else:
        missing_players = []
        if not player_info1:
            missing_players.append(name1)
        if not player_info2:
            missing_players.append(name2)
        await ctx.send(f"**Oops, this is embarrassing..**\n\nNo entries found for: **{', '.join(missing_players)}**.\nPlease check the spelling and try again.")