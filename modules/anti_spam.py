from datetime import datetime, timedelta
from difflib import SequenceMatcher
from itertools import combinations

import discord
from config.config import config
from discord import Embed, errors
from discord.ext import commands
from modules import db


class AntiSpam(commands.Cog):
    """ Cog for AntiSpam and AntiDupe
    """
    def __init__(self, bot):

        # (STATIC) Variables
        self.bot = bot

        # (DYMANIC) Variables
        self._last_messages = []

    @commands.Cog.listener()
    async def on_message(self, message):
        """ On message sent
        """
        # Check for bot
        if isinstance(message.channel, discord.channel.DMChannel) or \
           message.author.bot:

            return

        self._last_messages.append(

            {

                "User_ID": message.author.id,
                "Message_ID": message.id,
                "Channel_ID": message.channel.id,
                "Created_At": message.created_at,
                "Message_Content": message.clean_content,

            }

        )

        # CHECK DATA
        if config.STAFFROLE not in [role.id for role in message.author.roles] and \
           len(self._last_messages) >= 5:

            await self._check_spam()
            await self._check_dupe()

        # Remove old items to keep data fresh and juicy
        if len(self._last_messages) >= 6:

            self._last_messages.pop(0)

    def _flush_data(self):
        """ Reset data list
        """
        self._last_messages = []

    @db.flock
    async def _mute_spam(self, author_id):
        """ Seperated function from self._check_spam to reduce flock queue time
        """
        # Mute user
        channel_id = [message["Channel_ID"] for message in self._last_messages if message["User_ID"] == author_id][-1]

        # Flush data
        self._flush_data()

        guild = self.bot.get_guild(config.GUILD)
        log_channel = self.bot.get_channel(config.LOGCHANNEL)
        mute_channel = self.bot.get_channel(config.MUTE_CHANNEL)
        muted_role = guild.get_role(config.MUTEDROLE)
        author = await guild.fetch_member(author_id)
        channel = self.bot.get_channel(channel_id)

        await author.add_roles(muted_role)
        await channel.send(f"The member <@{author.id}> has been spam-muted.")
        await mute_channel.send(f"Sorry <@{author.id}>, you have been muted due to possible spamming.\nPlease wait for an <@&690212787087081554>, to discuss the issue, and get unmuted.\nWe are so sorry in case this is a false detection.")

        punishments = db["punishments"]["punishments"]

        # Check if muted
        muted = False

        for punishment in punishments:

            if punishment["userid"] == author.id and \
               punishment["type"] == "mute":

                muted = True

        if muted:

            await channel.send(f"The member {author.mention} is already muted.")

            return

        # Write punishment data
        endtime = datetime.utcnow() + timedelta(minutes=999999999)

        punishments.append(

            {

                "year": endtime.year,
                "month": endtime.month,
                "day": endtime.day,
                "hour": endtime.hour,
                "minute": endtime.minute,
                "userid": author.id,
                "guild": guild.id,
                "type": "mute",

            }

        )

        db["punishments"] = {"punishments": punishments}

        # Send log
        date = datetime.now().strftime("%d.%m.%Y")

        embed = Embed(

            description=f"{author.mention} has been spam-muted.",
            color=config.COLOR,

        )

        embed.set_author(name=f"{author.name}#{author.discriminator}", icon_url=author.avatar_url)

        embed.set_footer(text=f"ID: {author.id} • {date}")

        await log_channel.send(embed=embed)

    async def _check_spam(self):
        """ Detect possible spam

        Could be improved
         - TODO: Spamming innocent people? (https://discord.com/channels/690212435306741901/883363741654188133/883437674399154186)

        """
        test_result = {message["User_ID"]: 0 for message in self._last_messages}

        for author_id in set([message["User_ID"] for message in self._last_messages]):

            # Message count
            count = [message["User_ID"] for message in self._last_messages].count(author_id)

            if count >= 5:

                test_result[author_id] += 1

            # Check similarity
            author_messages = [message["Message_Content"] for message in self._last_messages if message["User_ID"] == author_id]

            for message in author_messages:

                count = author_messages.count(message)

                if count >= 5:

                    test_result[author_id] += 1

                    break

            # Check multi channel
            author_channels = [message["Channel_ID"] for message in self._last_messages if message["User_ID"] == author_id]

            for channel_id in author_channels:

                count = author_channels.count(channel_id)

                if (len(author_channels) - count) >= 2:

                    test_result[author_id] += 1

                    break

            # Check message length

            # author_channels took from 'Check multi channel'

            for message in author_messages:
                if len(message) >= 400:

                    test_result[author_id] += 1

                    break

            # Check time delay
            author_messages = [message for message in self._last_messages if message["User_ID"] == author_id]

            first_author_message_time = author_messages[0]["Created_At"]
            last_author_message_time = author_messages[-1]["Created_At"]

            if (last_author_message_time - first_author_message_time).total_seconds() <= 5:

                test_result[author_id] += 1

        # Check result
        for author_id, score in test_result.items():

            if score / 5 >= 0.6:  # Average of tests (SCORE PERCENTAGE)

                await self._mute_spam(author_id)

    async def _check_dupe(self):
        """ Detect possible dupes
        """
        test_result = {message["User_ID"]: 0 for message in self._last_messages}

        for author_id in set([message["User_ID"] for message in self._last_messages]):

            author_messages = [message for message in self._last_messages if message["User_ID"] == author_id]

            # Pre-checking to reduce cpu load
            if len(author_messages) <= 1 or \
               len(set([message["Channel_ID"] for message in author_messages])) <= 1:

                continue

            # Check message similarity
            similar = []
            for combination in combinations(author_messages, 2):

                if SequenceMatcher(

                    None,
                    combination[0]["Message_Content"],
                    combination[1]["Message_Content"],

                ).ratio() >= 0.75:  # Guessed value

                    similar.append(combination)

            # Check channel IDs
            for match1, match2 in similar:

                match1_channel = await self.bot.fetch_channel(match1["Channel_ID"])
                match2_channel = await self.bot.fetch_channel(match2["Channel_ID"])

                try:  # TODO: Improvement needed

                    match1_message = await match1_channel.fetch_message(match1["Message_ID"])
                    match2_message = await match2_channel.fetch_message(match2["Message_ID"])

                except (errors.Forbidden, errors.NotFound):

                    match1_message = None
                    match2_message = None

                match1_verify = match1_message is not None
                match2_verify = match2_message is not None

                if match1["Channel_ID"] != match2["Channel_ID"] and \
                   match1_verify and match2_verify:

                    test_result[author_id] = 1

        # Check result
        for author_id, score in test_result.items():

            if score:

                self._flush_data()

                # Warn user
                last_message = similar[::-1][-1][1]
                channel = self.bot.get_channel(last_message["Channel_ID"])

                await channel.send(f"Hey <@{author_id}>, please do not send the same question/message into multiple channels, as this behaviour can be punished.")


def setup(bot):
    """ On bot execute
    """
    bot.add_cog(AntiSpam(bot))
