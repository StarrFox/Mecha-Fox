from discord.ext import commands

GUILDID = 390607785437691916
MOD_ID = 396797202779078657
NUBBY_ID = 176796254821548033

async def is_nubby_or_owner(ctx):
    return await ctx.bot.is_owner(ctx.author) or ctx.author.id == NUBBY_ID

def is_filter_loaded():
    def predicate(ctx):
        return ctx.bot.events_loaded
    return commands.check(predicate)

def is_above_mod():
    def pred(ctx):
        mod_role = ctx.bot.get_guild(GUILDID).get_role(MOD_ID)
        return ctx.author.top_role.position >= mod_role.position
    return commands.check(pred)

def above_mod(member):
    mod_role = member.guild.get_role(MOD_ID)
    return member.top_role.position >= mod_role.position