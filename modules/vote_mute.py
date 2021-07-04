from base64 import b64encode

from config.config import config
from discord.ext import commands


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

    async def check_vote_reaction(self, client, channel, message):
        """ Check for mute reactions

        If certain voting score -> Mute user

        """
        # Check if author is staff
        if config.STAFFROLE in [role.id for role in message.author.roles]:
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

            await message.author.add_roles(message.guild.get_role(config.MUTEDROLE))

            await message.channel.send(f"The member <@{message.author.id}> has been vote-muted.")

            mute_channel = client.get_channel(config.MUTE_CHANNEL)

            await mute_channel.send(f"Sorry <@{message.author.id}>, you have been muted due to possible rule-breaking.\nPlease wait for an <@&690212787087081554>, to discuss the issue, and get unmuted.")
            await mute_channel.send(f"[{pro_count}/{contra_count}]\n||{message.content}||")

            await message.delete()


def setup(bot):
    """ On bot execute
    """
    bot.add_cog(VoteMute(bot))
