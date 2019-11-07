import bot_stuff
import config
import os

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

mecha.guild = guild

mecha.run(config.token)