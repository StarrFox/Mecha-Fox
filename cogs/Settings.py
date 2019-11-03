from discord.ext import commands

class settings(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    def load_settings(self):
        return

def setup(bot):
    bot.add_cog(settings(bot))