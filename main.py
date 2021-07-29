#!/usr/bin/python3
from json import dump
from os import mkdir, path
from random import choice

import discord
from config.config import TESTING, config
from discord.ext import commands
from discord_slash import SlashCommand
from modules import IgnoreException, db

# Bot initialization
print("[Use 'C^' twice instead of using 'Z^']")

intents = discord.Intents.default()
intents.members = True
intents.typing = False
intents.presences = False

bot = commands.Bot(command_prefix=config.PREFIX, intents=intents)
slash = SlashCommand(bot, sync_commands=True)

# Bot extensions
bot_extensions = [

    "modules.debug",
    "modules.moderation",
    "modules.message_detection",
    "modules.vote_mute",
    "modules.anti_spam",
    "modules.verification",
    "modules.message_log",
    "modules.roles",
    "modules.cleanup",
    "modules.public_help",
    "modules.bump_reminder",
    "modules.crypto_challenge",
    "modules.iss",

]


def write_empty(data_name, json_columns):
    """ Write empty json data set
    """
    with open(f"data/{data_name}.json", "w") as json_file:

        dump(json_columns, json_file)


# Common events
@bot.event
async def on_ready():
    """ Write data if not existing
    """
    if not path.isdir("data"):

        mkdir("data")

        for json_file, json_columns in config.DATA_FILES_EMPTY.items():

            write_empty(json_file, json_columns)


@bot.event
async def on_command_error(ctx, error):
    """ Error handeling
    """
    if isinstance(error, commands.MissingRole):

        await ctx.message.channel.send("You do not have permission to run this command.")

    elif isinstance(error, commands.CommandNotFound):

        pass

    elif hasattr(error, "original") and \
            isinstance(error.original, IgnoreException):

        pass  # Ignore

    else:

        # Change bot status (see debug.py)
        await bot.change_presence(

            status=discord.Status.dnd,
            activity=discord.Activity(name=choice(config.MAD_STATUS), type=discord.ActivityType.competing)

        )

        raise error

# Bot load extensions
for extension in bot_extensions:

    print(f"[i] Loading {extension}...")

    bot.load_extension(extension)

print("[i] Modules loaded")

# Testing init
if TESTING:

    import tracemalloc

    tracemalloc.start()

# Run bot
db.catch(bot, bot.run, config.TOKEN)

# Testing output
if TESTING:

    current, peak = tracemalloc.get_traced_memory()

    print(f"\033[37mCurrent memory usage:\033[36m {current / 10**6}MB\033[0m")
    print(f"\033[37mPeak                :\033[36m {peak / 10**6}MB\033[0m")
