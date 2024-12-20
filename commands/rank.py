# commands/stats_power.py

from interactions import CommandContext
from rapidfuzz import process, fuzz
import math
from config.google_sheets import client_gs
from config.constants import WAR_SHEET_ID
from utils.fetch_player_info import fetch_player_info
from utils.fetch_data_with_cache import fetch_data_with_cache

async def rank(ctx: CommandContext, type: str, name: str, clear_cache: bool = False):
    await ctx.defer()  # Acknowledge the interaction to avoid "Unknown Interaction" error
    rank_types = {
        "attack": "player_rank",
        "defense": "player_defense_rank",
        "dragon-attack": "dragon_attack_rank",
        "dragon-defense": "dragon_defense_rank",
    }
    
    if type == "dragon":
        attack_info = fetch_player_info(client_gs, WAR_SHEET_ID, "dragon_attack_rank", name.strip(), use_cache=not clear_cache)
        defense_info = fetch_player_info(client_gs, WAR_SHEET_ID, "dragon_defense_rank", name.strip(), use_cache=not clear_cache)
        
        # Soft match if no exact match found
        if not attack_info and not defense_info:
            soft_matches_attack = process.extract(name, [entry['Player Name'] for entry in fetch_data_with_cache(client_gs, WAR_SHEET_ID, "dragon_attack_rank", use_cache=not clear_cache)], scorer=fuzz.token_sort_ratio)
            soft_matches_defense = process.extract(name, [entry['Player Name'] for entry in fetch_data_with_cache(client_gs, WAR_SHEET_ID, "dragon_defense_rank", use_cache=not clear_cache)], scorer=fuzz.token_sort_ratio)
            best_match_attack = soft_matches_attack[0] if soft_matches_attack else None
            best_match_defense = soft_matches_defense[0] if soft_matches_defense else None
            if best_match_attack and best_match_attack[1] > 70:
                attack_info = fetch_player_info(client_gs, WAR_SHEET_ID, "dragon_attack_rank", best_match_attack[0], use_cache=not clear_cache)
            if best_match_defense and best_match_defense[1] > 70:
                defense_info = fetch_player_info(client_gs, WAR_SHEET_ID, "dragon_defense_rank", best_match_defense[0], use_cache=not clear_cache)
        
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
        player_info = fetch_player_info(client_gs, WAR_SHEET_ID, rank_type, name.strip(), use_cache=not clear_cache)
        
        # Soft match if no exact match found
        if not player_info:
            soft_matches = process.extract(name, [entry['Player Name'] for entry in fetch_data_with_cache(client_gs, WAR_SHEET_ID, rank_type, use_cache=not clear_cache)], scorer=fuzz.token_sort_ratio)
            best_match = soft_matches[0] if soft_matches else None
            if best_match and best_match[1] > 70:
                player_info = fetch_player_info(client_gs, WAR_SHEET_ID, rank_type, best_match[0], use_cache=not clear_cache)
        
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