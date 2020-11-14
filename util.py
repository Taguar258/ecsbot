import json
from discord import errors, Embed
from config import config
import os


async def sendDmEmbed(member, embed):
    try:
        await member.send(embed=embed)
    except (errors.Forbidden, AttributeError):
        pass # dms disabled
    return


def write_json(filename, data):
    with open(filename, 'w') as json_file:
        json.dump(data, json_file)
    return


def read_json(filename):
    with open(filename, 'r') as json_file:
        data = json.load(json_file)
    return data


async def log(author, guild, title, message):
    channel = guild.get_channel(config.LOGCHANNEL)
    embed = Embed(title=title, 
                  description=author.mention + " " + message,
                  color=0x57008b)
    await channel.send(embed=embed)
    return


async def parse_member(args, guild):
    if len(args) == 0:
        return None
    mention_or_id = args[0]
    if mention_or_id.isdigit():
        return guild.get_member(int(mention_or_id))
    else:
        mention_or_id = mention_or_id.strip("<@!").strip("<@").strip(">")
        if mention_or_id.isdigit():
            return guild.get_member(int(mention_or_id))
        else:
            return None

async def parse_member_banlist(args, guild):
    bans = await guild.bans()

    if len(args) == 0:
        return None

    mention_or_id = args[0]
    if mention_or_id.isdigit():
        userid = int(mention_or_id)
    else:
        userid = mention_or_id.strip("<@!").strip("<@").strip(">")
        if userid.isdigit():
            userid = int(userid)
        else:
            return None

    for i in bans:
        if i.user.id == userid:
            return i.user

def init_data():
    if not os.path.isdir("data"):
        os.mkdir("data")
        write_json("data/logs.json", {"logs": []})
        write_json("data/punishments.json", {"punishments": []})
        write_json("data/reminds.json", {"reminds": []})
    return 
