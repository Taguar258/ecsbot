from asyncio import sleep as async_sleep

import discord
from config.config import config
from discord.ext import commands, tasks


class BumpReminder(commands.Cog):
    """ Cog for reminding staff to bump server on disboard
    """
    def __init__(self, bot):

        self.bot = bot
        self._lock = False

    @commands.Cog.listener()
    async def on_ready(self):
        """ Send bump reminder
        """
        await self.send_embed()

    @commands.Cog.listener()
    async def on_message(self, message):
        """ Start reminder on bump
        """
        #                        \  DISBOARD ID  /
        if message.author.id == 302050872383242240 and \
           "done" in message.embeds[0].description and \
           not self._lock:

            self._lock = True

            self.bot.loop.create_task(self.bump_reminder_tick())

    async def send_embed(self):
        """ Send bump reminder message
        """
        channel = self.bot.get_channel(config.BUMPCHANNEL)

        embed = discord.Embed(

            title="Bump Reminder",
            description=f"<@&{config.STAFFROLE}> Please bump this server on disboard using `!d bump`.",
            color=0xeb8c4c,

        )

        embed.set_image(url="https://disboard.org/images/bot-command-image-bump.png")

        await channel.send(embed=embed)

    @tasks.loop(hours=2)
    async def bump_reminder_tick(self):
        """ Send bump reminder message after two hours
        """
        await async_sleep(2 * (60 ** 2))

        try:

            await self.send_embed()

        finally:

            self._lock = False


def setup(bot):
    """ On bot execute
    """
    bot.add_cog(BumpReminder(bot))
