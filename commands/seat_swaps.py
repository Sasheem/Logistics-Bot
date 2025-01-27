# commands/seat_swaps.py

import asyncio
from interactions import CommandContext
from config.google_sheets import client_gs
from config.constants import WAR_DOCS_SHEET_ID
from utils.fetch_data_with_cache import fetch_data_with_cache
from utils.last_updated import last_updated

async def seat_swaps(ctx: CommandContext, clear_cache: bool = False):
    await ctx.defer()  # Acknowledge the interaction to avoid "Unknown Interaction" error

    warplan_type = "bot_seat_swaps"
    warplan_info = fetch_data_with_cache(client_gs, WAR_DOCS_SHEET_ID, warplan_type, use_cache=not clear_cache)
    
    if warplan_info:
        ordered_seats = []
        special_values = ["KL Raffle", "DROP", "ANY RCA", "Fairy Alt", "X"]

        # Collect all rows into ordered_seats
        for row in warplan_info:
            ordered_seats.append(row)

        # Re-order the ordered_seats list
        def find_ordered_seats(ordered_seats):
            graph = {}
            indegree = {}
            for row in ordered_seats:
                current_holder = row["Current Holder"]
                new_holder = row["New Holder"]
                if current_holder not in graph:
                    graph[current_holder] = []
                if new_holder not in graph:
                    graph[new_holder] = []
                graph[current_holder].append(new_holder)
                indegree[new_holder] = indegree.get(new_holder, 0) + 1
                if current_holder not in indegree:
                    indegree[current_holder] = 0

            queue = [node for node in graph if indegree[node] == 0]
            sorted_order = []
            while queue:
                node = queue.pop(0)
                sorted_order.append(node)
                for neighbor in graph[node]:
                    indegree[neighbor] -= 1
                    if indegree[neighbor] == 0:
                        queue.append(neighbor)

            ordered_seats_sorted = []
            visited_indices = []
            for node in sorted_order:
                for idx, row in enumerate(ordered_seats):
                    if row["Current Holder"] == node and idx not in visited_indices:
                        ordered_seats_sorted.append(row)
                        visited_indices.append(idx)
                        # Ensure the row with the player's name in the new holder appears directly after
                        for dep_idx, dependent_row in enumerate(ordered_seats):
                            if dependent_row["Current Holder"] == row["New Holder"] and dep_idx not in visited_indices:
                                ordered_seats_sorted.append(dependent_row)
                                visited_indices.append(dep_idx)
            return ordered_seats_sorted

        ordered_seats = find_ordered_seats(ordered_seats)[::-1]  # Reverse the order

        # Ensure the correct order for the specific case
        def ensure_correct_order(ordered_seats):
            for i in range(len(ordered_seats) - 1):
                current_holder = ordered_seats[i]["Current Holder"]
                for j in range(i + 1, len(ordered_seats)):
                    if ordered_seats[j]["New Holder"] == current_holder:
                        ordered_seats.insert(i + 1, ordered_seats.pop(j))
                        break
            return ordered_seats

        ordered_seats = ensure_correct_order(ordered_seats)

        # Send the title for Ordered Seats
        await ctx.channel.send("# Ordered Seats")
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

    else:
        await ctx.channel.send("No seat swap data found.")