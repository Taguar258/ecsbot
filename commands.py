import discord
from config import config
import util
from datetime import datetime, timedelta


async def purge(author, channel, guild, args):

    await channel.send("Purging, please wait...")

    for i in guild.channels:
        if i.type == discord.ChannelType.text:
            await i.purge(check=lambda m: m.author.id == int(args[0]))
    
    await util.log(author, guild, "Purge", " has purged all messages from <@" + args[0] + ">")

    await channel.send("Done, if not all messages were affected re-do!")


async def verify(author, channel, guild, args):
    member = await util.parse_member(args, guild)
    if member == None:
        await channel.send("Please supply a valid mention or ID.")
        return

    verifiedrole = guild.get_role(config.VERIFIEDROLE)
    unverifiedrole = guild.get_role(config.UNVERIFIEDROLE)

    await member.add_roles(verifiedrole, 
                            reason="Verified by a moderator.")

    await member.remove_roles(unverifiedrole, 
                                reason="Verified by a moderator.")

    await channel.send("Successfully verified " + member.mention + "!")
    await util.log(author, guild, "Verification", " has verified " + member.mention)

    reminds = util.read_json("data/reminds.json")["reminds"]
    endreminds = []

    for i in reminds:
        if i["userid"] != int(args[0]):
            endreminds.append(i)

    util.write_json("data/reminds.json", {"reminds": endreminds})


async def vpurge(author, channel, guild, args):
    category = guild.get_channel(config.VERIFICATIONCHANNELCAT)

    for i in category.channels:
        if i.type == discord.ChannelType.text and i.name == config.VERIFICATIONCHANNELNAME:
            await i.delete()

    overwrites = {
        guild.get_role(config.UNVERIFIEDROLE): 
            discord.PermissionOverwrite(read_messages=True, 
                                        send_messages=True, 
                                        read_message_history=True),
        guild.get_role(config.STAFFROLE): 
            discord.PermissionOverwrite(read_messages=True, 
                                        send_messages=True, 
                                        read_message_history=True),
        guild.get_role(config.VERIFIEDROLE): 
            discord.PermissionOverwrite(read_messages=False, 
                                        send_messages=False, 
                                        read_message_history=False),
    }
    vchannel = await guild.create_text_channel(config.VERIFICATIONCHANNELNAME, 
                                                category=category,
                                                overwrites=overwrites,
                                                topic="Verify yourself to get access to the " \
                                                      "other channels and be able to communicate " \
                                                      "with others.")
    await vchannel.send(config.VERIFICATIONCHANNELMESSAGE)
    await util.log(author, guild, "Verification Purge", " has purged the #verification channel!")
    await channel.send("Successfully purged the verification channel!")


async def reject(author, channel, guild, args):
    if len(args) == 0 or not args[0].isdigit():
        await channel.send("Please supply a valid ID.")
        return

    member = guild.get_member(int(args[0]))
    await util.sendDmEmbed(member, config.DENIEDMSG)
    await member.ban(reason="Verification denied by a moderator.")
    await util.log(author, guild, "Reject", " has rejected " + member.mention)
    await channel.send("Successfully denied " + member.mention + "!")


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


