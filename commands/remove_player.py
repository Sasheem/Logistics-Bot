# commands/remove_player.py

from interactions import CommandContext
from config.constants import ATTACK_SHEET_ID, DEFENSE_SHEET_ID, DRAGON_SHEET_ID, TEST_SHEET_ID, ATTACK_SHEET_ID_33, DEFENSE_SHEET_ID_33, DRAGON_SHEET_ID_33
from utils.fetch_all_column_data import fetch_all_column_data
from utils.append_data_to_deleted_responses import append_data_to_deleted_responses
from rapidfuzz import process, fuzz
from datetime import datetime
import copy
from config.google_sheets import client_gs
import gspread.utils  # Import the gspread.utils module

# Define the sheet IDs for each option
SHEET_IDS = {
    "TEST": TEST_SHEET_ID,
    "Attack 89": ATTACK_SHEET_ID,
    "Defense 89": DEFENSE_SHEET_ID,
    "Dragon 89": DRAGON_SHEET_ID,
    "Attack 33": ATTACK_SHEET_ID_33,
    "Defense 33": DEFENSE_SHEET_ID_33,
    "Dragon 33": DRAGON_SHEET_ID_33,
}

# Headers to treat as strings
STRING_HEADERS = [
    "Keep Name",
    "Troop Tier",
    "Troop Type",
    "Primary or Secondary",
    "Additional Details",
    "Previous Team",
    "SOP"
]

# Header to treat as a date
DATE_HEADER = "Date"

async def remove_player(ctx: CommandContext, name: str, option: str, editor_note: str = None):
    await ctx.defer()  # Acknowledge the interaction to avoid "Unknown Interaction" error

    # Get the sheet ID for the selected option
    sheet_id = SHEET_IDS.get(option)
    if not sheet_id:
        await ctx.send(f"Invalid option: {option}")
        return

    tab_name = "Form_Responses"

    # Fetch the data from the specified sheet and tab
    data = fetch_all_column_data(sheet_id, tab_name)

    # Check for similar names using rapidfuzz, ignoring case
    existing_names = [str(row[1]).strip().lower() for row in data[1:]]  # Column index 1 for "Keep Name"
    similar_name = process.extractOne(name.strip().lower(), existing_names, scorer=fuzz.ratio, score_cutoff=80)

    if not similar_name:
        await ctx.send(f"\"{name}\" was not found in {option}.")
        return

    # Fetch the entire sheet data to access the "Editor Notes" column
    sheet_data = fetch_all_column_data(sheet_id, tab_name)

    # Find the index of the "Editor Notes" column (case-insensitive)
    headers = sheet_data[0]
    editor_notes_index = next((i for i, header in enumerate(headers) if header.lower() == "editor notes"), None)
    editor_checked_index = next((i for i, header in enumerate(headers) if header.lower() == "editor checked?"), None)
    if editor_notes_index is None:
        await ctx.send(f"\"Editor Notes\" column not found in {option}.")
        return

    # Initialize the sheet variable
    sheet = client_gs.open_by_key(sheet_id).worksheet(tab_name)

    # Find all entries for the matched name and clear their data
    matched_entries = []
    most_recent_entry_row_idx = -1
    for row_idx, row in enumerate(sheet_data[1:], start=1):
        if str(row[1]).strip().lower() == similar_name[0]:
            matched_entries.append(copy.deepcopy(row))
            most_recent_entry_row_idx = row_idx
            # Clear the data in the row except for the "Editor Notes" and "Editor checked?" columns
            for i in range(len(row)):
                if i != editor_notes_index and i != editor_checked_index:
                    row[i] = ""
            # Update the specific row in the sheet
            cell_list = sheet.range(f"A{row_idx + 1}:{gspread.utils.rowcol_to_a1(row_idx + 1, len(headers))}")
            for j, cell in enumerate(cell_list):
                if j < len(row):
                    value = row[j]
                    if headers[j] in STRING_HEADERS:
                        cell.value = value
                    elif headers[j] == DATE_HEADER:
                        cell.value = datetime.strptime(value, "%m/%d/%Y %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S") if value else ""
                    elif headers[j] != "Editor checked?":
                        cell.value = float(value.replace(',', '')) if value.replace(',', '').replace('.', '').isdigit() else value
                else:
                    cell.value = ""
            sheet.update_cells(cell_list)

    if not matched_entries:
        await ctx.send(f"No entries found for \"{name}\" in {option}.")
        return

    # Keep the most recent entry and append it to the "Deleted_Responses" tab
    most_recent_entry = matched_entries[-1]
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    deleted_entry = [timestamp] + most_recent_entry

    # Add the note to the "Editor Notes" column
    removal_message = f"{name} was removed"
    if editor_note:
        removal_message += f", {editor_note}"
    
    # Debug statement to check the removal message
    print(f"Removal Message: {removal_message}")

    if len(deleted_entry) > editor_notes_index:
        if deleted_entry[editor_notes_index]:
            # Debug statement to check the removal message
            print(f"Deleted_entry has existing note: {removal_message}")
            deleted_entry[editor_notes_index] += f" | {removal_message}"
        else:
            # Debug statement to check the removal message
            print(f"Deleted_entry DOES NOT HAVE existing note: {removal_message}")
            deleted_entry[editor_notes_index] = removal_message
    else:
        # Debug statement to check the removal message
        print(f"Deleted_entry len < note index - DOES NOT HAVE existing note: {removal_message}")
        deleted_entry.append(removal_message)

    # Append the deleted entry to the "Deleted_Responses" tab
    append_data_to_deleted_responses(sheet_id, headers, deleted_entry)

    # Update the "Editor Notes" column in the "Form_Responses" tab for the most recent entry row
    editor_notes_cell = sheet.cell(most_recent_entry_row_idx + 1, editor_notes_index + 1)  # Adjust for 1-based index
    if editor_notes_cell.value:
        editor_notes_cell.value += f" | {removal_message}"
    else:
        editor_notes_cell.value = removal_message
    sheet.update_cell(editor_notes_cell.row, editor_notes_cell.col, editor_notes_cell.value)

    await ctx.send(f"**Player Removed** \nDeleted {len(matched_entries)} instance(s) of \"{name}\" from {option} and archived the most recent entry.")