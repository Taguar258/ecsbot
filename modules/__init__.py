import json
import pickle
from asyncio import sleep as async_sleep
from copy import deepcopy
from json import dump
from os import mkdir, path
# from functools import wraps
from re import finditer, match, sub
from time import sleep
from traceback import print_exc

from config.config import config
from discord import Embed, errors
from discord.ext import tasks
from discord.ext.commands import Context

# ----------- ARGUMENT PARSER -----------


class Parsed:
    """ Return of parse_arguments.
    Holds functions for common tasks.
    """
    def __init__(self, raw_content):

        self.raw = raw_content
        self.args = raw_content.split()[1:]

    def __getitem__(self, pos):

        return self.args[pos]

    def check(self, pos, re=""):
        """ Check if pos in args and if args matches pattern if provided
        """
        if len(self.args) >= pos + 1 and \
           ((not re) or \
           (re and match(re, self.args[pos]))):  # noqa: E128

            return True

        return False


def parse_arguments(content):
    """ Parsing arguments of message while removing command itself
    """
    raw_content = content

    for re_match in finditer(r"<.{1,2}\d*>", content):

        pos = re_match.span()

        raw_content = raw_content[:pos[0]] + sub(r"[^0-9]", "", re_match.group()) + raw_content[pos[1]:]

    return Parsed(raw_content)


# --------- END ARGUMENT PARSER -----------

# ----------- COMMON FUNCTIONS ------------

class IgnoreException(Exception): pass


async def check_for_id(ctx, args, ignore_errors=False):
    """ Check for user id or mention, otherwise send error message
    """
    if not args.check(0, re=r"^[0-9]*$"):

        await ctx.message.channel.send("Please supply a valid mention or ID.")

        raise IgnoreException

    try:

        member = await ctx.message.guild.fetch_member(args[0])

    except (errors.NotFound, errors.HTTPException):

        if not ignore_errors:

            await ctx.message.channel.send("Could not fetch member.")

            raise IgnoreException

        else:

            return None

    return member


async def check_for_role(ctx, member, target_role, target_action):
    """ Check if user has role
    """
    if target_role in [role.id for role in member.roles]:

        await ctx.message.channel.send(f"This user cannot be {target_action}.")

        raise IgnoreException


def get_full_name(member):
    """ Get full name: USERNAME#DISCRIMINATOR
    """
    return f"{member.name}#{member.discriminator}"


async def get_punishment_reason_length(ctx, args, punishments, member, strtotimestr, strtotimemin, sub_punishments, action_name):
    """ Return length and reason of punishment
    Raise Error if not defined.
    """
    if action_name[-1] == "e":

        action_name = action_name[:-1]

    for punishment in punishments:

        if punishment["userid"] == member.id and \
           punishment["type"] in sub_punishments:

            await ctx.message.channel.send(f"This user is already {action_name}ed!")

            raise IgnoreException

    if not args.check(1, re="|".join(strtotimemin.keys())):

        await ctx.message.channel.send(f"Invalid or no time period specified\n({', '.join(strtotimestr)})")

        raise IgnoreException

    timestr = strtotimestr[args[1]]
    time_in_minutes = strtotimemin[args[1]]

    if not args.check(2):

        await ctx.message.channel.send("No Reason specified.")

        raise IgnoreException

    return time_in_minutes, timestr

# --------- END COMMON FUNCTIONS ----------

# -------- COMMON SERVER FUNCTIONS --------


async def log(guild, author, title, message):
    """ Send an embed to the log channel
    """
    channel = guild.get_channel(config.LOGCHANNEL)

    embed = Embed(

        title=title,
        description=f"{author.mention} has {message}",
        color=config.COLOR

    )

    await channel.send(embed=embed)


async def send_embed_dm(member, embed):
    """ Send an embed to dm of member
    """
    try:

        embed_footer = embed.footer

        if isinstance(embed_footer.text, str):

            embed_footer.text += "\n[Messages sent here are being ignored]"

        else:

            embed_footer.text = "[Messages sent here are being ignored]"

        new_embed = deepcopy(embed)
        new_embed.set_footer(**embed_footer.__dict__)

        await member.send(embed=new_embed)

    except Exception:

        await member.send(embed=embed)

    except (errors.Forbidden, AttributeError, errors.HTTPException):

        pass  # dms disabled


# ------ END COMMON SERVER FUNCTIONS ------


# ------------- DATA HANDLER --------------

class FileLock(Exception): pass


