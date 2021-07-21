from asyncio import sleep as async_sleep

from config.config import config
from discord.ext import commands


class Cleanup(commands.Cog):
    """ Cog for general cleanup tasks
    """
    def __init__(self, bot):

        self.bot = bot

    @commands.command(pass_context=True)
    @commands.has_role(config.STAFFROLE)
    async def mpurge(self, ctx):
        """ Purge the mute channel
        """
        channel = self.bot.get_channel(config.MUTECHANNEL)
        await channel.purge()

        info_msg = await ctx.message.channel.send("Successfully purged the mute-appeal channel.")

        if ctx.message.channel.id == channel.id:  # Temporary message if send in mute channel

            await ctx.message.delete()

            await info_msg.add_reaction(config.REACT_SUCCESS)

            await async_sleep(6)
            await info_msg.delete()


def setup(bot):
    """ On bot execute
    """
    bot.add_cog(Cleanup(bot))
