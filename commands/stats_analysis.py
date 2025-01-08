from interactions import CommandContext
from rapidfuzz import process, fuzz
import math
import numpy as np
from config.google_sheets import client_gs
from config.constants import WAR_SHEET_ID
from utils.fetch_player_info import fetch_player_info
from utils.fetch_data_with_cache import fetch_data_with_cache
from utils.string_utils import normalize_string

async def stats_analysis(ctx: CommandContext, type: str, tier: str, troop: str, name: str, percentile: str = "All", clear_cache: bool = False):
    await ctx.defer()  # Acknowledge the interaction to avoid "Unknown Interaction" error
    
    stats_types = {
        "attack": "player_stats",
        "defense": "player_defense_stats",
    }
    stats_type = stats_types.get(type)

    # Normalize the input name
    normalized_name = normalize_string(name)

    # Fetch player info
    player_info = fetch_player_info(client_gs, WAR_SHEET_ID, stats_type, normalized_name, use_cache=not clear_cache)

    # Soft match if no exact match found
    if not player_info:
        soft_matches = process.extract(normalized_name, [normalize_string(entry['Player Name']) for entry in fetch_data_with_cache(client_gs, WAR_SHEET_ID, stats_type, use_cache=not clear_cache)], scorer=fuzz.ratio)

        best_match = soft_matches[0] if soft_matches else None
        if best_match and best_match[1] > 80:
            original_name = next(entry['Player Name'] for entry in fetch_data_with_cache(client_gs, WAR_SHEET_ID, stats_type, use_cache=not clear_cache) if normalize_string(entry['Player Name']) == best_match[0])
            player_info = fetch_player_info(client_gs, WAR_SHEET_ID, stats_type, original_name, use_cache=not clear_cache)

    if player_info:
        title = f"{type.replace('-', ' ').title()} Stats Analysis"
        percentile_labels = {
            "1": "Top 25%",
            "2": "Top 26% to 50%",
            "3": "Top 51% to 75%",
            "4": "Bottom 25%"
        }
        percentile_label = percentile_labels.get(percentile, "All Percentiles")
        subtitle = f"**{name}** vs {tier} {troop} Players\nCompared against: {percentile_label}" if tier != "All" and troop != "All" else f"{name} vs All Tier / All Troop Players\n{percentile_label}"
        date = player_info.get('Date', 'N/A')
        formatted_info = [f"# {title} \n{subtitle}\n"]

        # Fetch all player data to calculate averages
        all_players_info = fetch_data_with_cache(client_gs, WAR_SHEET_ID, stats_type, use_cache=not clear_cache)
        
        # Filter out empty entries and RCA values
        valid_players_info = [player for player in all_players_info if player.get('Player Name') and player.get('Tier') and player.get('Troop') and player.get('Troop') != "RCA"]
        
        # Calculate percentiles and assign ranks
        scoring_overall_values = [float(player.get('Scoring Overall', 0)) for player in valid_players_info]
        percentiles = np.percentile(scoring_overall_values, [25, 50, 75])
        for player in valid_players_info:
            score = float(player.get('Scoring Overall', 0))
            if score >= percentiles[2]:
                player['Percentile Rank'] = 1
            elif score >= percentiles[1]:
                player['Percentile Rank'] = 2
            elif score >= percentiles[0]:
                player['Percentile Rank'] = 3
            else:
                player['Percentile Rank'] = 4
        
        # Filter by percentile rank
        if percentile != "All":
            valid_players_info = [player for player in valid_players_info if player.get('Percentile Rank') == int(percentile)]
        
        # Filter by tier
        if tier != "All":
            valid_players_info = [player for player in valid_players_info if player.get('Tier') == tier]
        
        # Filter by troop
        if troop == "Ranged":
            valid_players_info = [player for player in valid_players_info if player.get('Troop') == "Ranged"]
        elif troop == "Cav":
            valid_players_info = [player for player in valid_players_info if player.get('Troop') == "Cav"]
        elif troop == "inf":
            valid_players_info = [player for player in valid_players_info if player.get('Troop') not in ["Ranged", "Cav"]]
        
        # Debug statement to check the fetched data
        # print(f"Valid players info after filtering by troop: {valid_players_info}")
        # for player in valid_players_info:
        #     print(f"Player: {player['Player Name']}, Troop: {player.get('Troop', 'N/A')}")

        averages = {}
        count = len(valid_players_info)

        for key in player_info.keys():
            if key in ['Date', 'Additional Details', 'Editor Notes', 'Player Name', 'Tier', 'Troop', 'Scoring Base', 'Scoring Glam', 'Scoring Overall', 'Ranking Base Rank', 'Ranking Glam Rank', 'Ranking Overall Rank']:
                continue
            total = sum(float(player.get(key, 0)) for player in valid_players_info if player.get(key, 0) != 0)
            averages[key] = total / count if count != 0 else 0

        # Display player info and comparison with averages
        formatted_info.append(f"Date: {date}")
        formatted_info.append(f"Tier: {player_info.get('Tier', 'N/A')}")
        formatted_info.append(f"Troop: {player_info.get('Troop', 'N/A')}")

        base_section = False
        glam_section = False
        total_attack_multipliers_section = False

        for key in player_info.keys():
            if key in ['Date', 'Additional Details', 'Editor Notes', 'Player Name', 'Tier', 'Troop', 'Scoring Base', 'Scoring Glam', 'Scoring Overall', 'Ranking Base Rank', 'Ranking Glam Rank', 'Ranking Overall Rank']:
                continue
            if "(Base)" in key and not base_section:
                formatted_info.append("## Base")
                base_section = True
                total_attack_multipliers_section = False
            if "(Glam)" in key and not glam_section:
                formatted_info.append("## Glam")
                glam_section = True
                total_attack_multipliers_section = False
            if "Total" in key and not total_attack_multipliers_section:
                formatted_info.append("**-- Total Power --**")
                total_attack_multipliers_section = True
            formatted_key = key.replace("(Base)", "").replace("(Glam)", "").replace("Total", "").strip()
            value = player_info.get(key, 0)
            avg_value = averages.get(key, 0)
            if value == 0 or avg_value == 0:
                continue
            if isinstance(value, (int, float)) and math.isfinite(value) and isinstance(avg_value, (int, float)) and math.isfinite(avg_value):
                if key == "Percentile Rank": 
                    continue
                percentage_diff = round(abs((value - avg_value) / avg_value) * 100) if avg_value != 0 else "N/A"
                if value > avg_value:
                    formatted_value = f"**{round(value):,}** vs {round(avg_value):,} | {percentage_diff}%"
                else:
                    formatted_value = f"{round(value):,} vs **{round(avg_value):,}** | {percentage_diff}%"
                formatted_info.append(f"{formatted_key}: {formatted_value}")

                # Add mini dividers below specified headers
                if formatted_key in ["Attack", "Att vs Cav", "Health", "Def vs Cav"]:
                    formatted_info.append("-----")

        await ctx.send("\n".join(formatted_info))
    else:
        await ctx.send(f"**Oops, this is embarrassing..**\n\nNo entries found for: **{name}**.\nPlease check the spelling and try again.")