async def ban(author, channel, guild, args):
    fullname = author.name + "#" + author.discriminator

    member = await util.parse_member(args, guild)
    if member == None:
        await channel.send("Please supply a valid mention or ID.")
        return

    punishments = util.read_json("data/punishments.json")["punishments"]
    for i in punishments:
        if i["userid"] == member.id and i["type"] == "ban":
            await channel.send("This User is already banned!")
            return

    strtotimestr = {"1d": "1 day", "7d": "7 days", "30d": "30 days",
                    "perma": "permanently", "permanent": "permanently", 
                    "permanently": "permanently"}
    strtotimemin = {"1d": 1440, "7d": 10080, "30d": 43200, "perma": 999999999}

    if len(args) == 1 or args[1] not in  strtotimemin.keys():
        await channel.send("Invalid or no time period specified" +
                     "\n(1d, 7d, 30d, perma)")
        return
    
    timestr = strtotimestr[args[1]]
    time_in_minutes = strtotimemin[args[1]]

    if len(args) == 2:
        await channel.send("No Reason specified")
        return

    reason = ""

    for i in args[2:]:
        reason += i 
        reason += " "

    embed = config.BANMSG
    embed.add_field(name="Reason", 
                    value=reason)
    embed.add_field(name="Duration", 
                    value=timestr)
    await util.sendDmEmbed(member, embed)

    await util.log(author, guild, "Ban", " has banned " + member.mention + " for " +
                              timestr + ". Reason: " + reason)
    await member.ban(reason="Banned by " + fullname)

    endtime = datetime.utcnow() + timedelta(minutes=time_in_minutes)
    punishments.append({"year": endtime.year, 
                        "month": endtime.month,
                        "day": endtime.day, 
                        "hour": endtime.hour,
                        "minute": endtime.minute, 
                        "userid": member.id,
                        "guild": guild.id,
                        "type": "ban"})
    util.write_json("data/punishments.json", {"punishments": punishments})

    now = datetime.utcnow()
    logs = util.read_json("data/logs.json")["logs"]
    logs.append({"year": now.year, 
                 "month": now.month,
                 "day": now.day, 
                 "hour": now.hour,
                 "minute": now.minute, 
                 "userid": member.id,
                 "guild": guild.id,
                 "duration": args[1],
                 "reason": reason,
                 "type": "ban"})
    util.write_json("data/logs.json", {"logs": logs})


    await channel.send("Successfully banned " + member.mention + "!")
    

async def mute(author, channel, guild, args):
    fullname = author.name + "#" + author.discriminator

    member = await util.parse_member(args, guild)
    if member == None:
        await channel.send("Please supply a valid mention or ID.")
        return

    punishments = util.read_json("data/punishments.json")["punishments"]
    for i in punishments:
        if i["userid"] == member.id:
            await channel.send("This User is already muted!")
            return

    strtotimestr = {"30m": "30 minutes", "1d": "1 day", "7d": "7 days", 
                    "perma": "permanently", "permanent": "permanently", 
                    "permanently": "permanently"}
    strtotimemin = {"30m": 30, "1d": 1440, "7d": 10080, "perma": 999999999}

    if len(args) == 1 or args[1] not in strtotimemin.keys():
        await channel.send("Invalid or no time period specified" +
                     "\n(30m, 1d, 7d, perma)")
        return
    
    timestr = strtotimestr[args[1]]
    time_in_minutes = strtotimemin[args[1]]

    if len(args) == 2:
        await channel.send("No Reason specified")
        return

    reason = ""

    for i in args[2:]:
        reason += i 
        reason += " "

    embed = config.MUTEMSG
    embed.add_field(name="Reason", 
                    value=reason)
    embed.add_field(name="Duration", 
                    value=timestr)
    await util.sendDmEmbed(member, embed)

    await util.log(author, guild, "Mute", " has muted " + member.mention + " for " +
                               timestr + ". Reason: " + reason)
    muterole = guild.get_role(config.MUTEDROLE)
    await member.add_roles(muterole, reason="Muted by " + fullname)

    endtime = datetime.utcnow() + timedelta(minutes=time_in_minutes)
    punishments.append({"year": endtime.year, 
                        "month": endtime.month,
                        "day": endtime.day, 
                        "hour": endtime.hour,
                        "minute": endtime.minute, 
                        "userid": member.id,
                        "guild": guild.id,
                        "type": "mute"})
    util.write_json("data/punishments.json", {"punishments": punishments})

    now = datetime.utcnow()
    logs = util.read_json("data/logs.json")["logs"]
    logs.append({"year": now.year, 
                 "month": now.month,
                 "day": now.day, 
                 "hour": now.hour,
                 "minute": now.minute, 
                 "userid": member.id,
                 "guild": guild.id,
                 "duration": args[1],
                 "reason": reason,
                 "type": "mute"})
    util.write_json("data/logs.json", {"logs": logs})

    await channel.send("Successfully muted " + member.mention + "!")


