from random import choice

import discord
from config.config import config
from discord.ext import commands, tasks
from discord_slash import SlashContext, cog_ext
from modules import get_full_name


class Debug(commands.Cog):
    """ Cog for debugging
    """
    def __init__(self, bot):

        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """ Change presence and print status
        """
        self.rotate_status_tick.start()
        self.change_status_tick.start()

        await self.member_counter()

        print(f"[i] Bot is ready, {self.bot.user.name}")

    @tasks.loop(minutes=5)
    async def change_status_tick(self):  # Rotate after 1 day automatically
        """ Change status back if changed.
            Used for dynmaic mood status.
        """
        if self.bot.activity is None or \
           self.bot.activity.name not in config.STATUS:

            await self.bot.change_presence(

                status=discord.Status.online,
                activity=discord.Activity(name=choice(config.STATUS), type=discord.ActivityType.competing)

            )

    @tasks.loop(hours=24)
    async def rotate_status_tick(self):
        """ Rotate status back if not changed.
        """
        if self.bot.activity is not None and \
           self.bot.activity.name in config.STATUS:

            await self.bot.change_presence(

                status=discord.Status.online,
                activity=discord.Activity(name=choice(config.STATUS), type=discord.ActivityType.competing)

            )

    async def member_counter(self):
        """ Update voice channel member counter
        """
        guild = self.bot.get_guild(config.GUILD)

        channel = guild.get_channel(config.MEMBERCOUNTCHANNEL)

        member_count_no_bots = sum([1 async for n in guild.fetch_members() if not n.bot])

        await channel.edit(name=f"Members: {member_count_no_bots}")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """ On member join server
        """
        join_leave_channel = self.bot.get_channel(config.JOINLEAVE_CHANNEL)

        await join_leave_channel.send(f"{member.mention} joined.")

        await self.member_counter()

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """ On member left server
        """
        join_leave_channel = self.bot.get_channel(config.JOINLEAVE_CHANNEL)
        full_name = get_full_name(member)

        await join_leave_channel.send(f"{full_name} left.")

        await self.member_counter()

    @cog_ext.cog_slash(name="ping")
    async def ping(self, ctx: SlashContext):
        """ API call latency
        """
        embed = discord.Embed(title="Ping:", color=config.COLOR)

        embed.add_field(name="API", value=str(round(self.bot.latency * 1000)) + "ms", inline=True)

        await ctx.send(embed=embed)


def setup(bot):
    """ On bot execute
    """
    bot.add_cog(Debug(bot))
