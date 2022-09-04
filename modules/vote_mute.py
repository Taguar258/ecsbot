from base64 import b64encode
from datetime import datetime, timedelta

from config.config import config
from discord import Embed
from discord.ext import commands
from modules import db


class VoteMute(commands.Cog):
    """ Cog for mute on user vote-reaction threshold
    """
    def __init__(self, bot):

        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """ On reaction add
        """
        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        reaction = b64encode(str(payload.emoji).encode())

        if message.author.id == self.bot.user.id:

            return

        # Check if user and author are the same
        if reaction in [config.VOTE_REACTION_MUTE, config.VOTE_REACTION_NO_MUTE] and \
           message.author.id == payload.user_id:

            await message.remove_reaction(payload.emoji, message.author)

            return

        # Check for possible mute vote/result
        if reaction == config.VOTE_REACTION_MUTE:

            await self.check_vote_reaction(self.bot, channel, message)

    @db.flock
    async def _mute_voted_user(self, client, message, pro_count, contra_count):
        """ Seperate mute actions from self.check_vote_reaction to decrease queue time
        """
        # Init
        log_channel = self.bot.get_channel(config.LOGCHANNEL)

        await message.author.add_roles(message.guild.get_role(config.MUTEDROLE))

        await message.channel.send(f"The member <@{message.author.id}> has been vote-muted.")

        mute_channel = client.get_channel(config.MUTECHANNEL)

        await mute_channel.send(f"Sorry <@{message.author.id}>, you have been muted due to possible rule-breaking.\nPlease wait for an <@&690212787087081554>, to discuss the issue, and get unmuted.")
        await mute_channel.send(f"[{pro_count}/{contra_count}]\n||{message.content}||")

        await message.delete()

        # # Write punishment data
        # punishments = db["punishments"]["punishments"]

        # # Check if muted
        # muted = False

        # for punishment in punishments:

        #     if punishment["userid"] == message.author.id and \
        #        punishment["type"] == "mute":

        #         muted = True

        # if muted:

        #     await message.channel.send(f"The member {message.author.mention} is already muted.")

        #     return

        # # Write punishment data
        # endtime = datetime.utcnow() + timedelta(minutes=999999999)

        # punishments.append(

        #     {

        #         "year": endtime.year,
        #         "month": endtime.month,
        #         "day": endtime.day,
        #         "hour": endtime.hour,
        #         "minute": endtime.minute,
        #         "userid": message.author.id,
        #         "guild": message.guild.id,
        #         "type": "mute",

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
        #         "userid": message.author.id,
        #         "guild": message.guild.id,
        #         "duration": 999999999,
        #         "reason": f"Vote Mute ({message.content[:50]})",
        #         "type": "mute",

        #     }

        # )

        # db["logs"] = {"logs": logs}

        # Send log
        date = datetime.now().strftime("%d.%m.%Y")

        embed = Embed(

            description=f"{message.author.mention} has been vote muted.",
            color=config.COLOR,

        )

        embed.set_author(name=f"{message.author.name}#{message.author.discriminator}", icon_url=message.author.avatar_url)

        embed.set_footer(text=f"ID: {message.author.id} • {date}")

        await log_channel.send(embed=embed)

    async def check_vote_reaction(self, client, channel, message):
        """ Check for mute reactions

        If certain voting score -> Mute user

        """
        # Check if author is staff
        if config.STAFFROLE in [role.id for role in message.author.roles] or message.author.bot:
            return

        members_count = sum([1 if not member.bot else 0 async for member in message.guild.fetch_members()])
        needed_count = round(members_count * config.TRIP_LEVEL)

        if needed_count <= 3:
            needed_count = 3

        # Count Reactions
        pro_count = 0
        contra_count = 0
        pro_moderators_count = 0
        contra_moderators_count = 0

        for reaction in message.reactions:

            reaction_b64 = b64encode(str(reaction.emoji).encode())

            if reaction_b64 == config.VOTE_REACTION_MUTE:

                pro_count = reaction.count

                async for user in reaction.users():

                    if config.MODROLE in [role.id for role in user.roles]:

                        pro_moderators_count += 1

            elif reaction_b64 == config.VOTE_REACTION_NO_MUTE:

                contra_count = reaction.count

                async for user in reaction.users():

                    if config.MODROLE in [role.id for role in user.roles]:

                        contra_moderators_count += 1

        level = pro_count - contra_count

        if (level >= needed_count and \
            contra_moderators_count != 0) or \
           (pro_moderators_count >= 1):

            await self._mute_voted_user(client, message, pro_count, contra_count)


def setup(bot):
    """ On bot execute
    """
    bot.add_cog(VoteMute(bot))
