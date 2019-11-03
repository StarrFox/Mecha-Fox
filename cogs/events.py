from discord.ext import commands

class events(commands.Cog):
    """
    Cog for events
    should not show in help
    """

def setup(bot):
    bot.add_cog(events())