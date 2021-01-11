import modules.moderation as moderation
import modules.other as other
import modules.public_help as phelp
import modules.verification as verification
from config.config import config


async def exec_command(author, channel, command, args, guild, ping, message, client):

    if command in ["channel", "help"]:
        if len(args) == 0:
            await message.delete()
            if guild.get_role(config.STAFFROLE) not in author.roles:
                await phelp.help_help(channel, 0)
            else:
                await phelp.help_help(channel, 1)
        elif args[0] in ["new", "add"]:
            await phelp.new_help(author, channel, guild, args, message, client)
        elif args[0] in ["close", "remove"]:
            await phelp.close_help(author, channel, guild, args, message, client)
        elif guild.get_role(config.STAFFROLE) not in author.roles:
            await message.delete()
            await phelp.help_help(channel, 0)
            return

        elif args[0] == "list":
            await phelp.list_help(author, channel, message, client)
        elif args[0] == "fclose":
            await phelp.force_close_help(author, channel, guild, args, message, client)
        elif args[0] == "info":
            await phelp.info_help(author, channel, guild, args, message, client)
        elif args[0] == "flush":
            await phelp.flush_help(channel, message)
        elif args[0] == "freeze":
            await phelp.freeze_help(channel, args, message)
        elif args[0] == "db":
            await phelp.db_help(channel, message)
        else:
            await message.delete()
            await phelp.help_help(channel, 1)

        return

    if guild.get_role(config.STAFFROLE) not in author.roles:
        return

    if command == "purge":
        await moderation.purge(author, channel, guild, args)

    elif command in ["approve", "approved", "verify"]:
        await verification.verify(author, channel, guild, args)

    elif command == "vpurge":
        await verification.vpurge(author, channel, guild, args)

    elif command in ["denied", "deny", "reject"]:
        await verification.reject(author, channel, guild, args)

    elif command == "whois":
        await other.whois(channel, guild, args)

    elif command in ["ban", "detain", "obliterate"]:
        await moderation.ban(author, channel, guild, args)

    elif command in ["pardon", "unban"]:
        await moderation.unban(author, channel, guild, args)

    elif command in ["mute", "slap"]:
        await moderation.mute(author, channel, guild, args)

    elif command == "unmute":
        await moderation.unmute(author, channel, guild, args)

    elif command in ["warn", "pewpew"]:
        await moderation.warn(author, channel, guild, args)

    elif command == "kick":
        await moderation.kick(author, channel, guild, args)

    elif command in ["infractions", "modlogs", "punishments", "detentions"]:
        await moderation.infractions(author, channel, guild, args)

    elif command in ["ping", "pong"]:
        await other.ping(channel, ping)

    else:
        await channel.send("Command not found.")
