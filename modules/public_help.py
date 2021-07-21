from asyncio import sleep as asyc_sleep
from datetime import datetime

from config.config import config
from discord import Embed
from discord.ext import commands, tasks
from discord_slash import SlashContext, cog_ext
from discord_slash.utils.manage_commands import create_option
from modules import IgnoreException, db, parse_arguments


class PublicHelp(commands.Cog):
    """ Cog for public help system
    """
    def __init__(self, bot):

        self.bot = bot

    @tasks.loop(hours=1)
    @db.flock
    async def public_help_tick(self):
        """ Autodelete inactive channels
        """
        phelp_data = db["public_help"]["current_channels"]
        freeze = db["public_help"]["freeze"]

        for block in phelp_data:

            channel = self.bot.get_channel(block["channel"])
            fetch_message = await channel.history(limit=4).flatten()

            now = datetime.utcnow()
            delta = now - fetch_message[0].created_at

            if delta.days >= config.PHELP_REMEMBER_AFTER_DAY and \
               fetch_message[0].author.id != self.bot.user.id:

                # Warning
                await channel.send(f"Hey <@{block['user_id']}>, this channel will be automatically deleted in 2 days if not used by then.")

            elif delta.days >= config.PHELP_DELETE_AFTER_DAY and \
                    fetch_message[0].author.id == self.bot.user.id:

                # Delete Channel #
                end_data = []

                for block in phelp_data:

                    if block["channel"] != fetch_message[0].channel.id:

                        end_data.append(block)

                await channel.delete()

                db["public_help"] = {"current_channels": end_data, "freeze": freeze}

    @commands.Cog.listener()
    async def on_ready(self):
        """ Initialization
        """
        self.public_help_tick.start()

    async def tmp_msg(self, message_content, channel, reaction=config.REACT_ERROR, delete=1, delay=6):
        """ Send temporary message
        """
        info_msg = await channel.send(message_content)

        await info_msg.add_reaction(reaction)

        if delete:

            await asyc_sleep(delay)

            await info_msg.delete()

        return info_msg

    async def table(self, channel, data, embed=None):
        """ Send data as debug information in form of a table
        """
        if len(data) == 0:

            return await self.tmp_msg("No data available.", channel, delete=0)

        for test in data.values():

            if len(test) == 0:

                return await self.tmp_msg("No data available.", channel, delete=0)

        if embed is None:

            embed = Embed(color=config.COLOR)

        for key, value in data.items():

            embed.add_field(name=key, value="\n".join(value), inline=True)

        return await channel.send(embed=embed)

    async def request_permission(self, output_channel, channel, author, client, args):
        """ Validate selection by asking for message
        """
        if "-y" not in args:

            req_quest_msg = await output_channel.send("Please answer with 'YES' if you would like to close and delete your temporary channel.")

            for _ in range(4):

                try:

                    req_msg = await client.wait_for('message', timeout=5)

                    break

                except TimeoutError:

                    await self.tmp_msg("Timeout was raised.", output_channel)

                    raise IgnoreException

            if req_msg.author != author or req_msg.content != "YES" or req_msg.channel.id != channel.id:

                await self.tmp_msg("Message has not been answered with YES.\nYou could try again using the -y argument to bypass this step.", channel, delay=10)

                raise IgnoreException

            await req_quest_msg.delete()
            await req_msg.delete()

    @cog_ext.cog_slash(

        name="new",
        options=[

            create_option(

                name="title",
                description="Describe your issue in less than three words.",
                option_type=3,
                required=True,

            )

        ],

    )
    @db.flock
    async def new(self, ctx: SlashContext, title):
        """ Create a new help channel
        """
        # args = parse_arguments(ctx.message.content)

        # await ctx.message.delete()

        category = self.bot.get_channel(config.PHELPCATEGORY)

        phelp_data = db["public_help"]["current_channels"]
        freeze = db["public_help"]["freeze"]

        # Check for valid request
        if freeze:

            await self.tmp_msg("This feature is currently locked.", ctx)

            return

        if config.PHELP_MUTE_ROLE in [role.id for role in ctx.author.roles]:

            await self.tmp_msg("You don't have permission to use this feature.", ctx)

            return

        # if not args.check(0):

        #     await self.tmp_msg("Please supply a title.", ctx.message.channel)

        #     return

        # title = " ".join(args[0:])

        if len(title) > config.PHELP_MAX_TITLE:

            await self.tmp_msg("Please supply a shorter title.", ctx)

            return

        for data in phelp_data:

            if data["user_id"] == ctx.author.id:

                await self.tmp_msg("You are only allowed to have one public help channel.", ctx)

                return

        if len(category.channels) >= config.PHELP_MAX_CHANNELS:

            await self.tmp_msg(f"Only {config.PHELP_MAX_CHANNELS} public help channels are allowed.", ctx)

            return

        for check_channel in category.channels:

            if check_channel.topic == str(ctx.author.id):

                await self.tmp_msg("You are only allowed to have one public help channel.", ctx)

                return

        # Creating new channel
        creating_msg = await ctx.send("Creating new channel please wait...")

        new_channel = await ctx.guild.create_text_channel(

            title,

            category=category,
            topic=str(ctx.author.id),
            reason="New help channel requested.",

        )

        await new_channel.send(f"This is your new channel: <@{ctx.author.id}>\nPlease explain your problem down below, so other users can help you.")

        await creating_msg.edit(content="Your new channel has been created.")

        await creating_msg.add_reaction(config.REACT_SUCCESS)

        # Writing Data #
        date = datetime.utcnow()

        phelp_data.append(

            {

                "user_id": ctx.author.id,
                "category": category.id,
                "channel": new_channel.id,
                "title": title,
                "year": date.year,
                "month": date.month,
                "day": date.day,
                "hour": date.hour,
                "minute": date.minute,
                "user_name": ctx.author.name,
                "guild": ctx.guild.id,

            }

        )

        db["public_help"] = {"current_channels": phelp_data, "freeze": freeze}

        await asyc_sleep(10)
        await creating_msg.delete()

    @cog_ext.cog_slash(

        name="close",
        options=[

            create_option(

                name="y_skip",
                description="-y option to skip permission request.",
                option_type=3,
                required=False,

            )

        ],

    )
    @db.flock
    async def close(self, ctx: SlashContext, y_skip=""):
        """ Close your public help channel
        """
        # args = parse_arguments(ctx.message.content)

        # await ctx.message.delete()

        phelp_data = db["public_help"]["current_channels"]
        freeze = db["public_help"]["freeze"]

        # Check for valid request
        if freeze:

            await self.tmp_msg("This feature is currently locked.", ctx)

            return

        list_for_check = []

        for data in phelp_data:

            list_for_check.append(str(data["user_id"]))

        if str(ctx.author.id) not in list_for_check:

            await self.tmp_msg("You did not create a channel: No channel to delete.", ctx)

            return

        # Ask for permission #
        await self.request_permission(ctx, ctx.channel, ctx.author, self.bot, [y_skip])

        # Delete Channel #
        end_data = []

        for block in phelp_data:

            if block["user_id"] == ctx.author.id:

                delete_channel_id = block["channel"]

            else:

                end_data.append(block)

        delete_channel = self.bot.get_channel(delete_channel_id)

        db["public_help"] = {"current_channels": end_data, "freeze": freeze}

        if delete_channel.topic == str(ctx.author.id):

            await delete_channel.delete(reason="Help channel deletion requested.")

        else:

            await self.tmp_msg("Fatal Exception author id does not match.", ctx)

            return

        await self.tmp_msg("Your channel has been successfully closed.", ctx, reaction=config.REACT_SUCCESS)

    @commands.command(pass_context=True)
    @commands.has_role(config.STAFFROLE)
    async def phlist(self, ctx):
        """ List show info about public help db
        """
        await ctx.message.delete()

        phelp_data = db["public_help"]["current_channels"]
        table_data = {"Channel": [], "User": []}

        for block in phelp_data:

            table_data["Channel"].append(f"<#{block['channel']}>")
            table_data["User"].append(block["user_name"])
            # table_data["Category"].append(client.get_channel(block["category"]).name.replace("─ Public Help ", "").split(" ")[0])

        new_info_msg = await self.table(ctx.message.channel, table_data)

        await asyc_sleep(13)
        await new_info_msg.delete()

    @commands.command(pass_context=True)
    @commands.has_role(config.MODROLE)
    @db.flock
    async def fclose(self, ctx):
        """ Force close public help channel
        """
        await ctx.message.delete()

        args = parse_arguments(ctx.message.content)

        phelp_data = db["public_help"]["current_channels"]
        freeze = db["public_help"]["freeze"]

        # Check for valid request
        if not args.check(0, re=r"^[0-9]*$"):

            await self.tmp_msg("Please supply a valid ID.", ctx.message.channel)

            return

        list_for_check = []

        for data in phelp_data:

            list_for_check.append(str(data["channel"]))

        if args[0] not in list_for_check:

            await self.tmp_msg("Please supply a valid ID.", ctx.message.channel)

            return

        # Ask for permission #
        await self.request_permission(ctx.message.channel, ctx.message.channel, ctx.message.author, self.bot, args)

        # Delete Channel #
        end_data = []

        for block in phelp_data:

            if str(block["channel"]) != args[0]:

                end_data.append(block)

            else:

                delete_channel_id = str(block["channel"])

        db["public_help"] = {"current_channels": end_data, "freeze": freeze}

        delete_channel = self.bot.get_channel(int(delete_channel_id))

        await delete_channel.delete(reason="Force deletion of help channel.")

        await self.tmp_msg("The channel has been deleted.", ctx.message.channel, reaction=config.REACT_SUCCESS)

    @commands.command(pass_context=True)
    @commands.has_role(config.MODROLE)
    @db.flock
    async def rename(self, ctx):
        """ Rename an existing help channel
        """
        args = parse_arguments(ctx.message.content)

        await ctx.message.delete()

        category = self.bot.get_channel(config.PHELPCATEGORY)

        phelp_data = db["public_help"]["current_channels"]
        freeze = db["public_help"]["freeze"]

        # Check for valid request
        if not args.check(0, re=r"^[0-9]*$"):

            await self.tmp_msg("Please supply a valid ID.", ctx.message.channel)

            return

        if int(args[0]) not in [data["channel"] for data in phelp_data]:

            await self.tmp_msg("Please supply a valid ID.", ctx.message.channel)

            return

        if not args.check(1):

            await self.tmp_msg("Please supply a title.", ctx.message.channel)

            return

        title = " ".join(args[1:])

        if len(title) > config.PHELP_MAX_TITLE:

            await self.tmp_msg("Please supply a shorter title.", ctx)

            return

        channel_id = [channel["channel"] for channel in phelp_data if channel["channel"] == int(args[0])][0]

        channel = self.bot.get_channel(channel_id)
        old_name = channel.name

        await channel.edit(name=title)

        info_msg = await ctx.message.channel.send(f"Channel successfully renamed from '{old_name}' to '{title}'.")

        await info_msg.add_reaction(config.REACT_SUCCESS)

        # Writing Data #
        date = datetime.utcnow()

        new_phelp_data = []

        for data in phelp_data:

            if data["channel"] != int(args[0]):

                new_phelp_data.append(data)

        phelp_data.append(

            {

                "user_id": ctx.author.id,
                "category": category.id,
                "channel": channel.id,
                "title": title,
                "year": date.year,
                "month": date.month,
                "day": date.day,
                "hour": date.hour,
                "minute": date.minute,
                "user_name": ctx.author.name,
                "guild": ctx.guild.id,

            }

        )

        db["public_help"] = {"current_channels": phelp_data, "freeze": freeze}

        await asyc_sleep(10)
        await info_msg.delete()

    @commands.command(pass_context=True)
    @commands.has_role(config.STAFFROLE)
    async def phinfo(self, ctx):
        """ Fetch info of specific channel
        """
        await ctx.message.delete()

        args = parse_arguments(ctx.message.content)

        phelp_data = db["public_help"]["current_channels"]

        table_data = {}

        # Check for valid request #
        if not args.check(0, re=r"^[0-9]*$"):

            await self.tmp_msg("Please supply a valid ID.", ctx.message.channel)

            return

        list_for_check = []

        for data in phelp_data:

            list_for_check.append(str(data["channel"]))

        if args[0] not in list_for_check:

            await self.tmp_msg("Please supply a valid ID.", ctx.message.channel)

            return

        for block in phelp_data:

            if str(block["channel"]) == args[0]:

                for key, value in block.items():

                    if key in table_data:

                        table_data[str(key)].append(str(value))

                    else:

                        table_data[str(key)] = [str(value)]

        new_info_msg = await self.table(ctx.message.channel, table_data)

        await asyc_sleep(15)
        await new_info_msg.delete()

    @commands.command(pass_context=True)
    @commands.has_role(config.DEVROLE)
    @db.flock
    async def phdbflush(self, ctx):
        """ Flush public_help db
        """
        await ctx.message.delete()

        db["public_help"] = config.DATA_FILES_EMPTY["public_help"]

        await self.tmp_msg("Successfully flushed data.", ctx.message.channel, reaction=config.REACT_SUCCESS)

    @commands.command(pass_context=True)
    @commands.has_role(config.MODROLE)
    @db.flock
    async def phfreeze(self, ctx):
        """ Lock public help system
        """
        await ctx.message.delete()

        args = parse_arguments(ctx.message.content)

        phelp_data = db["public_help"]["current_channels"]

        if not args.check(0, re=r"(on|off)"):

            await self.tmp_msg("No matching argument passed.", ctx.message.channel)

            return

        if args[0] == "on":

            freeze = True

        elif args[0] == "off":

            freeze = False

        db["public_help"] = {"current_channels": phelp_data, "freeze": freeze}

        await self.tmp_msg("Successfully applied.", ctx.message.channel, reaction=config.REACT_SUCCESS)

    @commands.command(pass_context=True)
    @commands.has_role(config.DEVROLE)
    async def phdb(self, ctx):
        """ Print db to chat (DEBUG)
        """
        await ctx.message.delete()

        with open("data/public_help.json", "r") as db:

            db = db.read()

        await self.tmp_msg(f'`{db}`', ctx.message.channel, reaction=config.REACT_SUCCESS, delay=15)


def setup(bot):
    """ On bot execute
    """
    bot.add_cog(PublicHelp(bot))
