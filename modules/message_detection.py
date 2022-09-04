from datetime import datetime
from re import IGNORECASE, MULTILINE, search, sub
from time import sleep

from config.config import config
from discord import Embed, utils
from discord.ext import commands

# from requests import get as requests_get


class MessageDetection(commands.Cog):
    """ Cog for bad command message detection
    """
    def __init__(self, bot):

        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        """ On message sent
        """
        # retrieve member object to read roles of user aka author
        guild = self.bot.get_guild(config.GUILD)
        member = guild.get_member(message.author.id)

        if not message.author.bot and \
           config.HELPERROLE not in [role.id for role in member.roles]:

            message.content = utils.remove_markdown(message.content)

            await self.detect_dangerous_commands(message)

            # if len(message.attachments) >= 1:  # TODO: Check files too

            #     for attachment in message.attachments:

            #         if attachment.url.endswith(".sh"):

            #             file = requests_get(attachment.url)  # Limit download size

            #             message.content = file[:100]

            #             await self.detect_dangerous_commands(message)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        """ On message edit
        """
        # retrieve member object to read roles of user aka author
        guild = self.bot.get_guild(config.GUILD)
        member = guild.get_member(after.author.id)

        if not after.author.bot and \
           config.HELPERROLE not in [role.id for role in member.roles]:

            # after.content = self.filter_md(after.content)
            after.content = utils.remove_markdown(after.content)

            await self.detect_dangerous_commands(after)

    # def filter_md(self, md):
    #     """ Remove markdown syntax from content of message
    #     """
    #     for rep in ["*", "`", "~", "_"]:

    #         md = md.replace(f"\\{rep}", rep)

    #     for _ in range(20):  # Potential sec risk

    #         match = search(r"((\*.*\*)|(\_.*\_)|(\~.*\~)|(\`.*\`))", md)  # Bad regex

    #         if not match:

    #             break

    #         md = md[:match.start()] + md[(match.start() + 1):(match.end() - 1)] + md[match.end():]

    #     return md

    async def detect_dangerous_commands(self, message):
        """ Check if message includes potentially harmful code.

        For example:
         - dd
         - gparted
         - rm
         - etc.

        """
        message_content = sub(r"<.{1,2}\d*>", "", message.content)  # Pings trigger things ;)

        # Check for match
        if search(config.GREY_COMMANDS_COMBINED, message_content, MULTILINE | IGNORECASE):  # Checking in advance as this decreases cpu usage

            # Delete message
            await message.delete()

            # Get reason
            for regex_id, (regex, reason) in enumerate(config.GREY_COMMANDS.items()):  # noqa: B007  # Takes time but identifies regex

                if search(regex, message_content, MULTILINE | IGNORECASE):

                    break

                sleep(0.02)

            # Variables
            date = datetime.now().strftime("%d.%m.%Y")

            full_name = f"{message.author.name}#{message.author.discriminator}"
            footer = f"Author: {message.author.id} | Message ID: {message.id} • {date} • {regex_id}"

            new_message_content = f"""
**WARNING: Potentially harmful instructions:**

------------------------------------------
||{message.content[:1024]}||
------------------------------------------
*Click the spoiler above to see the original message, send by {full_name}.*

```
The following message includes a command that is gray-listed, {reason[0]}.
This does not mean that the commands included will cause damage, but we suggest you to get a trustful second opinion.
```
**{reason[1]}**
"""

            # Create Embed
            embed = Embed(description=new_message_content, color=config.COLOR)

            embed.set_author(name=full_name, icon_url=message.author.avatar_url)

            embed.set_footer(text=footer)

            # Send Embed
            await message.channel.send(embed=embed)


def setup(bot):
    """ On bot execute
    """
    bot.add_cog(MessageDetection(bot))
