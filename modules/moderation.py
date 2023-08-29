from asyncio import sleep as async_sleep
from copy import deepcopy
from datetime import timedelta

import discord
from config.config import config
from discord.ext import commands
from discord_slash import SlashContext, cog_ext, manage_commands
from discord_slash.utils.manage_commands import create_permission
from discord_slash.model import SlashCommandPermissionType
from modules import get_full_name, log, send_embed_dm


class Moderation(commands.Cog):
    """ Cog for moderation tasks
    """
    def __init__(self, bot):
        self.bot = bot

    def verify_role(required_role):
        """ Convenience wrapper to compensate for cog_slash permissions argument
            that does not work
        """
        def decorator(func):
            async def wrapper(self, ctx: SlashContext, *args, **kwargs):
                if required_role not in [role.id for role in ctx.author.roles]:
                    await ctx.send("You may not run this command!", delete_after=10)
                    raise IgnoreException

                return await func(self, ctx, *args, **kwargs)
            return wrapper
        return decorator

    async def fetch_member(self, ctx: SlashContext, user_id: str):
        if not user_id.isdigit():
            await ctx.send("The id is not a valid integer", delete_after=5)
            raise IgnoreException

        try:
            return await ctx.guild.fetch_member(user_id)
        except Exception:
            await ctx.send("Could not fetch the user", delete_after=5)
            raise IgnoreException

    @cog_ext.cog_slash(
        name="whois",
        options=[manage_commands.create_option(
            name="user_id",
            description="The id of the user",
            option_type=str,
            required=True,
        )],
    )
    @verify_role(config.STAFFROLE)
    async def whois(self, ctx: SlashContext, user_id: str):
        """ Whois member lookup
        """
        if not user_id.isdigit():
            await ctx.send("The id is not a valid integer", delete_after=5)
            return

        # check if not member and try to fetch user object
        member = None

        try:
            member = await self.bot.fetch_user(int(user_id))
            member = await ctx.guild.fetch_member(user_id)
        except Exception:
            pass

        if member is None:
            await ctx.send("Could not fetch the user", delete_after=5)
            return

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

    @cog_ext.cog_slash(
        name="purge",
        options=[manage_commands.create_option(
            name="user_id",
            description="The id of the user",
            option_type=str,
            required=True,
        )],
    )
    @verify_role(config.ROOTROLE)
    async def purge(self, ctx: SlashContext, user_id: str):
        """ Delete all messages of a specified user
        """
        if not user_id.isdigit():
            await ctx.send("The id is not a valid integer", delete_after=5)
            return

        try:
            member = await self.bot.fetch_user(user_id)
        except Exception:
            await ctx.send("Could not fetch the user", delete_after=5)
            return

        # Main logic
        purging_info = await ctx.send("Purging...", delete_after=60)

        for channel in ctx.message.guild.channels:

            if channel.type == discord.ChannelType.text:

                await channel.purge(check=(lambda m: m.author.id == int(member.id)))

        await log(ctx.guild, ctx.author, "Purge", f"purged all messages from {member.mention}")

        await purging_info.edit(content=f"Successfully purged {member.mention}, rerun if not all messages were affected.")

    @cog_ext.cog_slash(
        name="warn",
        options=[
            manage_commands.create_option(
                name="user_id",
                description="The id of the member",
                option_type=str,
                required=True,
            ),
            manage_commands.create_option(
                name="reason",
                description="The reason why you are warning this member",
                option_type=str,
                required=True,
            ),
        ],
    )
    @verify_role(config.MODROLE)
    async def warn(self, ctx: SlashContext, user_id: str, reason: str):
        """ Warn a member
        """
        member = await self.fetch_member(ctx, user_id)

        embed = deepcopy(config.WARNMSG)
        embed.add_field(
            name="Reason",
            value=reason,
        )

        await send_embed_dm(member, embed)
        await log(ctx.guild, ctx.author, "Warn", f"warned {member.mention}. Reason: {reason}")
        await ctx.send(f"Successfully warned {member.mention}!")

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        await log(guild, self.bot.user, "Ban", f"banned {user.mention}")

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        await log(guild, self.bot.user, "UnBan", f"unbanned {user.mention}")

    # TODO: feature available after bumping discord.py
    # @commands.Cog.listener()
    # async def on_member_update(self, before, after):
    #     if before.timed_out_until is None and after.timed_out_until is not None:
    #         # await log(ctx.guild, ctx.author, "TimeOut", f"timeout applied to {member.mention}")
    #         pass
    #     elif before.timed_out_until is not None and after.timed_out_until is None:
    #         # await log(ctx.guild, ctx.author, "TimeOut", f"timeout removed from {member.mention}")
    #         pass

def setup(bot):
    """ On bot execute
    """
    bot.add_cog(Moderation(bot))
