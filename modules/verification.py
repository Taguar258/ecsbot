from asyncio import sleep as async_sleep
from datetime import datetime, timedelta
from io import BytesIO

import discord
from config.config import config
from discord.ext import commands, tasks
from modules import check_for_id, db, log, parse_arguments, send_embed_dm


class Verification(commands.Cog):
    """ Cog for old verification system
    """
    def __init__(self, bot):

        self.bot = bot

        self._reaction_message_id = None

    async def _store_transcript(self, channel, author_name):
        """ fetch and store a transcript of a channel
        """
        # fetch the messages
        await channel.send("Fetching messages for transcript...")

        messages = await channel.history(limit=None).flatten()

        # check for user interaction
        if not any(message.author.name == author_name for message in messages):

            return

        # prepare data
        data = ["---- TRANSCRIPT START ----"]  # additional information
        data += [

                f"{message.author.name} ({message.created_at.strftime('%H:%M')}): {message.clean_content}"

            for message in reversed(messages)

        ]
        data += ["---- TRANSCRIPT END ----"]

        # create new transcript
        date = datetime.now().date().strftime('%y-%m-%d_%H:%M:%S')
        transcript_name = f"transcript_{author_name}_{channel.name}_{date}.txt"
        transcript_file = discord.File(
            BytesIO(
                b'\n'.join([buf.encode() for buf in data])
            ),
            filename=transcript_name,
        )

        # store transcript
        guild = self.bot.get_guild(config.GUILD)
        transcript_channel = guild.get_channel(config.VTICKET_TRANSCRIPT_CHANNEL)

        await transcript_channel.send(f"{author_name} ({channel.name})", file=transcript_file)

    @tasks.loop(hours=2)
    async def auto_inactivity_close_tick(self):
        """ automatically close inactive vtickets
        """
        # iterate through open tickets
        guild = self.bot.get_guild(config.GUILD)
        category = guild.get_channel(config.VERIFICATIONCHANNELCAT)

        for channel in category.channels:

            if channel.type == discord.ChannelType.text and \
               channel.name.startswith("vticket-"):

                # fetch ticket creator
                member = await guild.fetch_member(channel.name[8:])
                
                # get delta of last sent message time
                utc_now = datetime.utcnow()
                fetch_last_message = (await channel.history(limit=1).flatten())[0]
                time_delta = utc_now - fetch_last_message.created_at

                # check message for reminder or inactivity
                reminder_msg = config.VTICKET_AUTOCLOSEREMINDER.replace(

                    "{mention}",
                    f"<@{member.id}>"

                )

                # check for reminder
                if fetch_last_message.author.id == self.bot.user.id and \
                   fetch_last_message.content == reminder_msg and \
                   time_delta.days >= config.VTICKET_AUTOCLOSE_DAY:

                    await self._store_transcript(channel, member.name)
                    await channel.delete(reason="vticket closed due to inactivity")

                # check for inactivity
                elif time_delta.days >= config.VTICKET_AUTOCLOSEREMINDER_DAY:

                    await channel.send(reminder_msg)

    @commands.Cog.listener()
    async def on_ready(self):
        """ Initialization
        """
        # Delete channel
        guild = self.bot.get_guild(config.GUILD)

        category = guild.get_channel(config.VERIFICATIONCHANNELCAT)

        for channel in category.channels:

            if (channel.type == discord.ChannelType.text) and \
               (channel.name == config.VERIFICATIONCHANNELNAME or \
               channel.name == config.NOVERIFICATION_CHANNELNAME):

                await channel.delete()

        # Create new channel
        overwrites = {

            guild.default_role:  # everyone

            discord.PermissionOverwrite(

                read_messages=True,
                send_messages=False,
                read_message_history=True,
                add_reactions=False,

            ),

            guild.get_role(config.STAFFROLE):

            discord.PermissionOverwrite(

                read_messages=True,
                send_messages=True,
                read_message_history=True,

            ),

            guild.get_role(config.VERIFIEDROLE):

            discord.PermissionOverwrite(

                read_messages=False,
                send_messages=False,
                read_message_history=False,

            ),

            guild.get_role(config.NOVERIFIEDROLE):

            discord.PermissionOverwrite(

                read_messages=False,
                send_messages=False,
                read_message_history=False,

            ),

            guild.get_role(config.BOTLISTINGROLE):

            discord.PermissionOverwrite(

                read_messages=False,
                send_messages=False,
                read_message_history=False,

            ),

        }

        vchannel = await guild.create_text_channel(

            config.VERIFICATIONCHANNELNAME,

            category=category,
            overwrites=overwrites,
            topic="Open ticket for verification"

        )

        info_message = await vchannel.send(config.VERIFICATIONCHANNELMESSAGE)

        await info_message.add_reaction(config.REACT_VERIFICATION)

        self._reaction_message_id = info_message.id

        # start scheuduled tasks
        if not self.auto_inactivity_close_tick.is_running():

            self.auto_inactivity_close_tick.start()

    async def _create_channel(self, member):
        """ open new ticket
        """
        # Create new channel
        guild = self.bot.get_guild(config.GUILD)
        category = guild.get_channel(config.VERIFICATIONCHANNELCAT)

        overwrites = {

            guild.default_role:  # everyone

            discord.PermissionOverwrite(

                read_messages=False,
                send_messages=False,

            ),

            member:  # member who opened ticket

            discord.PermissionOverwrite(

                read_messages=True,
                send_messages=True,
                read_message_history=True,

            ),

            guild.get_role(config.STAFFROLE):

            discord.PermissionOverwrite(

                read_messages=True,
                send_messages=True,
                read_message_history=True,

            ),

            guild.get_role(config.VERIFIEDROLE):

            discord.PermissionOverwrite(

                read_messages=False,
                send_messages=False,
                read_message_history=False,

            ),

            guild.get_role(config.NOVERIFIEDROLE):

            discord.PermissionOverwrite(

                read_messages=False,
                send_messages=False,
                read_message_history=False,

            ),

            guild.get_role(config.VTICKET_MEDIA_ROLE):

            discord.PermissionOverwrite(

                attach_files=True,

            ),

            guild.get_role(config.BOTLISTINGROLE):

            discord.PermissionOverwrite(

                read_messages=False,
                send_messages=False,
                read_message_history=False,

            ),

        }

        new_ticket_channel = await guild.create_text_channel(

            f"vticket-{member.id}",

            category=category,
            overwrites=overwrites,
            topic=f"ticket for member: {member.id}"

        )

        await new_ticket_channel.send(f"G'day {member.mention}, this is your new verification channel. Please stand by as a <@&690212787087081554> will arrive in no time.")

        # ask user a couple of question beforehand
        async with new_ticket_channel.typing():

            await async_sleep(3)
            await new_ticket_channel.send("Nonetheless, I'd like to ask a couple of questions in advance so that moderators can verify you more quickly.")
            await async_sleep(5)
            await new_ticket_channel.send("`1. What made you join this computer science server (or in general a CS server)?`")
            await async_sleep(3)
            await new_ticket_channel.send("`2. What are your areas of interest?`")
            await async_sleep(3)
            await new_ticket_channel.send("Thank you in advance for taking the time to verify yourself.")
            await async_sleep(3)
            await new_ticket_channel.send("This verification process is mandatory, thus please answer the questions above, so we don't have to ask again. :)")

    def _get_vticket_channel(self, user_id):
        """ get verification channel for user id
            exception: return None
        """
        # try to get user channel
        target_channel = None

        guild = self.bot.get_guild(config.GUILD)
        category = guild.get_channel(config.VERIFICATIONCHANNELCAT)

        for channel in category.channels:

            if channel.type == discord.ChannelType.text and \
               channel.name == f"vticket-{user_id}":

                target_channel = channel

        return target_channel

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """ create new channel on reaction
        """
        # check if reaction of interest
        if payload.emoji.name == config.REACT_VERIFICATION and \
           not payload.member.bot and \
           payload.message_id == self._reaction_message_id and \
           self._get_vticket_channel(payload.user_id) is None:

            guild = self.bot.get_guild(config.GUILD)
            member = guild.get_member(payload.user_id)
            await self._create_channel(member)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """ Send information to user and add set reminder
        """
        # Send welcome message
        await send_embed_dm(member, config.WELCOMEMSG)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """ close vticket channel of member if exists
        """
        # fetch vticket channel
        vticket_channel = self._get_vticket_channel(member.id)

        # delete vticket channel if exists
        if vticket_channel is not None:

            await self._store_transcript(vticket_channel, member.name)

            await vticket_channel.delete()

    @commands.command(pass_context=True)
    @commands.has_role(config.STAFFROLE)
    async def verify(self, ctx):
        """ append VERIFIEDROLE to vticket user of current channel
        """
        # check if command is run in vticket channel
        if not ctx.message.channel.name.startswith("vticket-"):

            await ctx.message.channel.send("Sorry, but this is not a vticket channel.")

            return

        # get user information
        user_id = int(ctx.message.channel.name[8:])
        member = await ctx.guild.fetch_member(user_id)

        verifiedrole = ctx.message.guild.get_role(config.VERIFIEDROLE)
        mediapermrole = ctx.message.guild.get_role(config.VTICKET_MEDIA_ROLE)

        await member.add_roles(

            verifiedrole,

            reason="verified by a moderator"

        )

        await self._store_transcript(ctx.message.channel, member.name)
        await ctx.message.channel.send(f"Successfully verified {member.mention}!\nThe ticket will close shortly...")
        await log(ctx.message.guild, ctx.message.author, "Verification", f"verified {member.mention}")
        await async_sleep(5)

        # delete channel
        await member.remove_roles(mediapermrole)
        await ctx.message.channel.delete()

        # inform user about verification complete
        await send_embed_dm(member, config.ACCEPTEDMSG)

    @commands.command(pass_context=True)
    @commands.has_role(config.STAFFROLE)
    # @db.flock
    async def deny(self, ctx):
        """ ban users due to verification denial
        """
        # check if command is run in vticket channel
        if not ctx.message.channel.name.startswith("vticket-"):

            await ctx.message.channel.send("Sorry, but this is not a vticket channel.")

            return

        # get user information
        user_id = int(ctx.message.channel.name[8:])
        member = await ctx.guild.fetch_member(user_id)

        # ban user
        await send_embed_dm(member, config.DENIEDMSG)
        await member.ban(reason="verification denied by a moderator", delete_message_days=0)
        await log(ctx.guild, ctx.author, "Reject", f"rejected {member.mention}")

        # # Write data
        # punishments = db["punishments"]["punishments"]

        # endtime = datetime.utcnow() + timedelta(days=14)

        # punishments.append(

        #     {

        #         "year": endtime.year,
        #         "month": endtime.month,
        #         "day": endtime.day,
        #         "hour": endtime.hour,
        #         "minute": endtime.minute,
        #         "userid": member.id,
        #         "guild": ctx.guild.id,
        #         "type": "ban",

        #     }

        # )

        # db["punishments"] = {"punishments": punishments}

        # # Write log
        # now = datetime.utcnow()

        # logs = db["logs"]["logs"]

        # logs.append(

        #     {

        #         "year": now.year,
        #         "month": now.month,
        #         "day": now.day,
        #         "hour": now.hour,
        #         "minute": now.minute,
        #         "userid": member.id,
        #         "guild": ctx.guild.id,
        #         "duration": "14d",
        #         "reason": "verification denied by moderator",
        #         "type": "ban"

        #     }

        # )

        # db["logs"] = {"logs": logs}

        # the channel will automatically delete due to on_member_remove

    @commands.command(pass_context=True)
    @commands.has_role(config.STAFFROLE)
    async def vclose(self, ctx):
        """ close vticket
        """
        # check if command is run in vticket channel
        if not ctx.message.channel.name.startswith("vticket-"):

            await ctx.message.channel.send("Sorry, but this is not a vticket channel.")

            return

        user_id = int(ctx.message.channel.name[8:])
        member = await ctx.guild.fetch_member(user_id)

        await self._store_transcript(ctx.message.channel, member.name)
        await log(ctx.message.guild, ctx.message.author, "Ticket closed", f"closed {ctx.message.channel.name}")
        await ctx.message.channel.send(f"The ticket will close shortly...")
        await async_sleep(5)

        # delete channel
        await ctx.message.channel.delete()