async def unban(author, channel, guild, args):
    fullname = author.name + "#" + author.discriminator
    member = await util.parse_member_banlist(args, guild)
    if member == None:
        await channel.send("Please supply a valid mention or ID of a banned user.")
        return
    
    await util.log(author, guild, "Unban", " has unbanned " + member.mention)
    await member.unban(reason="Unbanned by " + fullname)
    
    punishments = util.read_json("data/punishments.json")["punishments"]
    endpunishments = []
    for i in punishments:
        if i["userid"] != member.id or i["type"] != "ban":
            endpunishments.append(i)
    util.write_json("data/punishments.json", {"punishments": endpunishments})
    await channel.send("Successfully unbanned " + member.mention + "!")


async def unmute(author, channel, guild, args):
    fullname = author.name + "#" + author.discriminator

    member = await util.parse_member(args, guild)
    if member == None:
        await channel.send("Please supply a valid mention or ID.")
        return

    muted = False

    punishments = util.read_json("data/punishments.json")["punishments"]

    for i in punishments:
        if i["userid"] == member.id and i["type"] == "mute":
            muted = True
        
    if not muted:
        await channel.send("This user isnt muted " + member.mention + "!")
        return

    await util.sendDmEmbed(member, config.UNMUTEMSG)
    await util.log(author, guild, "Unmute", " has unmuted " + member.mention)
    muterole = guild.get_role(config.MUTEDROLE)
    await member.remove_roles(muterole, reason="Unmuted by " + fullname)

    endpunishments = []
    for i in punishments:
        if i["userid"] != member.id or i["type"] != "mute":
            endpunishments.append(i)
    util.write_json("data/punishments.json", {"punishments": endpunishments})
    await channel.send("Successfully unmuted " + member.mention + "!")


async def warn(author, channel, guild, args):
    member = await util.parse_member(args, guild)
    if member == None:
        await channel.send("Please supply a valid mention or ID.")
        return

    reason = ""

    for i in args[1:]:
        reason += i 
        reason += " "

    now = datetime.utcnow()
    logs = util.read_json("data/logs.json")["logs"]
    logs.append({"year": now.year, 
                 "month": now.month,
                 "day": now.day, 
                 "hour": now.hour,
                 "minute": now.minute, 
                 "userid": member.id,
                 "guild": guild.id,
                 "reason": reason,
                 "type": "warn"})
    util.write_json("data/logs.json", {"logs": logs})

    embed = config.WARNMSG
    embed.add_field(name="Reason", 
                    value=reason)
    await util.sendDmEmbed(member, embed)

    await util.log(author, guild, "Warn", " has warned " + member.mention + 
                             ". Reason: " + reason)

    await channel.send("Successfully warned " + member.mention + "!")
    pass


async def infractions(author, channel, guild, args):
    member = await util.parse_member(args, guild)
    if member == None:
        await channel.send("Please supply a valid mention or ID.")
        return

    fullname = member.name + "#" + member.discriminator


    embed = discord.Embed(title=fullname, color=config.COLOR)

    logs = util.read_json("data/logs.json")["logs"]

    for i in logs:
        if i["userid"] == member.id:
            if i["type"] == "warn":
                embed.add_field(name=i["type"].capitalize(), 
                                value=f"Time: {i['day']}/{i['month']}/{i['year']} " + 
                                    f"{i['hour']}:{i['minute']}\n" +
                                    f"Reason: {i['reason']}",
                                inline=False)
            else:
                embed.add_field(name=i["type"].capitalize(), 
                                value=f"Time: {i['day']}/{i['month']}/{i['year']} " + 
                                    f"{i['hour']}:{i['minute']}\n" +
                                    f"Reason: {i['reason']}\n" +
                                    f"Duration: {i['duration']}" ,
                                inline=False)
    
    await channel.send(embed=embed)
    pass

