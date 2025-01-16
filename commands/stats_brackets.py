# commands/stats_brackets.py

import numpy as np
from interactions import CommandContext, Embed
from config.google_sheets import client_gs
from config.constants import WAR_SHEET_ID
from utils.fetch_data_with_cache import fetch_data_with_cache

async def stats_brackets(ctx: CommandContext, sheet: str, type: str, bracket: str, troop: str = "All", tier: str = "All", clear_cache: bool = False):
    await ctx.defer()  # Acknowledge the interaction to avoid "Unknown Interaction" error
    
    stats_types = {
        "attack": "player_stats",
        "defense": "player_defense_stats",
    }
    stats_type = stats_types.get(sheet)

    # Store original values of Troop and Tier
    original_troop = troop
    original_tier = tier

    # Fetch all player data
    all_players_info = fetch_data_with_cache(client_gs, WAR_SHEET_ID, stats_type, use_cache=not clear_cache)
    
    # Filter out empty entries and RCA values
    valid_players_info = [player for player in all_players_info if player.get('Player Name') and player.get('Tier') and player.get('Troop') and player.get('Troop') != "RCA"]
    
    # Calculate percentiles and assign ranks
    scoring_key = f"Scoring {type.capitalize()}"
    scoring_values = [float(player.get(scoring_key, 0)) for player in valid_players_info]
    percentiles = np.percentile(scoring_values, [25, 50, 75])
    for player in valid_players_info:
        score = float(player.get(scoring_key, 0))
        if score >= percentiles[2]:
            player['Percentile Rank'] = 1
        elif score >= percentiles[1]:
            player['Percentile Rank'] = 2
        elif score >= percentiles[0]:
            player['Percentile Rank'] = 3
        else:
            player['Percentile Rank'] = 4
    
    # Filter by bracket
    if bracket != "All":
        valid_players_info = [player for player in valid_players_info if player.get('Percentile Rank') == int(bracket)]
    
    # Filter by type (Base or Glam)
    type_key = f"({type.capitalize()})"
    filtered_players_info = []
    for player in valid_players_info:
        filtered_player = {key: (round(float(value)) if type_key in key else value) for key, value in player.items() if type_key in key or key in ['Player Name', 'Tier', 'Troop', 'Date', scoring_key]}
        filtered_players_info.append(filtered_player)

     # Additional filters for Troop and Tier (case-insensitive for Troop)
    if troop == "inf":
        non_inf_players = [player for player in filtered_players_info if isinstance(player.get('Troop'), str) and player.get('Troop').lower() in ["ranged", "cav"]]
        inf_players = [player for player in filtered_players_info if player not in non_inf_players]
        filtered_players_info = inf_players
    elif troop != "All":
        filtered_players_info = [player for player in filtered_players_info if isinstance(player.get('Troop'), str) and player.get('Troop').lower() == troop.lower()]
    
    if tier != "All":
        filtered_players_info = [player for player in filtered_players_info if player.get('Tier') == tier]
    
    # Sort the list by the scoring value in descending order
    filtered_players_info.sort(key=lambda x: float(x.get(scoring_key, 0)), reverse=True)
    
    # Format the output
    formatted_info = []
    for player in filtered_players_info:
        date = player.get('Date', 'N/A')
        name = player.get('Player Name', 'N/A')
        troop = player.get('Troop', 'N/A')
        tier = player.get('Tier', 'N/A')
        
        if sheet == "attack":
            attack = player.get(f'Attack {type_key}', 'N/A')
            marcher_attack = player.get(f'Marcher Attack SOP {type_key}', 'N/A')
            att_vs_inf = player.get(f'Att vs Inf {type_key}', 'N/A')
            att_vs_ranged = player.get(f'Att vs Ranged {type_key}', 'N/A')
            att_vs_cav = player.get(f'Att vs Cav {type_key}', 'N/A')
            formatted_info.append(f"{date}\n{name} | {troop} | {tier}\n{attack} | {marcher_attack}\n{att_vs_inf} | {att_vs_ranged} | {att_vs_cav}\n{'-' * 28}")
        else:
            defense = player.get(f'Defense {type_key}', 'N/A')
            defense_vs_sop = player.get(f'Defense vs Player at SoP {type_key}', 'N/A')
            def_vs_inf = player.get(f'Def vs Inf {type_key}', 'N/A')
            def_vs_ranged = player.get(f'Def vs Ranged {type_key}', 'N/A')
            def_vs_cav = player.get(f'Def vs Cav {type_key}', 'N/A')
            health = player.get(f'Health {type_key}', 'N/A')
            health_vs_sop = player.get(f'Health vs Player at SoP {type_key}', 'N/A')
            defender_defense = player.get(f'Defender Defense {type_key}', 'N/A')
            defender_health = player.get(f'Defender Health {type_key}', 'N/A')
            formatted_info.append(f"{date}\n{name} | {troop} | {tier}\n{defense} | {defense_vs_sop}\n{def_vs_inf} | {def_vs_ranged} | {def_vs_cav}\n{health} | {health_vs_sop}\n{defender_defense} | {defender_health}\n{'-' * 28}")
    
    # Add the total number of players at the bottom
    total_players = len(filtered_players_info)
    formatted_info.append(f"**Total Players:** {total_players}")

    # Add subtitle with options selected
    subtitle = f"\nStats - {sheet.capitalize()} \nType - {type.capitalize()} \nBracket - {bracket} \nTroop - {original_troop} \nTier - {original_tier}"
    formatted_info.append(subtitle)

    # Debug statement to check subtitle values
    print(f"Debug: Subtitle - {subtitle}")

    # Split the formatted_info into chunks if it exceeds the Discord limit
    chunks = []
    chunk = ""
    for info in formatted_info:
        if len(chunk) + len(info) + 1 > 4000:
            chunks.append(chunk)
            chunk = info
        else:
            chunk += "\n" + info
    if chunk:
        chunks.append(chunk)

    embeds = []
    for chunk in chunks:
        embed = Embed(
            title=f"{sheet.capitalize()} Stats Brackets ({type.capitalize()})",
            description=chunk,
            color=0x212121  # Black Charcoal color
        )
        embeds.append(embed)

    for embed in embeds:
        await ctx.send(embeds=[embed])
