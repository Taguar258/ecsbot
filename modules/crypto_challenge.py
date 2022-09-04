from re import search

import discord
from config.config import config
from discord.ext import commands
from modules import db, parse_arguments


class CryptoChallenge(commands.Cog):
    """ Cog for crypto Challenge role system
    """
    def __init__(self, bot):

        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        """ Automatically delete solution messages or check solution
        """
        if isinstance(message.channel, discord.channel.DMChannel) and \
           message.author != self.bot.user:

            if search(r"^\w{128}$", message.content):

                await self._check_solution(message)

        else:

            solution = db["crypto_challenge"]["solution-hash"]

            if solution != "" and \
               solution in "".join(message.content.split()):

                await message.channel.send(f"Crypto solution (posted by {message.author.mention}) has been eradicated!")

                await message.delete()

    async def _check_solution(self, message):
        """ Check solution
        """
        guild = self.bot.get_guild(config.GUILD)
        solver_role = guild.get_role(config.CRYPTOROLE)
        crypto_channel = self.bot.get_channel(config.CRYPTOANNOUNCMENTCHANNEL)
        member = await guild.fetch_member(message.author.id)

        solution = db["crypto_challenge"]["solution-hash"]

        if solution == "":

            pass  # Ignore when no solution hash set

        elif message.content == solution:

            congrats_msg = await message.channel.send("Congratulations, you have successfully solved the crypto challenge.")
            await congrats_msg.add_reaction(config.REACT_CONGRATS)

            if not len([1 for member in guild.members if config.CRYPTOROLE in [role.id for role in member.roles]]):  # FIRST BLOOD

                first_blood_msg = await message.channel.send("**YOU WERE THE FIRST ONE TO SOLVE THIS CHALLENGE TOO!**")
                await first_blood_msg.add_reaction(config.REACT_FIRST_BLOOD)

                await crypto_channel.send(f"First Blood: {message.author.mention}")

            await member.add_roles(solver_role, reason="Solved crypto challenge")

        else:

            await message.channel.send("Sorry, this SHA (512) Hash is incorrect.")

    async def _remove_roles(self, guild):
        """ Remove all solved_crypto roles
        """
        solver_role = guild.get_role(config.CRYPTOROLE)

        for member in guild.members:

            if config.CRYPTOROLE in [role.id for role in member.roles]:

                await member.remove_roles(solver_role, reason="New crypto challenge")

    @commands.command(pass_context=True)
    @commands.has_role(config.ROOTROLE)
    @db.flock
    async def newcrypto(self, ctx):
        """ Set the hash challenge solution and reset roles
        """
        # Init
        await ctx.message.delete()

        args = parse_arguments(ctx.message.content)

        if not args.check(0, re=r"^\w{128}$"):

            await ctx.message.channel.send("Please supply a SHA3 (512) Hash.")

            return

        # Remove role and set solution
        info_msg = await ctx.message.channel.send("Removing user roles...")

        await self._remove_roles(ctx.message.guild)

        db["crypto_challenge"] = {"solution-hash": args[0]}

        await info_msg.edit(content="Successfully applied new challenge.")
        await info_msg.add_reaction(config.REACT_SUCCESS)

    @commands.command(pass_context=True)
    @commands.has_role(config.ROOTROLE)
    @db.flock
    async def stopcrypto(self, ctx):
        """ Stop crypto and remove roles
        """
        info_msg = await ctx.message.channel.send("Removing user roles...")

        await self._remove_roles(ctx.message.guild)

        db["crypto_challenge"] = {"solution-hash": ""}

        await info_msg.edit(content="Successfully closed challenge.")
        await info_msg.add_reaction(config.REACT_SUCCESS)


def setup(bot):
    """ On bot execute
    """
    bot.add_cog(CryptoChallenge(bot))
