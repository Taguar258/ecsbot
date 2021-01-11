# Taguar

from datetime import datetime
from json import loads

from config.config import config
from discord import Embed
from requests import get


async def get_data():

    iss_now = get("http://api.open-notify.org/iss-now.json").text
    astros = get("http://api.open-notify.org/astros.json").text

    response = {"astros": loads(astros), "iss_now": loads(iss_now)}

    return response


async def parse_astros(astros):

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


async def iss_info(message):

    if config.ISS_INFO_ENABLED:

        channel = message.channel

        date = datetime.now().strftime("%d.%m.%Y")

        data = await get_data()

        iss_location = f"{data['iss_now']['iss_position']['latitude']}, {data['iss_now']['iss_position']['longitude']}\n\n"
        astros = await parse_astros(data['astros']['people'])

        embed = Embed(color=config.COLOR)
        embed.set_author(name="ISS Info", icon_url="https://images-ext-1.discordapp.net/external/4YAoGmsd8-XPm09ASdxEsnHLpxaInoCvQguBk70Y7YQ/https/d30y9cdsu7xlg0.cloudfront.net/png/381875-200.png")
        embed.add_field(name="Location of the ISS now:", value=iss_location, inline=False)
        embed.add_field(name=f"Humans in Space ({data['astros']['number']}):", value=astros, inline=False)
        embed.set_image(url="http://www.businessforum.com/nasa01.JPEG")
        embed.set_footer(text=date)

        await channel.send(embed=embed)
