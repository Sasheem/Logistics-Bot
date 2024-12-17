# commands/stats_review.py

from interactions import CommandContext


async def stats_review(ctx: CommandContext, type: str):
    await ctx.defer()  # Acknowledge the interaction to avoid "Unknown Interaction" error
    
    await ctx.send(f"## Command Unavailable \nPlease try again later.")