class NoVerification(commands.Cog):
    """ Cog temporarily disabling old verification system
    """
    def __init__(self, bot):

        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """ Delete verification channel and create new channel in case of failiure
        """
        guild = self.bot.get_guild(config.GUILD)
        category = guild.get_channel(config.VERIFICATIONCHANNELCAT)

        # Delete verification channel
        for channel in category.channels:

            if (channel.type == discord.ChannelType.text) and \
               (channel.name == config.VERIFICATIONCHANNELNAME or \
               channel.name == config.NOVERIFICATION_CHANNELNAME):

                await channel.delete()

        # Create failsafe channel
        overwrites = {

            guild.get_role(config.NOVERIFIEDROLE):

            discord.PermissionOverwrite(

                read_messages=False,
                send_messages=False,
                read_message_history=False,

            ),

            guild.get_role(config.VERIFIEDROLE):

            discord.PermissionOverwrite(

                read_messages=False,
                send_messages=False,
                read_message_history=False,

            ),

            guild.get_role(config.VERIFIEDROLE):

            discord.PermissionOverwrite(

                read_messages=False,
                send_messages=False,
                read_message_history=False,

            ),

            guild.default_role:

            discord.PermissionOverwrite(

                read_messages=True,
                send_messages=True,
                read_message_history=True,

            ),

            guild.get_role(config.STAFFROLE):

            discord.PermissionOverwrite(

                read_messages=True,
                send_messages=True,
                read_message_history=True,

            ),

            guild.get_role(config.BOTLISTINGROLE):

            discord.PermissionOverwrite(

                read_messages=False,
                send_messages=False,
                read_message_history=False,

            ),

        }

        vchannel = await guild.create_text_channel(

            config.NOVERIFICATION_CHANNELNAME,

            category=category,
            overwrites=overwrites,

        )

        # await vchannel.send("**Please contact us if you are not able to see all channels!\nOr try to rejoining later... sry :/**")

        embed = discord.Embed(

            title="You will need to do the steps shown by discord (accepting the rules).",
            description="In case you cannot access the channels even after doing these steps, please DM a moderator.\nYou can also request help here.",
            color=config.COLOR,

        )

        await vchannel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """ Send information to user
        """
        # Welcome message
        await send_embed_dm(member, config.NOVERIFICATION_WELCOMEMSG)

        # # Add member role | COMMENTED OUT: Due to rule screening
        # await member.add_roles(

        #     member.guild.get_role(config.NOVERIFIEDROLE),

        #     reason="Joined the server.",

        # )

    @commands.Cog.listener()
    async def on_member_update(self, _, member):
        """ Add NOVERIFIED role to rule screening verified members
        """
        if len(member.roles) <= 1 and \
           not member.pending:

            # Add member role
            await member.add_roles(

                member.guild.get_role(config.NOVERIFIEDROLE),

                reason="Accepted the rules.",

            )


def setup(bot):
    """ On bot execute
    """
    if config.VERIFICATIONENABLED:

        bot.add_cog(Verification(bot))

    else:

        bot.add_cog(NoVerification(bot))
