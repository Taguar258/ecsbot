# Taguar

from asyncio import sleep
from datetime import datetime

import util
from config.config import config
from discord import Embed


async def tmp_msg(message_content, channel, reaction=config.REACT_ERROR, delete=1, delay=6):

    info_msg = await channel.send(message_content)

    await info_msg.add_reaction(reaction)

    if delete:

        await sleep(delay)

        await info_msg.delete()

    return info_msg


async def table(channel, data, embed=None):

    if len(data) == 0:
        return await tmp_msg("No data available.", channel, delete=0)

    for test in data.values():
        if len(test) == 0:
            return await tmp_msg("No data available.", channel, delete=0)

    if embed is None:
        embed = Embed(color=config.COLOR)

    for key, value in data.items():
        embed.add_field(name=key, value="\n".join(value), inline=True)

    return await channel.send(embed=embed)


async def request_permission(channel, author, client, args):

    if "-y" not in args:

        req_quest_msg = await channel.send("Please answer with 'YES' if you would like to close and delete your temporary channel.")
        try:
            req_msg = await client.wait_for('message', timeout=10)
        except TimeoutError:
            await tmp_msg("Timeout was raised.", channel)
            return False

        if req_msg.author != author or req_msg.content != "YES" or req_msg.channel.id != channel.id:
            await tmp_msg("Message has not been answered with YES.\nYou could try again using the -y argument to bypass this step.", channel, delay=10)
            return False

        await req_quest_msg.delete()
        await req_msg.delete()

    return True


async def new_help(author, channel, guild, args, message, client):

    await message.delete()

    phelp_data = util.read_json("data/public_help.json")["current_channels"]
    freeze = util.read_json("data/public_help.json")["freeze"]

    category = config.PHELPCATEGORY

    author_roles = [role.id for role in author.roles]

    # Check for valid request #
    if freeze:
        await tmp_msg("This feature is currently locked.", channel)
        return

    if config.PHELP_MUTE_ROLE in author_roles:
        await tmp_msg("You don't have permission to use this feature.", channel)
        return

    if len(args) <= 1:
        await tmp_msg("Please supply a title.", channel)
        return

    title = " ".join(args[1:])

    if len(title) > config.PHELP_MAX_TITLE:
        await tmp_msg("Please supply a shorter title.", channel)
        return

    for data in phelp_data:
        if data["user_id"] == author.id:
            await tmp_msg("You are only allowed to have one public help channel.", channel)
            return

    if len(client.get_channel(category).channels) >= config.PHELP_MAX_CHANNELS:
        await tmp_msg(f"Only {config.PHELP_MAX_CHANNELS} public help channels are allowed.", channel)
        return

    for check_channel in client.get_channel(category).channels:
        if check_channel.topic == str(author.id):
            await tmp_msg("You are only allowed to have one public help channel.", channel)
            return

    # Creating new channel #
    creating_msg = await channel.send("Creating new channel please wait...")

    new_channel = await guild.create_text_channel(title, category=client.get_channel(category), topic=str(author.id), reason="New help channel requested.")
    await new_channel.send(f"This is your new channel: <@{author.id}>\nPlease explain your problem down below, so other users can help you.")
    success_msg = await channel.send("Your new channel has been created.")

    await creating_msg.delete()
    await success_msg.add_reaction(config.REACT_SUCCESS)

    # Writing Data #
    date = datetime.utcnow()
    phelp_data.append({"user_id": author.id,
                       "category": category,
                       "channel": new_channel.id,
                       "title": title,
                       "year": date.year,
                       "month": date.month,
                       "day": date.day,
                       "hour": date.hour,
                       "minute": date.minute,
                       "user_name": author.name,
                       "guild": guild.id})

    util.write_json("data/public_help.json", {"current_channels": phelp_data, "freeze": freeze})

    await sleep(10)
    await success_msg.delete()


async def close_help(author, channel, guild, args, message, client):

    await message.delete()

    phelp_data = util.read_json("data/public_help.json")["current_channels"]
    freeze = util.read_json("data/public_help.json")["freeze"]

    # Check for valid request #
    if freeze:
        await tmp_msg("This feature is currently locked.", channel)
        return

    list_for_check = []
    for data in phelp_data:
        list_for_check.append(str(data["user_id"]))

    if str(author.id) not in list_for_check:
        await tmp_msg("You did not create a channel: No channel to delete.", channel)
        return

    # Ask for permission #
    return_pass = await request_permission(channel, author, client, args)
    if return_pass is not True:
        return

    # Delete Channel #
    end_data = []
    for block in phelp_data:
        if block["user_id"] == author.id:
            delete_channel_id = block["channel"]
        else:
            end_data.append(block)

    delete_channel = client.get_channel(delete_channel_id)

    if delete_channel.topic == str(author.id):
        await delete_channel.delete(reason="Help channel deletion requested.")
    else:
        await tmp_msg("Fatal Exception author id does not match.", channel)
        return

    util.write_json("data/public_help.json", {"current_channels": end_data, "freeze": freeze})

    await tmp_msg("Your channel has been successfully closed.", channel, reaction=config.REACT_SUCCESS, delay=10)


