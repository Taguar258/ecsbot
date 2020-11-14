import util
from config.config import config
from datetime import datetime, timedelta

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