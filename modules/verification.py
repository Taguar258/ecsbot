from datetime import datetime, timedelta

import discord
from config.config import config
from discord.ext import commands, tasks
from modules import check_for_id, db, log, parse_arguments, send_embed_dm


class Verification(commands.Cog):
    """ Cog for old verification system
    """
    def __init__(self, bot):

        self.bot = bot

    @tasks.loop(hours=2)  # minutes=1
    @db.flock
    async def reminder_tick(self):
        """ Auto kick inactive users and warn them
        """
        time_now = datetime.utcnow()

        reminds = db["reminds"]["reminds"]

        endreminds = []
        for reminder in reminds:

            guild = self.bot.get_guild(reminder["guild"])
            member = guild.get_member(reminder["userid"])
            reminder_dt = datetime(

                reminder["year"],
                reminder["month"],
                reminder["day"],
                reminder["hour"],
                reminder["minute"],
                0,
                0,

            )

            if time_now > reminder_dt:

                if reminder["status"] in [0, 1, 2]:  # [0, 1]

                    await send_embed_dm(member, config.REMINDERMSG)

                    newremind = reminder_dt + timedelta(hours=24)

                    endreminds.append(

                        {

                            "year": newremind.year,
                            "month": newremind.month,
                            "day": newremind.day,
                            "hour": newremind.hour,
                            "minute": newremind.minute,
                            "userid": member.id,
                            "guild": guild.id,
                            "status": reminder["status"] + 1,

                        }
                    )

                else:

                    await log(guild, member, "Kick", "been kicked for not verifying in time.")
                    await send_embed_dm(member, config.REMINDKICKMSG)

                    try:

                        await member.kick(reason="Didn't verify.")

                    except AttributeError:

                        print("[w] Reminder kicking failed")

            else:

                endreminds.append(reminder)

        db["reminds"] = {"reminds": endreminds}

    @commands.Cog.listener()
    async def on_ready(self):
        """ Initialization
        """
        self.reminder_tick.start()

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

            guild.get_role(config.UNVERIFIEDROLE):

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
            topic="Verify yourself to get access to the " \
                  "other channels and be able to communicate " \
                  "with others.")

        await vchannel.send(config.VERIFICATIONCHANNELMESSAGE)

    @commands.Cog.listener()
    @db.flock
    async def on_member_join(self, member):
        """ Send information to user and add set reminder
        """
        # Welcome message
        channel = self.bot.get_channel(config.WELCOMEMSG_CHANNEL)

        msg = f"Hello <@{member.id}>!\nCheck out <#690216616163672136> to verify your account and start chatting, <#724238392723767357> to get answers to common questions and <#690219084469895225> to get special roles!"

        embed = discord.Embed(

            title="Welcome to Ethical Computing Society!",
            description=msg,
            color=config.COLOR,

        )

        await channel.send(embed=embed)

        # DM
        await send_embed_dm(member, config.WELCOMEMSG)

        # Reminder
        reminds = db["reminds"]["reminds"]

        reminder = datetime.utcnow() + timedelta(hours=24)

        reminds.append(

            {

                "year": reminder.year,
                "month": reminder.month,
                "day": reminder.day,
                "hour": reminder.hour,
                "minute": reminder.minute,
                "userid": member.id,
                "guild": member.guild.id,
                "status": 0,

            }

        )

        db["reminds"] = {"reminds": reminds}

        # Add unverified role
        await member.add_roles(

            member.guild.get_role(config.UNVERIFIEDROLE),

            reason="Joined the server."

        )

    @commands.Cog.listener()
    @db.flock
    async def on_member_remove(self, member):
        """ On member left
        """
        reminds = db["reminds"]["reminds"]

        endreminds = []

        for reminder in reminds:

            if reminder["userid"] != member.id:

                endreminds.append(reminder)

        db["reminds"] = {"reminds": endreminds}

    @commands.command(pass_context=True)
    @commands.has_role(config.STAFFROLE)
    @db.flock
    async def verify(self, ctx):
        """ Remove unverified role from user and append member role
        """
        args = parse_arguments(ctx.message.content)

        member = await check_for_id(ctx, args)

        verifiedrole = ctx.message.guild.get_role(config.VERIFIEDROLE)
        unverifiedrole = ctx.message.guild.get_role(config.UNVERIFIEDROLE)

        await member.add_roles(

            verifiedrole,

            reason="Verified by a moderator."

        )

        await member.remove_roles(

            unverifiedrole,

            reason="Verified by a moderator."

        )

        await ctx.message.channel.send(f"Successfully verified {member.mention}!")

        await log(ctx.message.guild, ctx.message.author, "Verification", f"verified {member.mention}")

        # Remove data entry
        reminds = db["reminds"]["reminds"]

        endreminds = []

        for reminder in reminds:

            if reminder["userid"] != member.id:

                endreminds.append(reminder)

        db["reminds"] = {"reminds": endreminds}

    @commands.command(pass_context=True)
    @commands.has_role(config.STAFFROLE)
    @db.flock
    async def deny(self, ctx):
        """ Ban users due to verification denial
        """
        args = parse_arguments(ctx.message.content)

        member = await check_for_id(ctx, args)

        await send_embed_dm(member, config.DENIEDMSG)

        await member.ban(reason="Verification denied by a moderator.")

        await log(ctx.message.guild, ctx.message.author, "Reject", f"rejected {member.mention}")

        await ctx.message.channel.send(f"Successfully denied {member.mention}!")

        # Remove data entry
        reminds = db["reminds"]["reminds"]

        endreminds = []

        for reminder in reminds:

            if reminder["userid"] != member.id:

                endreminds.append(reminder)

        db["reminds"] = {"reminds": endreminds}

    @commands.command(pass_context=True)
    @commands.has_role(config.STAFFROLE)
    async def vpurge(self, ctx):
        """ Purge verification channel by deleting and recreating it

        Verification channel will be always at the bottom of the verification category.

        """
        category = ctx.message.guild.get_channel(config.VERIFICATIONCHANNELCAT)

        # Delete channel
        for channel in category.channels:

            if channel.type == discord.ChannelType.text and \
               channel.name == config.VERIFICATIONCHANNELNAME:

                await channel.delete()

        # Create new channel
        overwrites = {

            ctx.message.guild.get_role(config.UNVERIFIEDROLE):

            discord.PermissionOverwrite(

                read_messages=True,
                send_messages=True,
                read_message_history=True,

            ),

            ctx.message.guild.get_role(config.STAFFROLE):

            discord.PermissionOverwrite(

                read_messages=True,
                send_messages=True,
                read_message_history=True,

            ),

            ctx.message.guild.get_role(config.VERIFIEDROLE):

            discord.PermissionOverwrite(

                read_messages=False,
                send_messages=False,
                read_message_history=False,

            ),

            ctx.message.guild.get_role(config.NOVERIFIEDROLE):

            discord.PermissionOverwrite(

                read_messages=False,
                send_messages=False,
                read_message_history=False,

            ),

            ctx.message.guild.get_role(config.BOTLISTINGROLE):

            discord.PermissionOverwrite(

                read_messages=False,
                send_messages=False,
                read_message_history=False,

            ),

        }

        vchannel = await ctx.message.guild.create_text_channel(

            config.VERIFICATIONCHANNELNAME,

            category=category,
            overwrites=overwrites,
            topic="Verify yourself to get access to the " \
                  "other channels and be able to communicate " \
                  "with others.")

        await vchannel.send(config.VERIFICATIONCHANNELMESSAGE)

        await log(ctx.message.guild, ctx.message.author, "Verification Purge", "purged the #verification channel!")

        await ctx.message.channel.send("Successfully purged the verification channel!")


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
        channel = self.bot.get_channel(config.WELCOMEMSG_CHANNEL)

        msg = f"Hello <@{member.id}>!\nCheck out <#724238392723767357> to get answers to common questions and <#690219084469895225> to get special roles!"

        embed = discord.Embed(

            title="Welcome to Ethical Computing Society!",
            description=msg,
            color=config.COLOR,

        )

        await channel.send(embed=embed)

        # DM
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