async def list_help(author, channel, message, client):

    await message.delete()

    phelp_data = util.read_json("data/public_help.json")["current_channels"]
    table_data = {"Channel": [], "User": []}

    for block in phelp_data:
        table_data["Channel"].append("<#%s>" % block["channel"])
        table_data["User"].append(block["user_name"])
        # table_data["Category"].append(client.get_channel(block["category"]).name.replace("─ Public Help ", "").split(" ")[0])

    new_info_msg = await table(channel, table_data)
    await sleep(13)
    await new_info_msg.delete()


async def force_close_help(author, channel, guild, args, message, client):

    await message.delete()

    phelp_data = util.read_json("data/public_help.json")["current_channels"]
    freeze = util.read_json("data/public_help.json")["freeze"]

    # Check for valid request #
    if len(args) == 1:
        await tmp_msg("Please supply a valid ID.", channel)
        return

    list_for_check = []
    for data in phelp_data:
        list_for_check.append(str(data["channel"]))

    if args[1] not in list_for_check:
        await tmp_msg("Please supply a valid ID.", channel)
        return

    # Ask for permission #
    return_pass = await request_permission(channel, author, client, args)
    if return_pass is not True:
        return

    # Delete Channel #
    end_data = []
    for block in phelp_data:
        if str(block["channel"]) != args[1]:
            end_data.append(block)
        else:
            delete_channel_id = str(block["channel"])

    util.write_json("data/public_help.json", {"current_channels": end_data, "freeze": freeze})

    delete_channel = client.get_channel(int(delete_channel_id))
    await delete_channel.delete(reason="Force deletion of help channel.")

    await tmp_msg("The channel has been deleted.", channel, reaction=config.REACT_SUCCESS, delay=10)


async def info_help(author, channel, guild, args, message, client):

    await message.delete()

    phelp_data = util.read_json("data/public_help.json")["current_channels"]
    table_data = {}

    # Check for valid request #
    if len(args) == 1:
        await tmp_msg("Please supply a valid ID.", channel)
        return

    list_for_check = []
    for data in phelp_data:
        list_for_check.append(str(data["channel"]))

    if args[1] not in list_for_check:
        await tmp_msg("Please supply a valid ID.", channel)
        return

    for block in phelp_data:
        if str(block["channel"]) == args[1]:
            for key, value in block.items():
                if key in table_data:
                    table_data[str(key)].append(str(value))
                else:
                    table_data[str(key)] = [str(value)]

    new_info_msg = await table(channel, table_data)
    await sleep(15)
    await new_info_msg.delete()


async def help_help(channel, mod):
    if mod:
        help_message = config.HELP_MESSAGE_MODS
    else:
        help_message = config.HELP_MESSAGE_USER

    embed = Embed(description=" ", color=config.COLOR)

    for line in help_message.split("\n"):
        if line != "":
            part = line.split(" | ")
            embed.add_field(name=part[0], value=part[1], inline=False)
    msg = await channel.send(embed=embed)
    await sleep(15)
    await msg.delete()


async def flush_help(channel, message):

    await message.delete()

    flush_file = open("data/public_help.json", "w")
    flush_file.write('{"current_channels": [], "freeze": false}')
    flush_file.close()
    await tmp_msg("Successfully flushed data.", channel, reaction=config.REACT_SUCCESS, delay=10)


async def freeze_help(channel, args, message):

    await message.delete()

    phelp_data = util.read_json("data/public_help.json")["current_channels"]

    if len(args) == 1:
        await tmp_msg("No arguments passed.", channel)
        return

    if args[1] == "on":
        freeze = True

    elif args[1] == "off":
        freeze = False

    util.write_json("data/public_help.json", {"current_channels": phelp_data, "freeze": freeze})
    await tmp_msg("Successfully applied.", channel, reaction=config.REACT_SUCCESS, delay=10)


async def db_help(channel, message):

    await message.delete()

    with open("data/public_help.json", "r") as db:
        db = db.read()

    await tmp_msg(f'`{db}`', channel, reaction=config.REACT_SUCCESS, delay=15)
