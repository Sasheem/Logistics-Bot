# utils/check_permissions.py
from interactions import CommandContext

async def check_permissions(ctx: CommandContext) -> bool:
    member = await ctx.guild.get_member(ctx.author.id)  # Fetch full member object

    if not member:
        await ctx.send("Could not retrieve member data. Try again later.")
        return False  # FAILURE

    # Fetch all roles in the guild
    guild_roles = await ctx.guild.get_all_roles()

    # Find the role object by name
    org_team_role = next((role for role in guild_roles if role.name == "Org Team"), None)

    # Check if user has the required role
    if org_team_role and org_team_role.id in member.roles:
        return True  # SUCCESS
    else:
        await ctx.send("> **Missing org role** \nTag Org Team for help or run roster command without clear_cache.")
        return False # FAILURE