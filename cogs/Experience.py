import discord
import json
import asyncio
import random

from discord.ext import commands

class experience(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.given_xp_tasks = {} # user_id: given_xp_task
        self.xp = {} # user_id: xp ammount
        self.load_xp()

    # internal methods

    def load_xp(self):
        """
        Loads xp file
        Json because this is only made for one guild
        """
        with open("storage/experience.json", 'a+') as fp:
            fp.seek(0)
            if len(fp.read()) == 0:
                self.xp = {}
            else:
                fp.seek(0)
                temp = json.load(fp)
                # convert keys to ints
                self.xp = {k: i for k, i in map(lambda ki: (int(ki[0]), ki[1]), temp.items())}
        return True

    def save_xp(self):
        """
        Saves xp file
        """
        with open("storage/experience.json", 'w') as fp:
            json.dump(self.xp, fp, indent=4)

    def cog_unload(self):
        self.save_xp()

    @commands.Cog.listener("on_message")
    async def Incoming_messages(self, message: discord.Message):
        """
        Handles inc messages and xp adding process
        """
        if self.should_add_xp(message):
            self.add_xp(message.author.id)
        else:
            return

    def should_add_xp(self, message: discord.Message):
        """
        Returns if a message should give xp
        atm just checks if they are in task list
        checking for spam messages in future?
        """
        return not message.author.id in self.given_xp_tasks.keys()

    def add_xp(self, user_id):
        """
        Adds xp to a user's total
        """
        try:
            self.xp[user_id] += 1
        except KeyError:
            self.xp[user_id] = 1
        time = random.randrange(0, 6)*60 # sleep takes seconds
        self.given_xp_tasks[user_id] = self.bot.loop.create_task(
            self.given_xp_task(user_id, time)
        )

    async def given_xp_task(self, user_id: int, time: int):
        """
        Removes a user from given_xp
        """
        try:
            await asyncio.sleep(time)
        except:
            pass
        self.given_xp_tasks.pop(user_id)

    # user facing

    @commands.command(name="xp")
    async def xp_view(self, ctx, user: discord.Member = None):
        """
        See your xp ammount
        """
        await ctx.send(self.xp.get(user.id if user else ctx.author.id) or 0)

def setup(bot):
    bot.add_cog(experience(bot))