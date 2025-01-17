# /commands/war_leads.py - Commands for fetching war leads data from the Google Sheets

from datetime import datetime, timedelta
import calendar
import pytz
from interactions import CommandContext, Embed
from config.google_sheets import client_gs
from config.constants import WAR_DOCS_SHEET_ID
from utils.fetch_data_with_cache import fetch_data_with_cache
from utils.last_updated import last_updated

async def warleads(ctx: CommandContext, type: str, clear_cache: bool = False):
    await ctx.defer()  # Acknowledge the interaction to avoid "Unknown Interaction" error

    warplan_type = "bot_war_leads"
    warplan_info = fetch_data_with_cache(client_gs, WAR_DOCS_SHEET_ID, warplan_type, use_cache=not clear_cache)
    
    if warplan_info:
        title = f"War Leads ({type.upper()})"
        formatted_info = ""

        # Define the headers based on the type
        headers = {
            "PVP": ["Shift", "Counter 1", "Counter 2", "Attack 1", "Attack 2", "Attack 3", "Defense 1", "Defense 2", "Defense 3"],
            "KVK": ["Shift KVK", "Counter 1 KVK", "Counter 2 KVK", "Attack 1 KVK", "Attack 2 KVK", "Attack 3 KVK", "Defense 1 KVK", "Defense 2 KVK", "Defense 3 KVK"]
        }

        # Get the current date and time in EST
        est = pytz.timezone('US/Eastern')
        now = datetime.now(est)
        print(f"Current date and time: {now}")

        # Calculate the upcoming Saturday at 6 PM EST for PVP and 1 PM EST for KVK
        days_until_saturday = (5 - now.weekday() + 7) % 7
        if days_until_saturday == 0:
            days_until_saturday = 7
        upcoming_saturday = now + timedelta(days=days_until_saturday)
        print(f"Upcoming Saturday: {upcoming_saturday}")

        first_shift_time_pvp = est.localize(datetime(upcoming_saturday.year, upcoming_saturday.month, upcoming_saturday.day, 18, 0))
        first_shift_time_kvk = est.localize(datetime(upcoming_saturday.year, upcoming_saturday.month, upcoming_saturday.day, 13, 0))
        print(f"First shift time PVP: {first_shift_time_pvp}")
        print(f"First shift time KVK: {first_shift_time_kvk}")

        shift_dt = first_shift_time_pvp if type.upper() == "PVP" else first_shift_time_kvk
        time_increment = timedelta(hours=3) if type.upper() == "PVP" else timedelta(hours=5)

        for i, row in enumerate(warplan_info):
            if type.upper() == "KVK" and i >= 7:
                break  # Limit to 7 shifts for KVK

            print(f"Shift datetime before increment: {shift_dt}")
            timestamp = calendar.timegm(shift_dt.utctimetuple())
            print(f"Timestamp: {timestamp}")
            formatted_info += f"**<t:{timestamp}:F>**\n\n"

            # Condense the values into a single line and exclude "X"
            counters = ", ".join([row[header] for header in headers[type] if "Counter" in header and row[header] != "X"])
            attacks = ", ".join([row[header] for header in headers[type] if "Attack" in header and row[header] != "X"])
            defenses = ", ".join([row[header] for header in headers[type] if "Defense" in header and row[header] != "X"])

            if counters or attacks or defenses:
                if counters:
                    formatted_info += f"Counter(s): {counters}\n"
                if attacks:
                    formatted_info += f"Attack: {attacks}\n"
                if defenses:
                    formatted_info += f"Defense: {defenses}\n"
            else:
                formatted_info += "None scheduled yet\n"
            
            formatted_info += "-" * 28 + "\n\n"
            shift_dt += time_increment  # Increment the shift time for the next row
            print(f"Shift datetime after increment: {shift_dt}")

            if type.upper() == "KVK":
                time_increment = timedelta(hours=4)  # Subsequent shifts are 4 hours

        # Split the formatted_info into chunks if it exceeds the Discord limit
        chunks = [formatted_info[i:i + 4000] for i in range(0, len(formatted_info), 4000)]

        embeds = []
        for chunk in chunks:
            embed = Embed(
                title=title,
                description=f"{chunk}\nLast Updated: **{last_updated()}**",
                color=0x212121  # Black Charcoal color
            )
            embeds.append(embed)

        for embed in embeds:
            await ctx.send(embeds=[embed])
    else:
        await ctx.send("No war leads data found.")

