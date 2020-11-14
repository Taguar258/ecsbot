from config.config import config
import modules.moderation as moderation
import modules.verification as verification
import modules.other as other

async def exec_command(author, channel, command, args, guild, ping):
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