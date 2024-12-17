# commands/stats_analysis.py

from interactions import CommandContext


async def stats_analysis(ctx: CommandContext, type: str):
    await ctx.defer()  # Acknowledge the interaction to avoid "Unknown Interaction" error
    
    await ctx.send(f"## Command Unavailable \nPlease try again later.")