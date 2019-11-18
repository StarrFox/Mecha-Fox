import os
import config
import datetime
import bot_stuff

IMAGE_PERM = 439723470667120640
NICK_PERM = 501092781473792020
REACT_PERM = 631690756079353887
STRIKE_ONE = 579370927389802499
STRIKE_TWO = 579370927943450626
STRIKE_THREE = 579370928987963396

# Makes our storage dir
if not os.path.exists('storage'):
    os.mkdir('storage')
    print("Made storage dir")

jsk_settings = {
    "scope_prefix": "",
    "retain": True,
    "channel_tracebacks": True
}

mecha = bot_stuff.Bot(config.prefix, config.owners, "cogs")

mecha.load_extension("bot_stuff.jsk", **jsk_settings)

mecha.guild_id = config.guild

def guild():
    return mecha.get_guild(mecha.guild_id)

def get_twoweeks():
    guild = mecha.guild()
    processed = [] #Returned positive
    for member in guild.members:
        role_ids = [r.id for r in member.roles]
        checks = [
            member.bot,
            IMAGE_PERM in role_ids and NICK_PERM in role_ids and REACT_PERM in role_ids,
            not member.joined_at + datetime.timedelta(weeks=2) < datetime.datetime.utcnow(),
            STRIKE_ONE in role_ids,
            STRIKE_TWO in role_ids,
            STRIKE_THREE in role_ids
        ]
        if any(checks):
            continue
        else:
            processed.append(member)
    return processed

mecha.twoweeks = get_twoweeks

mecha.guild = guild

mecha.events_loaded = False

mecha.add_ready_func(mecha.load_extension, "bot_stuff.logger", channel=578771629312704513)

mecha.run(config.token)