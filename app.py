import discord
from config import config
import commands
from base64 import b64encode
from datetime import datetime, timedelta
from discord.ext import tasks
import util

intents = discord.Intents.default()
intents.members = True
intents.typing = False
intents.presences = False

client = discord.Client(intents=intents)


async def reminds():
    reminds = util.read_json("data/reminds.json")["reminds"]
    now = datetime.utcnow()
    endreminds = []
    for i in reminds:
        guild = client.get_guild(i["guild"])
        member = guild.get_member(i["userid"])
        reminder = datetime(i["year"], i["month"], i["day"],
                            i["hour"], i["minute"], 0, 0)
        if now > reminder:
            if i["status"] in [0, 1]:
                await util.sendDmEmbed(member, config.REMINDERMSG)
                print("Reminded",i["userid"],i["status"])
                newremind = reminder + timedelta(hours=24)
                endreminds.append({"year": newremind.year, 
                                   "month": newremind.month,
                                   "day": newremind.day, 
                                   "hour": newremind.hour,
                                   "minute": newremind.minute, 
                                   "userid": i["userid"],
                                   "guild": i["guild"],
                                   "status": i["status"] + 1})
            else:
                await util.sendDmEmbed(member, config.KICKMSG)
                print("Kicked",i["userid"],i["status"])
                try:
                    await member.kick(reason="Didn't verify.")
                except AttributeError:
                    pass
        else:
            endreminds.append(i)
    util.write_json("data/reminds.json", {"reminds": endreminds})
    return

async def punishments():
    bancache = {}
    punishments = util.read_json("data/punishments.json")["punishments"]
    now = datetime.utcnow()
    endpunishments = []
    for i in punishments:
        if i["guild"] not in bancache.keys():
            guild = client.get_guild(i["guild"])
            bancache[i["guild"]] = await guild.bans()
        bans = bancache[i["guild"]]
        member = guild.get_member(i["userid"])
        for j in bans:
            if j.user.id == i["userid"]:
                member = j.user
        punishtime = datetime(i["year"], i["month"], i["day"],
                              i["hour"], i["minute"], 0, 0)
        if now > punishtime:
            if i["type"] == "mute":
                await util.sendDmEmbed(member, config.UNMUTEMSG)
                await util.log(member, guild, "Unmute", "'s mute has expired!")
                muterole = guild.get_role()
                await member.remove_roles(muterole)

            elif i["type"] == "ban":
                await util.log(member, guild, "Unban", "'s ban has expired!")
                await member.unban(reason="Ban expired.")
        else:
            endpunishments.append(i)
    util.write_json("data/punishments.json", {"punishments": endpunishments})
    return

async def membercount():
    guild = client.get_guild(config.GUILD)
    channel = guild.get_channel(config.MEMBERCOUNTCHANNEL)
    member_count_no_bots = 0
    async for i in guild.fetch_members():
        if not i.bot:
            member_count_no_bots += 1
    await channel.edit(name="Members: " + str(member_count_no_bots))
    return


@tasks.loop(minutes=1)
async def tick():

    await reminds()
    await punishments()

    return


@client.event
async def on_ready():
    print("Bot is ready, " + client.user.name)
    await client.change_presence(status=discord.Status.online,
                                 activity=discord.Game(config.STATUS))
    util.init_data()
    #await tick()
    await membercount()
    tick.start()
    return


async def exec_command(author, channel, command, args, guild):
    if guild.get_role(config.STAFFROLE) not in author.roles:
        return

    if command == "purge":
        await commands.purge(author, channel, guild, args)

    elif command in ["approve", "approved", "verify"]:
        await commands.verify(author, channel, guild, args)

    elif command == "vpurge":
        await commands.vpurge(author, channel, guild, args)

    elif command in ["denied", "deny", "reject"]:
        await commands.reject(author, channel, guild, args)
        
    elif command == "whois":
        await commands.whois(channel, guild, args)

    elif command in ["ban", "detain", "obliterate"]:
        await commands.ban(author, channel, guild, args)

    elif command in ["pardon", "unban"]:
        await commands.unban(author, channel, guild, args)

    elif command in ["mute", "slap"]:
        await commands.mute(author, channel, guild, args)

    elif command == "unmute":
        await commands.unmute(author, channel, guild, args)

    elif command in ["warn", "pewpew"]:
        await commands.warn(author, channel, guild, args)

    elif command in ["infractions", "modlogs", "punishments", "detentions"]:
        await commands.infractions(author, channel, guild, args)

    elif command in ["ping", "pong"]:
        await commands.ping(channel, client.latency)


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
        await exec_command(message.author, message.channel, command, args, message.guild)

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
    await membercount()
    return


@client.event
async def on_member_remove(member):
    reminds = util.read_json("data/reminds.json")["reminds"]
    endreminds = []
    for i in reminds:
        if i["userid"] != member.id:
           endreminds.append(i)
    util.write_json("data/reminds.json", {"reminds": endreminds})
    await membercount()
    return


client.run(config.TOKEN)
