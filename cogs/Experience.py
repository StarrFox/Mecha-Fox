import discord
import json
import asyncio
import random

from discord.ext import commands
from extras import checks, utils

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
                self.check_integrity()
        return True

    def save_xp(self):
        """
        Saves xp file
        """
        with open("storage/experience.json", 'w') as fp:
            json.dump(self.xp, fp, indent=4)

    def check_integrity(self):
        """
        Checks that everyone in the experience dict are
        in the guild
        """
        guild = self.bot.guild()
        guild_ids = [m.id for m in guild.members]
        dict_ids = list(self.xp.keys())
        for uid in dict_ids:
            if not uid in guild_ids:
                self.xp.pop(uid)
        return True

    def cog_unload(self):
        self.save_xp()

    @commands.Cog.listener("on_message")
    async def incoming_messages(self, message: discord.Message):
        """
        Handles inc messages and xp adding process
        """
        if self.should_add_xp(message):
            self.add_xp(message.author.id)
        else:
            return

    @commands.Cog.listener("on_member_remove")
    async def member_remove_integrity_trigger(self, member):
        self.check_integrity()

    def should_add_xp(self, message: discord.Message):
        """
        Returns if a message should give xp
        atm just checks if they are in task list
        checking for spam messages in future?
        """
        return not message.author.id in self.given_xp_tasks.keys() and not message.author.bot

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
        #user is None
        user = user or ctx.author
        xp = self.xp.get(user.id) or 0
        await ctx.send(f"{user.display_name} has {xp} experience.")

    @commands.command(name="clear")
    @checks.is_above_mod()
    async def xp_clear(self, ctx, user: discord.Member):
        """
        Clear a member's xp
        """
        try:
            await ctx.send(f"Cleared {user.display_name}'s {self.xp.pop(user.id)} experience.")
        except KeyError:
            await ctx.send(f"{user.display_name} had no xp to clear.")

    @commands.command(name="add")
    @checks.is_above_mod()
    async def xp_add(self, ctx, user: discord.Member, ammount: int):
        """
        adds to a users xp
        yes you can add negitives this
        is just for convence
        """
        try:
            self.xp[user.id] += ammount
        except KeyError:
            self.xp[user.id] = ammount
        await ctx.send(f"Added {ammount} to {user.display_name}'s total experience.")

    @commands.command(name="remove")
    @checks.is_above_mod()
    async def xp_remove(self, ctx, user: discord.Member, ammount: int):
        """
        removes from a users xp
        yes you can remove negitives this
        is just for convence
        """
        try:
            self.xp[user.id] -= ammount
            if self.xp[user.id] < 0:
                self.xp[user.id] = 0
        except KeyError:
            pass
        await ctx.send(f"Removed {ammount} from {user.display_name}'s total experience.")

    @commands.command(name="lb")
    async def xp_lb(self, ctx):
        """
        Top 10 leaderboard
        """
        lb = "\n".join(
            [f"{i+1}. {ctx.guild.get_member(ki[0]).display_name}: {ki[1]}" for i, ki in enumerate([(k, i) for k, i in reversed(sorted(list(self.xp.items())[:10], key=lambda x: x[1]))])]
            )
        await ctx.send(utils.block(lb))

def setup(bot):
    bot.add_cog(experience(bot))