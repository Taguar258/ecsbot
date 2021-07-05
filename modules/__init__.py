import json
from asyncio import coroutine
from asyncio import sleep as async_sleep
from re import finditer, match, sub
from time import sleep
from traceback import format_stack, print_exc

from config.config import config
from discord import Embed, errors

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


async def check_for_id(ctx, args):
    """ Check for user id or mention, otherwise send error message
    """
    if not args.check(0, re=r"^[0-9]*$"):

        await ctx.message.channel.send("Please supply a valid mention or ID.")

        raise IgnoreException

    try:

        member = await ctx.message.guild.fetch_member(args[0])

    except (errors.NotFound, errors.HTTPException):

        await ctx.message.channel.send("Could not fetch member.")

        raise IgnoreException

    return member


async def check_for_role(ctx, member, target_role, target_action):
    """ Check if user has role
    """
    if target_role in [role.id for role in member.roles]:

        await ctx.send(f"This user cannot be {target_action}.")

        # raise IgnoreException
        return True

    return False


def get_full_name(member):
    """ Get full name: USERNAME#DISCRIMINATOR
    """
    return f"{member.name}#{member.discriminator}"


async def get_punishment_reason_length(ctx, args, db, punishments, member, strtotimestr, strtotimemin, sub_punishments, action_name):
    """ Return length and reason of punishment
    Raise Error if not defined.
    """
    if action_name[-1] == "e":

        action_name = action_name[:-1]

    for punishment in punishments:

        if punishment["userid"] == member.id and \
           punishment["type"] in sub_punishments:

            db.unlock("punishments")

            await ctx.message.channel.send(f"This user is already {action_name}ed!")

            raise IgnoreException

    if not args.check(1, re="|".join(strtotimemin.keys())):

        db.unlock("punishments")

        await ctx.message.channel.send(f"Invalid or no time period specified\n({', '.join(strtotimestr)})")

        raise IgnoreException

    timestr = strtotimestr[args[1]]
    time_in_minutes = strtotimemin[args[1]]

    if not args.check(2):

        db.unlock("punishments")

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

    return


async def send_embed_dm(member, embed):
    """ Send an embed to dm of member
    """
    try:

        await member.send(embed=embed)

    except (errors.Forbidden, AttributeError):

        pass  # dms disabled

    return

# ------ END COMMON SERVER FUNCTIONS ------


# ------------- DATA HANDLER --------------

class FileLock(Exception): pass


class DataHandler:
    """ Save data in memory and periodiacally stores it on disk
    Should catch process interrupts too.

    TODO: Add lock for file rather than all data
    """
    def __init__(self):

        # Static Variables
        self._save_frequency = 30  # seconds
        self._delay = 1
        self._iter_timeout = round(90 // self._delay)  # 1.5 min

        self._data_files = config.DATA_FILES

        # Dynamic Variables
        self._file_lock = {file: False for file in self._data_files}
        self._last_lock = None  # Security warning due to file lock rewrite

        self.data = self._read_from_disk()

        self._edited_data = {key: 0 for key in self.data.keys()}

    def __getitem__(self, data_name):
        """ Return data from memory
        """
        self.__check_data_exist(data_name)

        return self.data[data_name]

    def __setitem__(self, data_name, new_data):
        """ Write new data to memory
        """
        if self._last_lock == data_name:

            pass

        elif self._last_lock is None:

            raise FileLock(f"no data lock for {new_data} data")

        elif self._last_lock is not new_data:

            raise FileLock(f"data lock not matching with {new_data} data")

        else:

            raise FileLock

        self.__check_data_exist(data_name)

        self.data[data_name] = new_data
        self._edited_data[data_name] = 1

    def __check_data_exist(self, data_name):
        """ Check if data name in data files, otherwise throw error
        """
        if data_name not in self._data_files:

            raise KeyError("specified data does not exists")

    def _write_to_disk(self):
        """ Write data from memory to disk
        """
        for file_name, file_data in self.data.items():

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

    @coroutine
    async def _auto_save(self):
        """ Write data to disk every x seconds
        """
        while True:

            await async_sleep(self._save_frequency)

            self._write_to_disk()

    def catch(self, bot, func, *argv):
        """ Save to disk if exception
        """
        bot.loop.create_task(self._auto_save())

        try:

            func(*argv)

            while True: sleep(100)

        except (Exception, KeyboardInterrupt):

            print("Exception/KeyBoardInterrupt: Saving Data...")

            self._write_to_disk()

            print_exc()

    async def lock(self, data_name):
        """ Lock file (only one process at a time)
        """
        if self._last_lock is not None:

            print("-------------------------------------")
            print("".join(format_stack()[:-1]))
            print(f"File: {self._last_lock}\n")
            print("[w] Unlock last file before locking new one")
            print("-------------------------------------")

        for _ in range(self._iter_timeout):  # Might cause issues if qeue too long

            if self._file_lock[data_name]:

                await async_sleep(self._delay)

            else:

                break

        if self._file_lock[data_name]:
            print("[w] File lock timeout")

        self._file_lock[data_name] = True
        self._last_lock = data_name

    def unlock(self, data_name):
        """ Unlock file
        """
        if self._last_lock == data_name or \
           self._last_lock is None:

            pass

        elif data_name not in self._file_lock.keys():

            raise KeyError

        elif self._last_lock != data_name:  # Maybe unnecessary

            print("-------------------------------------")
            print("".join(format_stack()[:-1]))
            print(f"File: {self._last_lock}\n")
            print("[w] Unlock last file before relocking")
            print("-------------------------------------")

        elif self._last_lock is not None:

            print("-------------------------------------")
            print("".join(format_stack()[:-1]))
            print(f"File: {self._last_lock}\n")
            print("[w] Unlock last file")
            print("-------------------------------------")

        self._file_lock[data_name] = False
        self._last_lock = None

    def write(self, data_name, new_data):
        """ Write new data to memory
        """
        self.__setitem__(data_name, new_data)

    def read(self, data_name):
        """ Function calls self.__getitem__()
        """
        return self.__getitem__(data_name)


db = DataHandler()

# ----------- END DATA HANDLER ------------
