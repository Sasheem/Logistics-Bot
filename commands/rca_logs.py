from interactions import CommandContext
from config.google_sheets import client_gs
from config.constants import RCA_SHEET_ID
from utils.fetch_sheets_data import fetch_sheets_data

async def rca_logs(ctx: CommandContext, filter_type: str = "All"):
    await ctx.defer()  # Acknowledge the interaction to avoid "Unknown Interaction" error
    rca_logs_list = fetch_sheets_data(client_gs, RCA_SHEET_ID, "bot_rca_info")
    if rca_logs_list:
        if filter_type != "All":
            rca_logs_list = [entry for entry in rca_logs_list if entry['Type'] == filter_type]

        messages = []
        chunk_counter = 1
        formatted_info = f">>> # RCA Logs {chunk_counter}\n## Filtered by: {filter_type}\n"
        for entry in rca_logs_list:
            name = entry['Name']
            rein_cap = entry['Rein Cap']
            type_ = entry['Type']
            power_level = entry['Power Level']
            facebook_name = entry['Facebook Name']
            email = entry['Email']
            password = entry['Password']
            entry_info = (
                f"**{name:<20}**\n"
                f"{rein_cap} | {type_} | {power_level}\n"
                f"{'-' * 5}\n"
                f"FB: {facebook_name:<20}\n"
                f"{email} | {password}\n"
                + "-" * 30 + "\n"
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