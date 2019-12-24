import json
import discord
import logging

from extras import checks, utils
from discord.ext import commands, tasks

logger = logging.getLogger(__name__)

MOD_ID = 396797202779078657
LOGGING_ID = 578771629312704513
MUTED_ID = 396797327068626944
OPEN_CHAT_ID = 578328936472248340
MEMBER_ID = 439723301238210560
IMAGE_PERM = 439723470667120640
NICK_PERM = 501092781473792020
REACT_PERM = 631690756079353887

class events(commands.Cog):
    """
    Cog for events
    should not show in help
    """

    def __init__(self, bot):
        self.bot = bot
        self.warned = [] # list of ids
        self.muted = [] # list of ids
        self.warned_tasks = {} # id: self.warned_remover
        self.filter_list = [] # list of filtered words
        self.logging_channel = bot.guild().get_channel(LOGGING_ID)

        self.load_filter()
        bot.events_loaded = True
        self.check_twoweeks.start()

    def load_filter(self):
        with open("storage/filter.json", "a+") as fp:
            # Word mapped to True
            fp.seek(0)
            if len(fp.read()) == 0:
                return
            else:
                fp.seek(0)
                self.filter_list = list(json.load(fp).keys())
        logger.info(f"Loaded {len(self.filter_list)} filtered words.")

    def save_filter(self):
        to_save = {i: True for i in self.filter_list}
        with open("storage/filter.json", "w") as fp:
            json.dump(to_save, fp, indent=4)
        logger.info(f"Saved {len(self.filter_list)} filtered words.")

    async def attempt_send(self, destination, message):
        """
        Attempts to send a message to a destination
        useful for dms
        """
        try:
            await destination.send(message)
        except:
            pass

    def cog_unload(self):
        self.save_filter()

    @commands.Cog.listener("on_message")
    async def _filter(self, message):
        # Dm message
        if not message.guild or isinstance(message.author, discord.User):
            return
        ignored = [
            message.guild != self.bot.guild(),
            message.channel.id == OPEN_CHAT_ID,
            message.author.bot,
            checks.above_mod(message.author),
        ]
        if any(ignored):
            return
        words = [word for word in self.filter_list if word in message.content.lower()]
        if words:
            print(words) # debug
            author = message.author
            await message.delete()
            await self.logging_channel.send(utils.block(
                f"Filtered message from {author} ({author.id}) with words {', '.join(words)}\n"
                f"Time:{message.created_at} channel: {message.channel.name}"
            ))
            logger.info(f"Filtered {', '.join(words)} from {author}.")
            if author.id in self.warned:
                self.warned.remove(author.id)
                self.muted.append(author.id)
                self.warned_tasks[author.id].cancel()
                await author.add_roles(
                    self.bot.guild().get_role(MUTED_ID)
                )
                await self.logging_channel.send(utils.block(
                    f"Muted {author} ({author.id})\n"
                    f"Time:{message.created_at}"
                 ) + self.bot.guild().get_role(MOD_ID).mention
                )
                await self.attempt_send(author, "u used a bad word u will be muted until a mod decides your mute time ~Nubby")
            else:
                self.warned.append(author.id)
                await self.attempt_send(author, f"Warning: word(s) {', '.join(words)} are/is filtered, don't do again haha yes")
                await self.logging_channel.send(utils.block(
                    f"Warned {message.author} ({author.id})\n"
                    f"Time:{message.created_at}"
                ))
                self.warned_tasks[author.id] = self.bot.loop.create_task(self.warning_remover(author.id))
                logger.info(f"Running {len(self.warned_tasks.keys())} warning tasks.")
            

    @commands.Cog.listener("on_member_join")
    async def mute_retainer(self, member):
        if member.guild.id != self.bot.guild():
            return
        if member.id in self.muted:
            await member.add_roles(
                self.bot.guild().get_role(MUTED_ID)
            )
            logger.info(f"Retained {member}'s muted role.'")

    @commands.Cog.listener("on_member_update")
    async def mute_remover(self, before, after):
        if before.guild.id != self.bot.guild():
            return
        mute_role = self.bot.guild().get_role(MUTED_ID)
        if before.id in self.muted and mute_role in before.roles and not mute_role in after.roles:
            self.muted.remove(before.id)
            logger.info(f"Removed {after} from internal muted cache.")

    async def warning_remover(self, author_id: int):
        """
        Removes a warning after 24 hours
        """
        try:
            await asyncio.sleep(86_400)
            self.warned.remove(author_id)
        except:
            pass
        self.warned_tasks.pop(author_id)
        logger.info(f"Warning task for {author_id} ended.")

    @commands.Cog.listener("on_member_join")
    async def member_role_adder(self, member):
        await member.add_roles(
            self.bot.guild().get_role(MEMBER_ID)
        )
        logger.info(f"Gave {member} the member role.")

    @tasks.loop(hours=1)
    async def check_twoweeks(self):
        processed = self.bot.twoweeks()
        if not processed:
            return
        roles = [self.bot.guild().get_role(i) for i in [NICK_PERM, REACT_PERM, IMAGE_PERM]]
        for member in processed:
            await member.add_roles(*roles)
            logger.info(f"Twoweeks roles added to {member}.")
            await self.logging_channel.send(f"Twoweeks roles added to {member}.")

def setup(bot):
    bot.add_cog(events(bot))
