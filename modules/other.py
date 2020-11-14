import discord

from config.config import config
import util

async def membercount(client):
    guild = client.get_guild(config.GUILD)
    channel = guild.get_channel(config.MEMBERCOUNTCHANNEL)
    member_count_no_bots = 0
    async for i in guild.fetch_members():
        if not i.bot:
            member_count_no_bots += 1
    await channel.edit(name="Members: " + str(member_count_no_bots))
    return


async def whois(channel, guild, args):
    member = await util.parse_member(args, guild)
    if member == None:
        await channel.send("Please supply a valid mention or ID.")
        return

    fullname = member.name + "#" + member.discriminator
    joinedstrf = member.joined_at.strftime("%d/%m/%Y %H:%M:%S")
    createdstrf = member.created_at.strftime("%d/%m/%Y %H:%M:%S")

    embed = discord.Embed(title=fullname, color=config.COLOR)

    embed.add_field(name="Nick", 
                    value=member.display_name, inline=True)
    embed.add_field(name="Username", 
                    value=fullname, inline=True)
    embed.add_field(name="Joined", 
                    value=joinedstrf, inline=False)
    embed.add_field(name="Created", 
                    value=createdstrf, inline=False)

    await channel.send(embed=embed)


async def ping(channel, ping):
    embed = discord.Embed(title="Ping", color=config.COLOR)

    embed.add_field(name="API", value=str(round(ping*1000)) + "ms", inline=True)
    await channel.send(embed=embed)
