from interactions import CommandContext
from utils.check_permissions import check_permissions
from utils.clear_all_cache import clear_all_cache

async def clear_roster_cache(ctx: CommandContext):
    await ctx.defer()

    has_permission = await check_permissions(ctx)
    if not has_permission:
        return

    cleared = clear_all_cache()
    if cleared:
        await ctx.send("> ✅ Roster cache has been successfully cleared.")
    else:
        await ctx.send("> ⚠️ Roster cache was already empty. Nothing to clear.")