import bot_stuff
import config

mecha = bot_stuff.Bot("fox!", [285148358815776768], "cogs")

mecha.load_extension("jishaku")

mecha.run(config.token)