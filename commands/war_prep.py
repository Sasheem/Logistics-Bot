# commands/war_prep.py

from interactions import CommandContext, Embed
from config.google_sheets import client_gs
from config.constants import WAR_DOCS_SHEET_ID
from utils.fetch_data_with_cache import fetch_data_with_cache
from utils.last_updated import last_updated

async def war_prep(ctx: CommandContext, type: str, clear_cache: bool = False):
    await ctx.defer()  # Acknowledge the interaction to avoid "Unknown Interaction" error

    warplan_types = {
        "seat_swaps": "bot_seat_swaps",
        "tier_placement": "bot_tier_placement",
    }
    warplan_type = warplan_types.get(type)
    warplan_info = fetch_data_with_cache(client_gs, WAR_DOCS_SHEET_ID, warplan_type, use_cache=not clear_cache)
    
    if warplan_info:
        title = f"{type.replace('_', ' ').title()} Plan"
        formatted_info = ""

        if type == "seat_swaps":
            for row in warplan_info:
                seat = row.get("Seat", "N/A")
                current_holder = row.get("Current Holder", "N/A")
                new_holder = row.get("New Holder", "N/A")
                status = row.get("Status", "N/A")
                formatted_info += f"**{seat}** ({status})\n{current_holder} > {new_holder}\n" + "-" * 28 + "\n"
        
        elif type == "tier_placement":
            current_team = ""
            for row in warplan_info:
                roster = row.get("Roster", "N/A")
                name = row.get("Name", "N/A")
                if roster.startswith("T1"):
                    current_team = roster.split()[1]
                    formatted_info += f"**{current_team}**\n"
                formatted_info += f"{roster.replace(current_team, '').strip()} {name}\n"

        # Split the formatted_info into chunks if it exceeds the Discord limit
        chunks = [formatted_info[i:i + 4000] for i in range(0, len(formatted_info), 4000)]

        embeds = []
        for chunk in chunks:
            embed = Embed(
                title=title,
                description=f"{chunk}\n\nLast Updated: **{last_updated()}**",
                color=0x212121  # Black Charcoal color
            )
            embeds.append(embed)

        for embed in embeds:
            await ctx.send(embeds=[embed])
    else:
        await ctx.send("No warplan data found.")