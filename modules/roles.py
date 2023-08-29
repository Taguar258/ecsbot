from base64 import b64encode

from config.config import config
from discord.ext import commands


class Roles(commands.Cog):
    """ Cog for roles on reaction
    """
    def __init__(self, bot):

        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """ Add role on reaction add
        """
        guild = self.bot.get_guild(payload.guild_id)
        reaction = b64encode(str(payload.emoji).encode())
        member = guild.get_member(payload.user_id)

        if config.ROLESMSG == payload.message_id and \
           config.ROLESCHANNEL == payload.channel_id:

            if reaction in config.ROLES:

                await member.add_roles(

                    guild.get_role(

                        config.ROLES[reaction][1]

                    ),

                    reason=f"Added {config.ROLES[reaction][0]}"

                )

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        """ Remove role on reaction remove
        """
        guild = self.bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        reaction = b64encode(str(payload.emoji).encode())

        if config.ROLESMSG == payload.message_id and \
           config.ROLESCHANNEL == payload.channel_id:

            if reaction in config.ROLES.keys():

                await member.remove_roles(

                    guild.get_role(

                        config.ROLES[reaction][1]

                    ),

                    reason="Removed " + config.ROLES[reaction][0]

                )


def setup(bot):
    """ On bot execute
    """
    bot.add_cog(Roles(bot))
