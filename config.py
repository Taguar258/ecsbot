import discord
TOKEN = "INSERT-TOKEN-HERE"
PREFIX = "!"

STATUS = "Ethical Computing Society!"

# ID of the Guild.
GUILD = 690212435306741901

# IDs of various channels.
RULESCHANNEL = 690216616163672136
RULESMSG = 690217807748530276
ROLESCHANNEL = 690219084469895225
ROLESMSG = 724236686971764767

# base64 encoded emoji as reaction for accepting rules.
RULESREACTION = b"4pyF"

# Roles for the Rules-Mechanism.
UNVERIFIEDROLE = 732212270385332225
VERIFIEDROLE = 690212961876312094

# Staff roles, for admin commands.
ADMINROLE = 724251714613411851

# Custom roles {b64reaction: [rolename, roleid]}
ROLES = {b"8J+UlA==": ["ping", 690239204667818102],
         b"4oyo77iP": ["coder", 690243098533822485],
         b"8J+Suw==": ["hacker", 690243125225980007],
         b"8J+Upw==": ["hardware", 726809084975906856]}

# Discord Embeds for Reminders
WELCOMEMSG = discord.Embed(title="Ethical Computing Society", 
                           description="Welcome to the Ethical Computing Society! To be able to chat and accept the rules, react with a checkmark in #rules! If you have problems verifying, contact us in #verification-help!", color=0x57008b)
REMINDERMSG = discord.Embed(title="Ethical Computing Society", 
                           description="We've seen that you didn't accept the rules yet! To accept them, react with a checkmark in #rules! If you have problems verifying, contact us in #verification-help!", color=0x57008b)
KICKMSG = discord.Embed(title="Ethical Computing Society", 
                           description="We're sorry, but you didn't accept the rules and we had to kick you. You can always rejoin if you want to come back!", color=0x57008b)
