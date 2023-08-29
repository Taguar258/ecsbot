from datetime import datetime
from textwrap import wrap

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

            for pos, (before, after) in enumerate(zip(wrap(before.content, 1000), wrap(after.content, 1000))):

                embed.add_field(name=f"Before[{pos}]", value=before, inline=False)

                embed.add_field(name=f"After[{pos}]", value=after, inline=False)

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
            full_title = f"**Message sent by** <@{message.author.id}> **deleted in** <#{message.channel.id}>"
            footer = f"Author: {message.author.id} | Message ID: {message.id} • {date}"

            embed = Embed(

                description=full_title,
                color=config.COLOR,

            )

            for pos, content in enumerate(wrap(message.content, 1000)):

                embed.add_field(name=f"Content[{pos}]", value=content, inline=False)

            for pos, attachment in enumerate(message.attachments):

                embed.add_field(name=f"Attachment[{pos}]", value=attachment.url, inline=False)

            embed.set_author(name=full_name, icon_url=message.author.avatar_url)

            embed.set_footer(text=footer)

            log_message = await channel.send(embed=embed)
            await message.channel.send(embed=Embed(
                description=f"*Message sent by* <@{message.author.id}> *deleted* ({log_message.jump_url})",
                color=config.COLOR,
            ))

def setup(bot):
    """ On bot execute
    """
    bot.add_cog(MessageLog(bot))