class DataHandler:
    """ Save data in memory and periodiacally stores it on disk
        Prevents interfering of data by queueing functions
    """
    def __init__(self):

        # Init checks
        self._create_data_structure()

        # (Static) Variables
        self._data_files = config.DATA_FILES
        self._warning_threshold = 8  # On len(self._queue) warn user

        # (DYNAMIC) Queue Variables
        self._queue = []
        self._return_queue = {}

        # (DANYMIC) DATA
        self.data = self._read_from_disk()

        self._edited_data = {key: 0 for key in self.data.keys()}

    # Magic functions for data modification
    def __getitem__(self, data_name):
        """ Return data from memory
        """
        self.__check_data_exist(data_name)

        return self.data[data_name]

    def __setitem__(self, data_name, new_data):
        """ Write new data to memory
        """
        self.__check_data_exist(data_name)

        self.data[data_name] = new_data
        self._edited_data[data_name] = 1

    # Init data
    def __write_empty_data_entry(self, data_name, json_columns):
        """ Write empty json data set
        """
        with open(f"data/{data_name}.json", "w") as json_file:

            dump(json_columns, json_file)

    def _create_data_structure(self):
        """ Write and repair data structure if not existing
        """
        if not path.isdir("data"):

            mkdir("data")

        for json_file, json_columns in config.DATA_FILES_EMPTY.items():

            if not path.isfile(f"data/{json_file}.json"):

                self.__write_empty_data_entry(json_file, json_columns)

    # Checking functions
    def __check_data_exist(self, data_name):
        """ Check if data name in data files, otherwise throw error
        """
        if data_name not in self._data_files:

            raise KeyError("specified data does not exists")

    def _get_nested_items(self, input_type):
        """ Get all items of nested dict and list
            (written by Richard and dtc; added code myself)
        """
        if isinstance(input_type, dict):

            input_iter = input_type.values()

        elif isinstance(input_type, list):

            input_iter = input_type

        for nested in input_iter:

            if isinstance(nested, (dict, list)):

                yield from self._get_nested_items(nested)

            else:

                yield nested

    # Data-storing handeling
    def _write_to_disk(self):
        """ Write data from memory to disk
        """
        for file_name, file_data in self.data.items():

            if sum([0 if isinstance(value, (int, str, bool, float)) else 1 for value in self._get_nested_items(self.data)]):

                raise IndexError("cannot write object without return type")

            if self._edited_data[file_name]:

                with open(f"data/{file_name}.json", "w") as json_file:

                    json.dump(file_data, json_file)

    def _read_from_disk(self):
        """ Read data from disk to memory
        """
        data = {}

        for file_name in self._data_files:

            with open(f"data/{file_name}.json", "r") as json_file:

                data[file_name] = json.load(json_file)

        return data

    # Tasks of storing data to disk
    @tasks.loop(seconds=config.BACKUP_FREQUENCY)
    async def _auto_backup(self):
        """ Write data to disk using pickle in case of issues
        """
        with open("data/backup.pickle", "wb") as pickle_file:

            pickle.dump(self.data, pickle_file)

    @tasks.loop(seconds=config.SAVE_FREQUENCY)
    async def _auto_save(self):
        """ Write data to disk every x seconds
        """
        self._write_to_disk()

    # Safety catches
    def catch(self, bot, func, *argv):
        """ Save to disk if exception
        """
        self._auto_save.start()
        self._auto_backup.start()

        try:

            func(*argv)

            while True: sleep(100)

        except (Exception, KeyboardInterrupt):

            print("Exception/KeyBoardInterrupt: Saving Data...")

            self._write_to_disk()

            print_exc()

    # Main queue handeling
    @tasks.loop(seconds=1)
    async def _queue_handler(self):
        """ Queue handler
        """
        if len(self._queue) >= 1:

            # Remove last entry
            func = self._queue.pop(0)

            # Run function
            try:

                return_value = await func[0](*func[1][0], **func[1][1])

            except IgnoreException:

                pass

            finally:

                return_value = None

            # Send return values back to flock
            self._return_queue[func[0].__id__] = return_value

        else:

            # Stop loop for less cpu utilization
            self._queue_handler.stop()

    def flock(self, func):
        """ Decorator queueing functions
        """
        async def decorator_function(*args, **kwargs):
            """ Decorator Frame
            """
            # Setting unique id
            func.__id__ = str(id(func))

            # Warn user on long queue
            if len(self._queue) >= self._warning_threshold:

                for pos in [0, 1]:  # first argument might be self

                    if (len(args) - 1) >= pos and \
                       isinstance(args[pos], Context):

                        await args[pos].channel.send("Due to a long action queue, there might be some action delays.")

            # Run queue_handler if inactive
            if not self._queue_handler.is_running():

                self._queue_handler.start()

            self._queue.append([func, (args, kwargs)])

            # Wait for return
            while True:

                if func.__id__ in self._return_queue:

                    break

                else:

                    await async_sleep(1)

            # Return value and delete from return queue
            return_value = self._return_queue[func.__id__]
            del self._return_queue[func.__id__]

            return return_value

        # Change name to keep command name
        decorator_function.__name__ = func.__name__

        return decorator_function


db = DataHandler()

# ----------- END DATA HANDLER ------------
