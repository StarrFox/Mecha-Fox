from discord.ext import commands

class meta(commands.Cog):

    @commands.command()
    async def ping(self, ctx):
        """
        Send's the bot's websocket latency
        """
        await ctx.send(f"\N{TABLE TENNIS PADDLE AND BALL} {round(ctx.bot.latency*1000)}ms")

def setup(bot):
    bot.add_cog(meta())