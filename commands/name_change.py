# commands/name_change.py

from interactions import CommandContext
from config.constants import ATTACK_SHEET_ID, DEFENSE_SHEET_ID, DRAGON_SHEET_ID, ROSTER_SHEET_ID, RCA_SHEET_ID, TEST_SHEET_ID, ATTACK_SHEET_ID_33, DEFENSE_SHEET_ID_33, DRAGON_SHEET_ID_33
from utils.update_column_data import update_column_data
from utils.fetch_column_data import fetch_column_data
from utils.add_name_change_note import add_name_change_note

# Define the sheet and tab names for each option
SHEET_TABS = {
    "TEST": {"sheet_id": TEST_SHEET_ID, "tab_name": "Form_Responses", "column": 2},
    "Active Keeps": {"sheet_id": ROSTER_SHEET_ID, "tab_name": "ACTIVE_KEEPS", "column": 2},
    "Keep Logistics": {"sheet_id": ROSTER_SHEET_ID, "tab_name": "Keep_Logistics_Submissions", "column": 3},
    "Attack 89": {"sheet_id": ATTACK_SHEET_ID, "tab_name": "Form_Responses", "column": 2},
    "Defense 89": {"sheet_id": DEFENSE_SHEET_ID, "tab_name": "Form_Responses", "column": 2},
    "Dragon 89": {"sheet_id": DRAGON_SHEET_ID, "tab_name": "Form_Responses", "column": 2},
    "Attack 33": {"sheet_id": ATTACK_SHEET_ID_33, "tab_name": "Form_Responses", "column": 2},
    "Defense 33": {"sheet_id": DEFENSE_SHEET_ID_33, "tab_name": "Form_Responses", "column": 2},
    "Dragon 33": {"sheet_id": DRAGON_SHEET_ID_33, "tab_name": "Form_Responses", "column": 2},
    "RCA": {"sheet_id": RCA_SHEET_ID, "tab_name": "RADS_RCA_Info", "column": 1},
}

async def name_change(ctx: CommandContext, old_name: str, new_name: str, option: str):
    await ctx.defer()  # Acknowledge the interaction to avoid "Unknown Interaction" error

    # Get the sheet and tab details for the selected option
    sheet_details = SHEET_TABS.get(option)
    if not sheet_details:
        await ctx.send(f"Invalid option: {option}")
        return

    sheet_id = sheet_details["sheet_id"]
    tab_name = sheet_details["tab_name"]
    column_index = sheet_details["column"]

    # Fetch the data from the specified sheet and tab
    data = fetch_column_data(sheet_id, tab_name, column_index)

    # Check if the old name exists in the data (case-insensitive, match entire cell contents)
    old_name_found = any(str(row).strip().lower() == old_name.strip().lower() for row in data)

    if not old_name_found:
        await ctx.send(f"\"{old_name}\" was not found in {option}.")
        return

    # Check if the old name and new name are the same (case-insensitive)
    if old_name.strip().lower() == new_name.strip().lower():
        await ctx.send(f"The old name \"{old_name}\" and the new name \"{new_name}\" are the same. Please try with a different new name.")
        return

    # Find and replace the old name with the new name (case-insensitive, match entire cell contents)
    updated_data = []
    change_count = 0
    for row in data:
        if str(row).strip().lower() == old_name.strip().lower():
            updated_data.append(new_name)
            change_count += 1
        else:
            updated_data.append(row)

    # Update the sheet with the modified data
    update_column_data(sheet_id, tab_name, column_index, updated_data)

    # Add a custom note if the option is "Active Keeps"
    if option == "Active Keeps":
        await add_name_change_note(ctx, old_name, new_name, ctx.author.name)

    await ctx.send(f"## Name change \nUpdated {change_count} instance(s) of \"{old_name}\" to **\"{new_name}\"** in {option}.")