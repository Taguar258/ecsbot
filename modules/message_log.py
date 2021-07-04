from datetime import datetime

from config.config import config
from discord import Embed
from discord.ext import commands


class MessageLog(commands.Cog):
    """ Cog for logging common events
    """
    def __init__(self, bot):

        self.bot = bot

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        """ Log on message edit
        """
        if not after.author.bot:

            channel = self.bot.get_channel(config.LOGCHANNEL)

            date = datetime.now().strftime("%d.%m.%Y")

            full_name = f"{after.author.name}#{after.author.discriminator}"
            full_title = f"**Message edited in** <#{after.channel.id}> [Jump to Message]({after.jump_url})"
            footer = f"User ID: {after.author.id} • {date}"

            embed = Embed(

                description=full_title,
                color=config.COLOR,

            )

            embed.set_author(name=full_name, icon_url=after.author.avatar_url)

            embed.add_field(name="Before", value=before.content, inline=False)
            embed.add_field(name="After", value=after.content, inline=False)

            embed.set_footer(text=footer)

            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        """ Log on message delete
        """
        if not message.author.bot:

            channel = self.bot.get_channel(config.LOGCHANNEL)

            date = datetime.now().strftime("%d.%m.%Y")

            full_name = f"{message.author.name}#{message.author.discriminator}"
            full_title = f"**Message sent by** <@{message.author.id}> **deleted in** <#{message.channel.id}>\n{message.content}"
            footer = f"Author: {message.author.id} | Message ID: {message.id} • {date}"

            embed = Embed(

                description=full_title,
                color=config.COLOR,

            )

            embed.set_author(name=full_name, icon_url=message.author.avatar_url)

            embed.set_footer(text=footer)

            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        """ Log member update event
        """
        # On role add
        if len(before.roles) < len(after.roles):

            channel = self.bot.get_channel(config.LOGCHANNEL)

            date = datetime.now().strftime("%d.%m.%Y")

            # Determin new role
            for role in after.roles:

                if role not in before.roles:

                    added_role = role

            full_name = f"{after.name}#{after.discriminator}"
            full_title = f"**The** `{added_role.name}` **role was given to** <@{after.id}>"
            footer = f"ID: {after.id} • {date}"

            embed = Embed(

                description=full_title,
                color=config.COLOR,

            )

            embed.set_author(name=full_name, icon_url=after.avatar_url)

            embed.set_footer(text=footer)

            await channel.send(embed=embed)

        # On role remove
        elif len(before.roles) > len(after.roles):

            channel = self.bot.get_channel(config.LOGCHANNEL)

            date = datetime.now().strftime("%d.%m.%Y")

            # Determin removed role
            for role in before.roles:

                if role not in after.roles:

                    removed_role = role

            full_name = f"{after.name}#{after.discriminator}"
            full_title = f"**The** `{removed_role.name}` **role was removed from** <@{after.id}>"
            footer = f"ID: {after.id} • {date}"

            embed = Embed(

                description=full_title,
                color=config.COLOR,

            )

            embed.set_author(name=full_name, icon_url=after.avatar_url)

            embed.set_footer(text=footer)

            await channel.send(embed=embed)


def setup(bot):
    """ On bot execute
    """
    bot.add_cog(MessageLog(bot))
