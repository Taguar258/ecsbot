import discord
from config import *
from base64 import b64encode
from datetime import datetime, timedelta
import json
from discord.ext import tasks
import asyncio

client = discord.Client()

guild = None


@client.event
async def on_ready():
    global guild
    print("Bot is ready, " + client.user.name)
    guild = client.get_guild(GUILD)
    await client.change_presence(status=discord.Status.online,
                                 activity=discord.Game(STATUS))
    reminder.start()
    return


def write_reminds(reminds):
    with open('reminds.json', 'w') as json_file:
        json.dump({"reminds": reminds}, json_file)
    return


def read_reminds():
    with open('reminds.json', 'r') as json_file:
        reminds = json.load(json_file)
    return reminds["reminds"]


@tasks.loop(minutes=1)
async def reminder():
    # [year, month, day, hour, minute, userid, status]
    reminds = read_reminds()
    now = datetime.now()
    endreminds = []
    for i in reminds:
        member = guild.get_member(i[5])
        reminder = datetime(i[0], i[1], i[2], i[3], i[4], 0, 0)
        if now > reminder:
            if i[6] in [0, 1]:
                await member.send(embed=REMINDERMSG)
                print("Reminded " + str(i[5]) + " " + str(i[6]))
                newremind = reminder + timedelta(hours=24)
                endreminds.append([newremind.year, newremind.month,
                                   newremind.day, newremind.hour,
                                   newremind.minute, i[5], i[6] + 1])
            else:
                await member.send(embed=KICKMSG)
                print("Kicked " + str(i[5]) + " " + str(i[6]))
                await member.kick(reason="Didn't accept the rules.")
        else:
            endreminds.append(i)
    write_reminds(endreminds)
    return


async def exec_command(author, channel, command, args):
    global guild
    if guild.get_role(STAFFROLE) not in author.roles:
        return
    if command == "purge":
        if len(args) == 0 or not args[0].isdigit():
            await channel.send("Please supply a valid ID.")
            return
        await channel.send("Purging, please wait...")
        for i in guild.channels:
            if str(i.type) == "text":
                await i.purge(check=lambda m: m.author.id == int(args[0]))
        await channel.send("Done, if not all messages were affected re-do!")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith(PREFIX):
        args = message.content.strip(PREFIX).split(" ")
        command = args[0]
        args.pop(0)

    await exec_command(message.author, message.channel, command, args)

    return


@client.event
async def on_raw_reaction_add(payload):
    member = guild.get_member(payload.user_id)
    reaction = b64encode(str(payload.emoji).encode())

    if RULESMSG == payload.message_id and RULESCHANNEL == payload.channel_id:
        if RULESREACTION == reaction:
            await member.add_roles(guild.get_role(VERIFIEDROLE),
                                   reason="Accepted the Rules!")
            await member.remove_roles(guild.get_role(UNVERIFIEDROLE),
                                      reason="Accepted the Rules!")
            reminds = read_reminds()
            endreminds = []
            for i in reminds:
                if i[5] != payload.user_id:
                    endreminds.append(i)
            write_reminds(endreminds)

    if ROLESMSG == payload.message_id and ROLESCHANNEL == payload.channel_id:
        if reaction in ROLES.keys():
            await member.add_roles(guild.get_role(ROLES[reaction][1]),
                                   reason="Added " + ROLES[reaction][0])
    return


@client.event
async def on_raw_reaction_remove(payload):
    member = guild.get_member(payload.user_id)
    reaction = b64encode(str(payload.emoji).encode())

    if ROLESMSG == payload.message_id and ROLESCHANNEL == payload.channel_id:
        if reaction in ROLES.keys():
            await member.remove_roles(guild.get_role(ROLES[reaction][1]),
                                      reason="Removed " + ROLES[reaction][0])
    return


@client.event
async def on_member_join(member):
    await member.send(embed=WELCOMEMSG)
    reminds = read_reminds()
    reminder = datetime.now() + timedelta(hours=24)
    reminds.append([reminder.year, reminder.month, reminder.day,
                    reminder.hour, reminder.minute, member.id, 0])
    write_reminds(reminds)
    return


@client.event
async def on_member_remove(member):
    reminds = read_reminds()
    endreminds = []
    for i in reminds:
        if i[5] != member.id:
            endreminds.append(i)
    write_reminds(endreminds)
    return


client.run(TOKEN)
