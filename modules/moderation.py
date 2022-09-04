from asyncio import sleep as async_sleep
from copy import deepcopy
from datetime import datetime, timedelta

import discord
from config.config import config
from discord.ext import commands, tasks
from modules import (check_for_id, check_for_role, db, get_full_name,
                     get_punishment_reason_length, log, parse_arguments,
                     send_embed_dm)


class Moderation(commands.Cog):
    """ Cog for moderation tasks
    """
    def __init__(self, bot):

        self.bot = bot

    @tasks.loop(minutes=3)  # minutes=1
    @db.flock
    async def punishment_tick(self):
        """ Handling of expired punishments
        """
        now = datetime.utcnow()
        guild = self.bot.get_guild(config.GUILD)

        punishments = db["punishments"]["punishments"]

        endpunishments = []

        for punishment in punishments:

            punishtime = datetime(

                punishment["year"],
                punishment["month"],
                punishment["day"],
                punishment["hour"],
                punishment["minute"],
                0,
                0,

            )

            if now > punishtime:

                user = await self.bot.fetch_user(punishment["userid"])
                member = guild.get_member(punishment["userid"])  # shouldn't fetch both

                if punishment["type"] == "mute" and \
                   member is not None:  # skip if user not member anymore

                    await send_embed_dm(member, config.UNMUTEMSG)
                    await log(guild, member, "Unmute", "been unmuted due to expiration!")

                    muterole = guild.get_role(config.MUTEDROLE)

                    await member.remove_roles(muterole)

                elif punishment["type"] == "ban":

                    await log(guild, user, "Unban", "been unbanned due to expiration!")

                    await guild.unban(user, reason="Ban expired.")

            else:

                endpunishments.append(punishment)

        db["punishments"] = {"punishments": endpunishments}

    @commands.Cog.listener()
    async def on_ready(self):
        """ Initialization
        """
        await async_sleep(1)  # Wait to hopefully prevent interfering

        self.punishment_tick.start()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """ Add mute to joining members with according punishment
        """
        punishments = db["punishments"]["punishments"]

        for punishment in punishments:

            if punishment["userid"] == member.id and \
               punishment["type"] == "mute":

                await member.add_roles(

                    member.guild.get_role(config.MUTEDROLE),

                    reason="Mute due to rejoining."

                )

                break

    @commands.command(pass_context=True)
    @commands.has_role(config.STAFFROLE)
    async def whois(self, ctx):
        """ Whois member lookup
        """
        args = parse_arguments(ctx.message.content)

        member = await check_for_id(ctx, args, ignore_errors=True)

        # check if not member and try to fetch user object
        if member is None:

            user = await self.bot.fetch_user(args[0])

            if user is None:

                await ctx.message.channel.send("Could not fetch user.")

                raise IgnoreException

            member = user

        # fetch member data
        fullname = get_full_name(member)

        # initialization of user device object
        class UserDevice:

            def __init__(self, member):

                self.desktop = member.desktop_status
                self.web = member.web_status
                self.mobile = member.mobile_status

                self.code = ""

                self.code += ("d" if self.desktop else "x")
                self.code += ("w" if self.web else "x")
                self.code += ("m" if self.mobile else "x")

            def __repr__(self):

                return f"<Device value={self.code}>"

        # embed generation
        embed = discord.Embed(title="Whois:", color=config.COLOR)

        if isinstance(member, discord.Member):

            device = UserDevice(member)

            information = {

                "Nick": member.nick,
                "Username": fullname,
                "Color": member.color,
                "Joined": member.joined_at.strftime("%d/%m/%Y %H:%M:%S"),
                "Created": member.created_at.strftime("%d/%m/%Y %H:%M:%S"),
                "Premium Since": ("None" if member.premium_since is None else member.premium_since.strftime("%d/%m/%Y %H:%M:%S")),
                "Device": device,
                "Pending": member.pending,
                "Top Role": member.top_role,
                "Roles": [role.name for role in member.roles],
                "Guild Permissions": member.guild_permissions,
                "Flags": {flag[0]: flag[1] for flag in member.public_flags},
                "Bot": member.bot,
                "Mention": member.mention,

            }

        elif isinstance(member, discord.User):

            information = {

                "Username": fullname,
                "Color": member.color,
                "Created": member.created_at.strftime("%d/%m/%Y %H:%M:%S"),
                "Flags": {flag[0]: flag[1] for flag in member.public_flags},
                "Bot": member.bot,
                "Mention": member.mention,

            }

        for name, value in information.items():

            embed.add_field(

                name=name,
                value=value,
                inline=False,

            )

        embed.set_author(name=fullname, icon_url=member.avatar_url)

        embed.set_footer(text=f"User ID: {member.id}")

        await ctx.send(embed=embed)

    @commands.command(pass_context=True)
    @commands.has_role(config.ROOTROLE)
    async def purge(self, ctx):
        """ Delete all messages of a specified user
        """
        args = parse_arguments(ctx.message.content)

        # Check
        member = await check_for_id(ctx, args, ignore_errors=True)

        not_in_guild = member is None
        if not_in_guild:

            member = await self.bot.fetch_user(args[0])

        if not not_in_guild:

            await check_for_role(ctx, member, config.STAFFROLE, "purged")

        # Main logic
        purging_info = await ctx.send("Purging...")

        for channel in ctx.message.guild.channels:

            if channel.type == discord.ChannelType.text:

                await channel.purge(check=(lambda m: m.author.id == int(member.id)))

        await log(ctx.guild, ctx.author, "Purge", f"purged all messages from {member.mention}")

        await purging_info.edit(content=f"Successfully purged {member.mention}, rerun if not all messages were affected.")

    @commands.command(pass_context=True)
    @commands.has_any_role(config.TRIALMODROLE, config.MODROLE)
    @db.flock
    async def mute(self, ctx):
        """ Mute user for certain amount of time
        """
        # Check stuff
        args = parse_arguments(ctx.message.content)

        # Check
        member = await check_for_id(ctx, args)

        await check_for_role(ctx, member, config.MODROLE, "muted")

        fullname = get_full_name(ctx.message.author)

        punishments = db["punishments"]["punishments"]

        strtotimestr = {

            "5m": "5 minutes",
            "30m": "30 minutes",
            "1h": "1 hour",
            "2h": "2 hours",
            "1d": "1 day",
            "2d": "2 days",
            "3d": "3 days",
            "5d": "5 days",
            "7d": "7 days",
            "perma": "permanently",

        }

        strtotimemin = {

            "5m": 5,
            "30m": 30,
            "1h": 60,
            "2h": 120,
            "1d": 1440,
            "2d": 2880,
            "3d": 4320,
            "5d": 7200,
            "7d": 10080,
            "perma": 999999999,

        }

        time_in_minutes, timestr = await get_punishment_reason_length(ctx, args, punishments, member, strtotimestr, strtotimemin, ["mute", "ban"], "mute")

        # Main logic
        reason = " ".join(args[2:])

        embed = deepcopy(config.MUTEMSG)

        embed.add_field(

            name="Reason",
            value=reason,

        )

        embed.add_field(

            name="Duration",
            value=timestr,

        )

        await send_embed_dm(member, embed)

        await log(ctx.message.guild, ctx.message.author, "Mute", f"muted {member.mention} for {timestr}. Reason: {reason}")

        muterole = ctx.message.guild.get_role(config.MUTEDROLE)

        await member.add_roles(muterole, reason=f"Muted by {fullname}")

        # Write data
        endtime = datetime.utcnow() + timedelta(minutes=time_in_minutes)

        punishments.append(

            {

                "year": endtime.year,
                "month": endtime.month,
                "day": endtime.day,
                "hour": endtime.hour,
                "minute": endtime.minute,
                "userid": member.id,
                "guild": ctx.message.guild.id,
                "type": "mute",

            }

        )

        db["punishments"] = {"punishments": punishments}

        # Write log
        now = datetime.utcnow()

        logs = db["logs"]["logs"]

        logs.append(

            {

                "year": now.year,
                "month": now.month,
                "day": now.day,
                "hour": now.hour,
                "minute": now.minute,
                "userid": member.id,
                "guild": ctx.message.guild.id,
                "duration": args[1],
                "reason": reason,
                "type": "mute",

            }

        )

        db["logs"] = {"logs": logs}

        # Send mention into mute-appeal
        mute_channel = self.bot.get_channel(config.MUTECHANNEL)
        await mute_channel.send(f"Sorry {member.mention}, you have been muted. Nonetheless, you have access to this hidden channel so that you can communicate with the server's moderators.")

        await ctx.message.channel.send(f"Successfully muted {member.mention}!")

    @commands.command(pass_context=True)
    @commands.has_role(config.MODROLE)
    @db.flock
    async def ban(self, ctx):
        """ Ban user for specific time and delete messages
        """
        args = parse_arguments(ctx.message.content)

        member = await check_for_id(ctx, args, ignore_errors=True)

        not_in_guild = member is None
        if not_in_guild:

            member = await self.bot.fetch_user(args[0])

        if not not_in_guild:

            await check_for_role(ctx, member, config.MODROLE, "banned")

        fullname = get_full_name(ctx.message.author)

        punishments = db["punishments"]["punishments"]

        strtotimestr = {

            "1d": "1 day",
            "2d": "2 days",
            "3d": "3 days",
            "5d": "5 days",
            "7d": "7 days",
            "14d": "14 days",
            "30d": "30 days",
            "60d": "60 days",
            "120d": "120 days",
            "240d": "240 days",
            "1y": "1 year",
            "perma": "permanently",

        }

        strtotimemin = {

            "1d": 1440,
            "2d": 2880,
            "3d": 4320,
            "5d": 7200,
            "7d": 10080,
            "14d": 20160,
            "30d": 43200,
            "60d": 86400,
            "120d": 172800,
            "240d": 345600,
            "1y": 525600,
            "perma": 999999999,

        }

        time_in_minutes, timestr = await get_punishment_reason_length(ctx, args, punishments, member, strtotimestr, strtotimemin, ["ban"], "ban")

        # Main logic
        reason = " ".join(args[2:])

        embed = deepcopy(config.BANMSG)

        embed.add_field(

            name="Reason",
            value=reason,

        )

        embed.add_field(

            name="Duration",
            value=timestr,

        )

        if not not_in_guild:

            await send_embed_dm(member, embed)

        await log(ctx.message.guild, ctx.message.author, "Ban", f"banned {member.mention} for {timestr}. Reason: {reason}")

        if not not_in_guild:

            await member.ban(reason=f"Banned by {fullname} for {timestr}. Reason: {reason}", delete_message_days=config.BANDELETEMESSAGES)

        else:

            await ctx.guild.ban(member)

        # Write data
        endtime = datetime.utcnow() + timedelta(minutes=time_in_minutes)

        punishments.append(

            {

                "year": endtime.year,
                "month": endtime.month,
                "day": endtime.day,
                "hour": endtime.hour,
                "minute": endtime.minute,
                "userid": member.id,
                "guild": ctx.message.guild.id,
                "type": "ban",

            }

        )

        db["punishments"] = {"punishments": punishments}

        # Write log
        now = datetime.utcnow()

        logs = db["logs"]["logs"]

        logs.append(

            {

                "year": now.year,
                "month": now.month,
                "day": now.day,
                "hour": now.hour,
                "minute": now.minute,
                "userid": member.id,
                "guild": ctx.message.guild.id,
                "duration": args[1],
                "reason": reason,
                "type": "ban"

            }

        )

        db["logs"] = {"logs": logs}

        await ctx.message.channel.send(f"Successfully banned {member.mention}!")

    @commands.command(pass_context=True)
    @commands.has_any_role(config.TRIALMODROLE, config.MODROLE)
    @db.flock
    async def unmute(self, ctx):
        """ Unmute muted member
        """
        args = parse_arguments(ctx.message.content)

        member = await check_for_id(ctx, args)

        fullname = get_full_name(ctx.message.author)

        punishments = db["punishments"]["punishments"]

        muted = False

        for punishment in punishments:

            if punishment["userid"] == member.id and \
               punishment["type"] == "mute":

                muted = True

        muterole = ctx.message.guild.get_role(config.MUTEDROLE)

        muted_role = config.MUTEDROLE in [role.id for role in member.roles]

        if not muted and muted_role:

            await member.remove_roles(muterole, reason="Unmuted by ")

            await ctx.message.channel.send(f"Successfully unmuted {member.mention}.")

            return

        elif not muted:

            await ctx.message.channel.send(f"The user {member.mention} is not muted.")

            return

        await member.remove_roles(muterole, reason=f"Unmuted by {fullname}")

        new_punishments = []

        for punishment in punishments:

            if punishment["userid"] != member.id or \
               punishment["type"] != "mute":

                new_punishments.append(punishment)

        db["punishments"] = {"punishments": new_punishments}

        await send_embed_dm(member, config.UNMUTEMSG)

        await log(ctx.message.guild, ctx.message.author, "Unmuted", f"unmuted {member.mention}")

        await ctx.message.channel.send(f"Successfully unmuted {member.mention}!")

    @commands.command(pass_context=True)
    @commands.has_role(config.MODROLE)
    @db.flock
    async def unban(self, ctx):
        """ Unban banned user
        """
        args = parse_arguments(ctx.message.content)

        if not args.check(0, re=r"^[0-9]*$"):

            await ctx.message.channel.send("Please supply a valid mention or ID.")

            return

        banned_users = [ban.user for ban in await ctx.message.guild.bans() if ban.user.id == int(args[0])]

        if len(banned_users) == 0:

            await ctx.message.channel.send("Please supply a valid mention or ID.")

            return

        user = banned_users[0]

        fullname = get_full_name(ctx.message.author)

        punishments = db["punishments"]["punishments"]

        banned = False

        for punishment in punishments:

            if punishment["userid"] == user.id and \
               punishment["type"] == "ban":

                banned = True

        server_banned = user.id in [ban.user.id for ban in await ctx.message.guild.bans()]

        if not banned and server_banned:

            await ctx.message.guild.unban(user, reason=f"Unbanned by {fullname}")

            await ctx.message.channel.send(f"Successfully unbanned {user.mention}.")

            return

        elif not banned:

            await ctx.message.channel.send(f"The user {user.mention} is not banned.")

            return

        await ctx.message.guild.unban(user, reason=f"Unmuted by {fullname}")

        new_punishments = []

        for punishment in punishments:

            if punishment["userid"] != user.id or \
               punishment["type"] != "ban":

                new_punishments.append(punishment)

        db["punishments"] = {"punishments": new_punishments}

        # await send_embed_dm(user, config.UNBANMSG)

        await log(ctx.message.guild, ctx.message.author, "Unbanned", f"unbanned {user.mention}")

        await ctx.message.channel.send(f"Successfully unbanned {user.mention}!")

    @commands.command(pass_context=True)
    @commands.has_any_role(config.TRIALMODROLE, config.MODROLE)
    @db.flock
    async def kick(self, ctx):
        """ Kick a member
        """
        args = parse_arguments(ctx.message.content)

        member = await check_for_id(ctx, args)

        await check_for_role(ctx, member, config.STAFFROLE, "kicked")

        fullname = get_full_name(ctx.message.author)

        # Main logic
        if not args.check(1):

            await ctx.message.channel.send("Please specify a reason.")

            return

        reason = " ".join(args[1:])

        now = datetime.utcnow()

        logs = db["logs"]["logs"]

        logs.append(

            {

                "year": now.year,
                "month": now.month,
                "day": now.day,
                "hour": now.hour,
                "minute": now.minute,
                "userid": member.id,
                "guild": ctx.message.guild.id,
                "reason": reason,
                "type": "kick",

            }

        )

        db["logs"] = {"logs": logs}

        embed = deepcopy(config.KICKMSG)

        embed.add_field(

            name="Reason",
            value=reason,

        )

        await send_embed_dm(member, embed)

        await log(ctx.message.guild, ctx.message.author, "Kick", f"kicked {member.mention}. Reason: {reason}")

        await member.kick(reason=f"Kicked by {fullname}")

        await ctx.message.channel.send(f"Successfully kicked {member.mention}!")

    @commands.command(pass_context=True)
    @commands.has_any_role(config.TRIALMODROLE, config.MODROLE)
    @db.flock
    async def warn(self, ctx):
        """ Warn a member
        """
        args = parse_arguments(ctx.message.content)

        member = await check_for_id(ctx, args)

        # Main logic
        if not args.check(1):

            await ctx.message.channel.send("Please specify a reason.")

            return

        reason = " ".join(args[1:])

        now = datetime.utcnow()

        logs = db["logs"]["logs"]

        logs.append(

            {

                "year": now.year,
                "month": now.month,
                "day": now.day,
                "hour": now.hour,
                "minute": now.minute,
                "userid": member.id,
                "guild": ctx.message.guild.id,
                "reason": reason,
                "type": "warn",

            }

        )

        db["logs"] = {"logs": logs}

        embed = deepcopy(config.WARNMSG)

        embed.add_field(

            name="Reason",
            value=reason,

        )

        await send_embed_dm(member, embed)

        await log(ctx.message.guild, ctx.message.author, "Warn", f"warned {member.mention}. Reason: {reason}")

        await ctx.message.channel.send(f"Successfully warned {member.mention}!")

    @commands.command(pass_context=True)
    @commands.has_role(config.STAFFROLE)
    async def modlog(self, ctx):
        """ Return moderation log of a member
        """
        args = parse_arguments(ctx.message.content)

        member = await check_for_id(ctx, args, ignore_errors=True)

        if member is None:  # TEST

            full_name = args[0]

        else:

            member = await self.bot.fetch_user(args[0])
            full_name = get_full_name(member)

        embed = discord.Embed(

            title=full_name,
            color=config.COLOR,

        )

        for log_entry in db["logs"]["logs"]:

            if log_entry["userid"] == int(args[0]):

                if log_entry["type"] in ["warn", "kick"]:

                    embed.add_field(

                        name=log_entry["type"].capitalize(),
                        value=(

                            f"Time: {log_entry['day']}/{log_entry['month']}/{log_entry['year']} " + \
                            f"{log_entry['hour']}:{log_entry['minute']}\n" + \
                            f"Reason: {log_entry['reason']}"

                        ),

                        inline=False,

                    )

                else:

                    embed.add_field(

                        name=log_entry["type"].capitalize(),
                        value=(

                            f"Time: {log_entry['day']}/{log_entry['month']}/{log_entry['year']} " + \
                            f"{log_entry['hour']}:{log_entry['minute']}\n" + \
                            f"Reason: {log_entry['reason']}\n" + \
                            f"Duration: {log_entry['duration']}"

                        ),

                        inline=False,

                    )

        await ctx.message.channel.send(embed=embed)

    @commands.command(pass_context=True)
    @commands.has_role(config.ROOTROLE)
    @db.flock
    async def clearlog(self, ctx):
        """ Delete log of a specific user
        """
        args = parse_arguments(ctx.message.content)

        member = await check_for_id(ctx, args)

        new_log = []

        for log_entry in db["logs"]["logs"]:

            if log_entry["userid"] != int(args[0]):

                new_log.append(log_entry)

        db["logs"] = {"logs": new_log}

        await ctx.message.channel.send(f"Cleared modlog of {member.mention}.")


def setup(bot):
    """ On bot execute
    """
    bot.add_cog(Moderation(bot))
