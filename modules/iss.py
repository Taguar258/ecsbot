from datetime import datetime
from json import loads

from config.config import config
from discord import Embed
from discord.ext import commands
from discord_slash import SlashContext, cog_ext
from requests import get


class ISS(commands.Cog):
    """ Cog for iss command
    """
    def __init__(self, bot):

        self.bot = bot

    async def get_data(self):
        """ Fetch data from open notify server
        """
        iss_now = get("http://api.open-notify.org/iss-now.json").text
        astros = get("http://api.open-notify.org/astros.json").text

        response = {"astros": loads(astros), "iss_now": loads(iss_now)}

        return response

    async def parse_astros(self, astros):
        """ Parse astros from json data
        """
        people = {}
        msg = ""

        for guy in astros:

            if guy["craft"] in people:

                people[guy["craft"]].append(str(len(people[guy["craft"]]) + 1) + ". " + guy["name"])

            else:

                people[guy["craft"]] = ["1. " + guy["name"]]

        for key in people:

            msg += "**" + key + "**\n" + "\n".join(people[key]) + "\n"

        return msg

    @cog_ext.cog_slash(name="iss")
    async def iss(self, ctx: SlashContext):
        """ Show data of ISS API (open-notify)
        """
        pls_wait = await ctx.send("Fetching...")

        date = datetime.now().strftime("%d.%m.%Y")

        data = await self.get_data()

        iss_location = f"{data['iss_now']['iss_position']['latitude']}, {data['iss_now']['iss_position']['longitude']}\n\n"
        astros = await self.parse_astros(data['astros']['people'])

        embed = Embed(color=config.COLOR)

        embed.set_author(name="ISS Info", icon_url="https://images-ext-1.discordapp.net/external/4YAoGmsd8-XPm09ASdxEsnHLpxaInoCvQguBk70Y7YQ/https/d30y9cdsu7xlg0.cloudfront.net/png/381875-200.png")
        embed.add_field(name="Location of the ISS now:", value=iss_location, inline=False)
        embed.add_field(name=f"Humans in Space ({data['astros']['number']}):", value=astros, inline=False)
        embed.set_image(url="http://www.businessforum.com/nasa01.JPEG")
        embed.set_footer(text=date)

        await pls_wait.edit(content="", embed=embed)


def setup(bot):
    """ On bot execute
    """
    if config.ISS_INFO_ENABLED:

        bot.add_cog(ISS(bot))
