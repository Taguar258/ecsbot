import discord
import util
from config.config import config


async def verify(author, channel, guild, args):
    member = await util.parse_member(args, guild)
    if member is None:
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
        if i["userid"] != member.id:
            endreminds.append(i)

    util.write_json("data/reminds.json", {"reminds": endreminds})


async def reject(author, channel, guild, args):
    member = await util.parse_member(args, guild)
    if member == None:
        await channel.send("Please supply a valid mention or ID.")
        return

    await util.sendDmEmbed(member, config.DENIEDMSG)
    await member.ban(reason="Verification denied by a moderator.")
    await util.log(author, guild, "Reject", " has rejected " + member.mention)
    await channel.send("Successfully denied " + member.mention + "!")


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
