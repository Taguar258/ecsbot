import discord
from base64 import b64encode
from datetime import datetime, timedelta
from discord.ext import tasks

from config.config import config
import modules.moderation as moderation
import modules.other as other
import modules.verification as verification
import modules.tick as tick
from modules import exec_command
import util

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


@client.event
async def on_ready():
    print("Bot is ready, " + client.user.name)
    await client.change_presence(status=discord.Status.online,
                                 activity=discord.Game(config.STATUS))
    util.init_data()
    #await tick()
    await other.membercount(client)
    tickfunc.start()
    return


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
        await exec_command(message.author, message.channel, command, args, message.guild, client.latency)

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
    await other.membercount(client)
    return


@client.event
async def on_member_remove(member):
    reminds = util.read_json("data/reminds.json")["reminds"]
    endreminds = []
    for i in reminds:
        if i["userid"] != member.id:
           endreminds.append(i)
    util.write_json("data/reminds.json", {"reminds": endreminds})
    await other.membercount(client)
    return


client.run(config.TOKEN)
