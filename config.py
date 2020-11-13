import discord
import tokens

TESTING = True

class ProductionEnv:
    TOKEN = tokens.TOKEN
    PREFIX = "/"

    STATUS = "Ethical Computing Society!"

    # ID of the Guild.
    GUILD = 690212435306741901

    # Roles for the Verification-Mechanism.
    UNVERIFIEDROLE = 732212270385332225
    VERIFIEDROLE = 690212961876312094
    STAFFROLE = 724251714613411851
    MUTEDROLE = 690254996004012050

    # Custom roles {b64reaction: [rolename, roleid]}
    ROLES = {b"8J+UlA==": ["ping", 690239204667818102],
            b"4oyo77iP": ["coder", 690243098533822485],
            b"8J+Suw==": ["hacker", 690243125225980007],
            b"8J+Upw==": ["hardware", 726809084975906856]}

    # Category of the verification channel
    VERIFICATIONCHANNELCAT = 690212435310936085
    VERIFICATIONCHANNELNAME = "verification"
    LOGCHANNEL = 746076232634073118
    MEMBERCOUNTCHANNEL = 755757420021809322
    ROLESCHANNEL = 690219084469895225

    ROLESMSG = 724236686971764767
    
    VERIFICATIONCHANNELMESSAGE = """
    **How do I verify myself?**
    Since there has been an increasing number of people with bad intentions joining, we've implemented this verification system.
    You can simply type something here to make a moderator know you are ready to be verified. 
    Once you've messaged something in #verification, a moderator should arrive and chat with you.

    **What are we going to chat about?**
    Nothing really personal. Mostly about your intentions and how you found this discord server. 
    You shouldn't be afraid of anything in this server.

    **How long does getting verified take?**
    It will be around 2 to 4 messages. So, not long.

    **Do I need to do something before trying to get verified?**
    Yes, please be sure to read the rules and accept them first and be sure you have no malicious intents 
    (this includes but is not limited to things that are illegal, againts ToS and could cause mass or singular damage to anything.)

    **No mods online. What do I do now?**
    Mods should be on 24/7 as they are from different countries all over the world with different timezones, 
    but in a case of no mods being online, please wait and do not spam in #verification. 
    If a mod is online but doesn't see your message in #verification, you can ping them just once to get their attention so they can verify you.
    """

    # Discord Embeds for Reminders and various other warnings.
    WELCOMEMSG = discord.Embed(title="Ethical Computing Society", 
                            description="Welcome to the Ethical Computing Society! To be able to chat, verify yourself in #verification!", color=0x57008b)
    REMINDERMSG = discord.Embed(title="Ethical Computing Society", 
                            description="We've seen that you didn't verify yet! To verify yourself in #verification!", color=0x57008b)
    KICKMSG = discord.Embed(title="Ethical Computing Society", 
                            description="We're sorry, but you didn't verify yourself and we had to kick you. You can always rejoin if you want to come back!", color=0x57008b)
    DENIEDMSG = discord.Embed(title="Ethical Computing Society",
                            description="We're sorry, but we suspect you'd break one of our Rules on the server, so we couldn't verify you. You can appeal this at banappeal@sw1tchbl4d3.com", color=0x57008b)
    UNMUTEMSG = discord.Embed(title="Ethical Computing Society",
                            description="We're happy to notify you that you have been unmuted! Get chatting!", color=0x57008b)
    MUTEMSG = discord.Embed(title="Ethical Computing Society",
                            description="We're sorry, but you have been muted for violating one of our rules. You can appeal this in the #muteappeal channel!", color=0x57008b)
    BANMSG = discord.Embed(title="Ethical Computing Society",
                            description="We're sorry, but you have been banned for violating one of our rules. You can appeal this at banappeal@sw1tchbl4d3.com", color=0x57008b)
    WARNMSG = discord.Embed(title="Ethical Computing Society",
                            description="We're sorry, but you have been warned for violating one of our rules.", color=0x57008b)

class TestingEnv:
    TOKEN = tokens.TOKENTESTING
    PREFIX = "/"

    STATUS = "ECS - TESTING!"

    # ID of the Guild.
    GUILD = 776898177302921286
    
    # Roles for the Verification-Mechanism.
    UNVERIFIEDROLE = 776900475161280514
    VERIFIEDROLE = 776900474552844288
    STAFFROLE = 776900462753480714
    MUTEDROLE = 776900473391022101

    # Custom roles {b64reaction: [rolename, roleid]}
    ROLES = {b"8J+UlA==": ["ping", 776900472358305833],
            b"4oyo77iP": ["coder", 776900472086331452],
            b"8J+Suw==": ["hacker", 776900471004594188],
            b"8J+Upw==": ["hardware", 776900470601154580]}

    # Category of the verification channel
    VERIFICATIONCHANNELCAT = 776900479946194955
    VERIFICATIONCHANNELNAME = "verification"
    LOGCHANNEL = 776900515640115250
    MEMBERCOUNTCHANNEL = 776900480521338951

    # Channel and Message for the reaction roles.
    ROLESCHANNEL = 776900486145900566
    ROLESMSG = 776901414940049438
    
    VERIFICATIONCHANNELMESSAGE = ProductionEnv.VERIFICATIONCHANNELMESSAGE

    WELCOMEMSG = ProductionEnv.WELCOMEMSG
    REMINDERMSG = ProductionEnv.REMINDERMSG
    KICKMSG = ProductionEnv.KICKMSG
    DENIEDMSG = ProductionEnv.DENIEDMSG
    UNMUTEMSG = ProductionEnv.UNMUTEMSG
    MUTEMSG = ProductionEnv.MUTEMSG
    BANMSG = ProductionEnv.BANMSG
    WARNMSG = ProductionEnv.WARNMSG

if TESTING:
    config = TestingEnv
else:
    config = ProductionEnv
