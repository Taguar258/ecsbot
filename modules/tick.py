from datetime import datetime, timedelta

import util
from config.config import config


async def reminds(client):
    reminds = util.read_json("data/reminds.json")["reminds"]
    now = datetime.utcnow()
    endreminds = []
    for i in reminds:
        guild = client.get_guild(i["guild"])
        member = guild.get_member(i["userid"])
        reminder = datetime(i["year"], i["month"], i["day"],
                            i["hour"], i["minute"], 0, 0)
        if now > reminder:
            if i["status"] in [0, 1, 2]:  # [0, 1]
                await util.sendDmEmbed(member, config.REMINDERMSG)
                print("Reminded", i["userid"], i["status"])
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
                await util.log(member, guild, "Kick", "has been kicked for not verifying in time.")
                await util.sendDmEmbed(member, config.REMINDKICKMSG)
                print("Kicked", i["userid"], i["status"])
                try:
                    await member.kick(reason="Didn't verify.")
                except AttributeError:
                    pass
        else:
            endreminds.append(i)
    util.write_json("data/reminds.json", {"reminds": endreminds})
    return


async def punishments(client):
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


async def public_help(client):

    phelp_data = util.read_json("data/public_help.json")["current_channels"]
    freeze = util.read_json("data/public_help.json")["freeze"]

    for block in phelp_data:

        channel = client.get_channel(block["channel"])
        fetchMessage = await channel.history(limit=4).flatten()
        now = datetime.utcnow()
        delta = now - fetchMessage[0].created_at

        if delta.days >= config.PHELP_REMEMBER_AFTER_DAY and fetchMessage[0].author.id != client.user.id:
            await channel.send(f"Hey <@{block['user_id']}>, this channel will be automatically deleted in 2 days if not used by then.")

        elif delta.days >= config.PHELP_DELETE_AFTER_DAY and fetchMessage[0].author.id == client.user.id:
            # Delete Channel #
            end_data = []
            for block in phelp_data:
                if block["channel"] != fetchMessage[0].channel.id:
                    end_data.append(block)

            await channel.delete()
            util.write_json("data/public_help.json", {"current_channels": end_data, "freeze": freeze})
