from datetime import datetime
from re import IGNORECASE, MULTILINE, search, sub
from time import sleep

from config.config import config
from discord import Embed


async def detect_dangerous_commands(message):
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
