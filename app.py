from base64 import b64encode
from datetime import datetime, timedelta

import discord
import modules.other as other
import modules.tick as tick
import util
from config.config import config
from discord.ext import tasks
from modules import exec_command

# import modules.moderation as moderation
# import modules.verification as verification

intents = discord.Intents.default()
intents.members = True
intents.typing = False
intents.presences = False

client = discord.Client(intents=intents)


@tasks.loop(minutes=1)
async def tickfunc():

    await tick.reminds(client)
    await tick.punishments(client)

    return


@tasks.loop(seconds=10)  # hours=1
async def public_help_tick():

    await tick.public_help(client)

    return


@client.event
async def on_ready():
    print("Bot is ready, " + client.user.name)
    await client.change_presence(status=discord.Status.online,
                                 activity=discord.Game(config.STATUS))
    util.init_data()
    # await tick()
    await other.membercount(client)
    tickfunc.start()
    public_help_tick.start()

    return


async def welcome_message(member):
    channel = client.get_channel(config.WELCOMEMSG_CHANNEL)

    msg = f"Hello <@{member.id}>!\nCheck out <#690216616163672136> to verify your account and start chatting, <#724238392723767357> to get answers to common questions and <#690219084469895225> to get special roles!"

    embed = discord.Embed(title="Welcome to Ethical Computing Society!", description=msg, color=config.COLOR)

    await channel.send(embed=embed)


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith(config.PREFIX):
        args = message.content.strip(config.PREFIX).split(" ")
        if not len(args):
            return
        command = args[0].lower()
        args.pop(0)
        await exec_command(message.author, message.channel, command, args, message.guild, client.latency, message, client)

    return


@client.event
async def on_raw_reaction_add(payload):
    guild = client.get_guild(payload.guild_id)
    member = guild.get_member(payload.user_id)
    reaction = b64encode(str(payload.emoji).encode())

    if config.ROLESMSG == payload.message_id and config.ROLESCHANNEL == payload.channel_id:
        if reaction in config.ROLES.keys():
            await member.add_roles(guild.get_role(config.ROLES[reaction][1]),
                                   reason="Added " + config.ROLES[reaction][0])

    return


@client.event
async def on_raw_reaction_remove(payload):
    guild = client.get_guild(payload.guild_id)
    member = guild.get_member(payload.user_id)
    reaction = b64encode(str(payload.emoji).encode())

    if config.ROLESMSG == payload.message_id and config.ROLESCHANNEL == payload.channel_id:
        if reaction in config.ROLES.keys():
            await member.remove_roles(guild.get_role(config.ROLES[reaction][1]),
                                      reason="Removed " + config.ROLES[reaction][0])
    return


@client.event
async def on_member_join(member):
    joinleave_channel = client.get_channel(config.JOINLEAVE_CHANNEL)

    guild = member.guild
    await util.sendDmEmbed(member, config.WELCOMEMSG)
    reminds = util.read_json("data/reminds.json")["reminds"]
    reminder = datetime.utcnow() + timedelta(hours=24)
    reminds.append({"year": reminder.year,
                    "month": reminder.month,
                    "day": reminder.day,
                    "hour": reminder.hour,
                    "minute": reminder.minute,
                    "userid": member.id,
                    "guild": guild.id,
                    "status": 0})
    util.write_json("data/reminds.json", {"reminds": reminds})
    punishments = util.read_json("data/punishments.json")["punishments"]
    for i in punishments:
        if i["userid"] == member.id and i["type"] == "mute":
            await member.add_roles(guild.get_role(config.MUTEDROLE),
                           reason="Mute after rejoin.")
            break
    await member.add_roles(guild.get_role(config.UNVERIFIEDROLE),
                           reason="Joined the server.")
    await other.membercount(client)

    await welcome_message(member)

    await joinleave_channel.send(f"<@{member.id}> joined.")

    return


@client.event
async def on_member_remove(member):
    joinleave_channel = client.get_channel(config.JOINLEAVE_CHANNEL)
    full_name = f"{member.name}#{member.discriminator}"

    reminds = util.read_json("data/reminds.json")["reminds"]
    endreminds = []
    for i in reminds:
        if i["userid"] != member.id:
            endreminds.append(i)
    util.write_json("data/reminds.json", {"reminds": endreminds})
    await other.membercount(client)

    await joinleave_channel.send(f"{full_name} left.")

    return


# Log events #
# https://cog-creators.github.io/discord-embed-sandbox/

@client.event
async def on_message_edit(before, after):

    if not after.author.bot:

        channel = client.get_channel(config.LOGCHANNEL)

        date = datetime.now().strftime("%d.%m.%Y")

        full_name = f"{after.author.name}#{after.author.discriminator}"
        full_title = f"**Message edited in** <#{after.channel.id}> [Jump to Message]({after.jump_url})"
        footer = f"User ID: {after.author.id} • {date}"

        embed = discord.Embed(description=full_title, color=config.COLOR)

        embed.set_author(name=full_name, icon_url=after.author.avatar_url)

        embed.add_field(name="Before", value=before.content, inline=False)
        embed.add_field(name="After", value=after.content, inline=False)
        embed.set_footer(text=footer)

        await channel.send(embed=embed)


@client.event
async def on_message_delete(message):

    if not message.author.bot and not message.content.startswith("/channel") and not message.content.startswith("/help"):

        channel = client.get_channel(config.LOGCHANNEL)

        date = datetime.now().strftime("%d.%m.%Y")

        full_name = f"{message.author.name}#{message.author.discriminator}"
        full_title = f"**Message sent by** <@{message.author.id}> **deleted in** <#{message.channel.id}>\n{message.content}"
        footer = f"Author: {message.author.id} | Message ID: {message.id} • {date}"

        embed = discord.Embed(description=full_title, color=config.COLOR)

        embed.set_author(name=full_name, icon_url=message.author.avatar_url)

        embed.set_footer(text=footer)

        await channel.send(embed=embed)


@client.event
async def on_member_update(before, after):

    if len(before.roles) < len(after.roles):

        for role in after.roles:

            if role not in before.roles:

                added_role = role

        channel = client.get_channel(config.LOGCHANNEL)

        date = datetime.now().strftime("%d.%m.%Y")

        full_name = f"{after.name}#{after.discriminator}"
        full_title = f"**The** `{added_role.name}` **role was given to** <@{after.id}>"
        footer = f"ID: {after.id} • {date}"

        embed = discord.Embed(description=full_title, color=config.COLOR)

        embed.set_author(name=full_name, icon_url=after.avatar_url)

        embed.set_footer(text=footer)

        await channel.send(embed=embed)

    elif len(before.roles) > len(after.roles):

        for role in before.roles:

            if role not in after.roles:

                removed_role = role

        channel = client.get_channel(config.LOGCHANNEL)

        date = datetime.now().strftime("%d.%m.%Y")

        full_name = f"{after.name}#{after.discriminator}"
        full_title = f"**The** `{removed_role.name}` **role was removed from** <@{after.id}>"
        footer = f"ID: {after.id} • {date}"

        embed = discord.Embed(description=full_title, color=config.COLOR)

        embed.set_author(name=full_name, icon_url=after.avatar_url)

        embed.set_footer(text=footer)

        await channel.send(embed=embed)


client.run(config.TOKEN)
