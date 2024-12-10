from interactions import CommandContext
from config.google_sheets import client_gs
from config.constants import RCA_SHEET_ID
from utils.fetch_sheets_data import fetch_sheets_data

async def list_rca_logs(ctx: CommandContext, filter_type: str = "All", min_cap: int = 0):
    await ctx.defer()  # Acknowledge the interaction to avoid "Unknown Interaction" error
    rca_logs_list = fetch_sheets_data(client_gs, RCA_SHEET_ID, "bot_rca_info")
    if rca_logs_list:
        if filter_type != "All":
            rca_logs_list = [entry for entry in rca_logs_list if entry['Type'] == filter_type]
        if min_cap > 0:
            rca_logs_list = [entry for entry in rca_logs_list if convert_to_number(entry['Rein Cap']) > min_cap]

        messages = []
        chunk_counter = 1
        formatted_info = f">>> # RCA Logs {chunk_counter}\n## Filtered by: {filter_type}\n"
        for entry in rca_logs_list:
            name = entry['Name'] or "n/a"
            rein_cap = entry['Rein Cap'] or "n/a"
            type_ = entry['Type'] or "n/a"
            power_level = entry['Power Level'] or "n/a"
            facebook_name = entry['Facebook Name'] or "n/a"
            email = entry['Email'] or "n/a"
            password = entry['Password'] or "n/a"
            entry_info = (
                f"{'-' * 30}\n"
                f"**{name}**\n"
                f"{rein_cap} | {type_} | {power_level}\n"
                f"{'--' * 2}\n"
                f"FB: {facebook_name}\n"
                f"{email} | {password}\n"
            )
            if len(formatted_info) + len(entry_info) + 3 > 2000:  # 2000 is the Discord message limit
                messages.append(formatted_info)
                chunk_counter += 1
                formatted_info = f">>> # RCA Logs {chunk_counter}\n## Filtered by: {filter_type}\n" + entry_info
            else:
                formatted_info += entry_info
        messages.append(formatted_info)
        
        for message in messages:
            await ctx.send(message)
    else:
        await ctx.send("No RCA logs found.")

def convert_to_number(value):
    if isinstance(value, str) and value.endswith('K'):
        return int(float(value[:-1]) * 1000)
    return int(value)