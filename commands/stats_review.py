from interactions import CommandContext, Embed
from config.google_sheets import client_gs
from config.constants import ATTACK_SHEET_ID, DEFENSE_SHEET_ID, DRAGON_SHEET_ID
from utils.fetch_data_with_cache import fetch_data_with_cache, clear_cache
from datetime import datetime, timedelta

async def stats_review(ctx: CommandContext, type: str, filter_by: str):
    await ctx.defer()  # Acknowledge the interaction to avoid "Unknown Interaction" error

    # Determine the sheet ID, color, and emoji based on the type
    if type == "attack":
        sheet_id = ATTACK_SHEET_ID
        color = 0xFF4500  # Orange red color
        emoji = "⚔️"
    elif type == "defense":
        sheet_id = DEFENSE_SHEET_ID
        color = 0x6A0DAD  # Purple blue color
        emoji = "🛡️"
    elif type == "dragon":
        sheet_id = DRAGON_SHEET_ID
        color = 0x9ACD32  # Yellow green color
        emoji = "🐉"
    else:
        await ctx.send("Invalid type specified.")
        return

    # Clear the cache before fetching new data
    clear_cache("stats_review")

    sheet_data = fetch_data_with_cache(client_gs, sheet_id, "stats_review")
    
    if not sheet_data:
        await ctx.send("No data found.")
        return

    filtered_data = []
    current_date = datetime.now()

    if filter_by == "New":
        filtered_data = [entry for entry in sheet_data if entry.get('Notes') == '0' or entry.get('Notes') == 0]
    elif filter_by == "Duplicates":
        name_counts = {}
        for entry in sheet_data:
            name = entry.get('Name')
            if name:
                name_counts[name] = name_counts.get(name, 0) + 1
        filtered_data = [entry for entry in sheet_data if name_counts.get(entry.get('Name')) > 1]
    elif filter_by == "Last Week":
        last_week = current_date - timedelta(weeks=1)
        filtered_data = [entry for entry in sheet_data if datetime.strptime(entry.get('Date'), '%Y-%m-%d') >= last_week]
    elif filter_by == "Last Month":
        last_month = current_date - timedelta(days=30)
        filtered_data = [entry for entry in sheet_data if datetime.strptime(entry.get('Date'), '%Y-%m-%d') >= last_month]
    elif filter_by == "Over a month":
        over_a_month = current_date - timedelta(days=30)
        filtered_data = [entry for entry in sheet_data if datetime.strptime(entry.get('Date'), '%Y-%m-%d') < over_a_month]

    if not filtered_data:
        await ctx.send("No matching data found.")
        return

    number_of_entries = len(filtered_data)
    description = f"\n{number_of_entries} {type} submission(s)\nFiltered by: {filter_by}\n\n"

    formatted_info = ""
    for entry in filtered_data:
        date = entry.get('Date', 'n/a')
        old_team = entry.get('Old Team', 'n/a')
        name = entry.get('Name', 'n/a')
        tier = entry.get('Tier', 'n/a')
        troop = entry.get('Troop', 'n/a')
        drag = entry.get('Drag Lvl', 'n/a')
        notes = entry.get('Notes', 'n/a')
        stat_lines = entry.get('Stat Lines', 'n/a')
        
        entry_info = (
            f"{date}\n"
            f"**{name}** | {old_team}\n"
            f"{tier} | {troop} | {drag} \n"
        )
        
        if notes != '0' and notes != 0:
            entry_info += (
                f"**Editor Notes**\n"
                f"{notes}\n"
            )
        
        if stat_lines != '0' and stat_lines != 0:
            entry_info += (
                f"**Stat Lines**\n"
                f"{stat_lines}\n"
            )
        
        entry_info += "-" * 34 + "\n"
        
        if len(formatted_info) + len(entry_info) + 3 > 2000:  # 2000 is the Discord message limit
            embed = Embed(
                title=f"{type.capitalize()} Stats Review {emoji}",
                description=description + formatted_info,
                color=color
            )
            await ctx.send(embeds=[embed])
            formatted_info = entry_info
        else:
            formatted_info += entry_info
    
    if formatted_info:
        embed = Embed(
            title=f"{type.capitalize()} Stats Review {emoji}",
            description=description + formatted_info + description,
            color=color
        )
        await ctx.send(embeds=[embed])