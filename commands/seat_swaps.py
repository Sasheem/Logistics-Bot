# commands/seat_swaps.py

import asyncio
from interactions import CommandContext
from config.google_sheets import client_gs
from config.constants import WAR_DOCS_SHEET_ID
from utils.fetch_data_with_cache import fetch_data_with_cache
from utils.last_updated import last_updated
from utils.seat_swaps_utils import build_graph_and_indegrees, topological_sort, reorder_rows, ensure_correct_order, detect_cycles

async def seat_swaps(ctx: CommandContext, clear_cache: bool = False):
    await ctx.defer()  # Acknowledge the interaction to avoid "Unknown Interaction" error

    warplan_type = "bot_seat_swaps"
    warplan_info = fetch_data_with_cache(client_gs, WAR_DOCS_SHEET_ID, warplan_type, use_cache=not clear_cache)
    
    if not warplan_info:
        await ctx.channel.send("No seat swap data found.")
        return
    
    # Build graph and perform topological sort
    graph, indegree = build_graph_and_indegrees(warplan_info)

    # Detect cycles before proceeding
    if detect_cycles(graph):
        await ctx.channel.send("⚠️ Circular Dependency detected. \nPlease check all holders in the sheet for duplicate names.")
        return

    # Perform topological sort and reorder rows
    sorted_order = topological_sort(graph, indegree)
    ordered_seats = reorder_rows(warplan_info, sorted_order)[::-1]  # Reverse the order

    # Ensure the correct order for specific cases
    ordered_seats = ensure_correct_order(ordered_seats)

    # Send the title for Ordered Seats
    await ctx.channel.send("# Seat MFing Swaps")
    await asyncio.sleep(1)  # Add a delay to avoid rate limiting

    # Send each ordered seat as an individual message
    for index, row in enumerate(ordered_seats, start=1):
        seat = row.get("Seat", "N/A")
        current_holder = row.get("Current Holder", "N/A")
        new_holder = row.get("New Holder", "N/A")
        status = row.get("Status", "N/A")
        message = f"{index}. **{seat} ({status})**\n{current_holder} > {new_holder}"
        await ctx.channel.send(message)
        await asyncio.sleep(1)  # Add a delay to avoid rate limiting

    # Send a final response to indicate the interaction is complete
    await ctx.channel.send(f"> Seat Swaps: **{last_updated()}**")
    await ctx.send("Seat swaps have been processed.")