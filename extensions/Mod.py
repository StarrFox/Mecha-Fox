import discord
import logging

from extras import checks
from discord.ext import commands

logger = logging.getLogger(__name__)

class mod(commands.Cog):
    """
    Moderation commands
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="filter", invoke_without_command=True)
    @checks.is_filter_loaded()
    @checks.is_above_mod()
    async def filter_command(self, ctx):
        """
        Base filter command
        Sends filter to dms without subcommand
        """
        filter_list = self.bot.get_cog("events").filter_list
        await self.bot.paginate(", ".join(filter_list), ctx.author)

    @filter_command.command(name="add")
    async def filter_add_command(self, ctx, *words):
        """
        Add a filtered word or words
        seperated by spaces
        """
        events_cog = self.bot.get_cog("events")
        for word in words:
            if word in events_cog.filter_list:
                await ctx.send(f"{word} is already filtered.")
            else:
                await ctx.send(f"Added {word} to filter.")
                events_cog.filter_list.append(word)
        events_cog.save_filter()
        logger.info(f"Added {', '.join(words)} to filter.")

    @filter_command.command(name="remove", aliases=["rem"])
    async def filter_rem_command(self, ctx, *words):
        """
        Remove a filter word or words
        seperated by spaces
        """
        events_cog = self.bot.get_cog("events")
        for word in words:
            try:
                events_cog.filter_list.remove(word)
                await ctx.send(f"Removed {word} from filter.")
            except ValueError:
                await ctx.send(f"{word} was not in filter.")
        events_cog.save_filter()
        logger.info(f"Removed {', '.join(words)} from filer.")

def setup(bot):
    bot.add_cog(mod(bot))