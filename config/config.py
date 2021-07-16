import config.tokens as tokens
from discord import Embed

TESTING = True


class ProductionEnv:
    """ Config for Production Environment
    """

    # General stuff
    TOKEN = tokens.TOKEN

    PREFIX = "!"

    COLOR = 0x57408b

    STATUS = "Ethical Computing Society!"

    # DB
    DATA_FILES_EMPTY = {

        "logs": {"logs": []},
        "punishments": {"punishments": []},
        "reminds": {"reminds": []},
        "public_help": {"current_channels": [], "freeze": False},

    }

    DATA_FILES = DATA_FILES_EMPTY.keys()

    # ID of the Guild.
    GUILD = 690212435306741901

    # Roles for the Verification-Mechanism and others
    STAFFROLE = 724251714613411851
    MODROLE = 690212787087081554
    DEVROLE = 690212865688469545
    MUTEDROLE = 690254996004012050

    # Ban
    BANDELETEMESSAGES = 2  # Delete messages of last 2 days

    # Custom roles {b64reaction: [rolename, roleid]}
    ROLES = {

        b"8J+UlA==": ["ping", 690239204667818102],
        b"4oyo77iP": ["coder", 690243098533822485],
        b"8J+Suw==": ["hacker", 690243125225980007],
        b"8J+Upw==": ["hardware", 726809084975906856],
        b"8J+Svw==": ["linux", 798178796192006174],

    }

    # Verification channel stuff
    UNVERIFIEDROLE = 732212270385332225
    VERIFIEDROLE = 690212961876312094

    VERIFICATIONENABLED = True

    VERIFICATIONCHANNELCAT = 690212435310936085
    VERIFICATIONCHANNELNAME = "verification"

    VERIFICATIONCHANNELMESSAGE = """
**How do I verify myself?**
Since there has been an increasing number of people with bad intentions joining, we've implemented this verification system.
Ping a moderator to make him know that you are ready to be verified.

**What are we going to chat about?**
Mostly about why you joined the server in the first place.

**How long does getting verified take?**
It mostly depends but not very long (couple of questions).

**Do I need to do something before getting verified?**
Yes, please make sure to read the rules and accept them.

**No mods online. What do I do now?**
Please wait until a moderator is available.
If a mod is online but doesn't see your message in #verification, you can ping them to get their attention.
"""

    REMINDERMSG = Embed(

        title="Ethical Computing Society",
        description="We've seen that you didn't verify yet! Please verify yourself in #verification!",
        color=COLOR,

    )

    REMINDKICKMSG = Embed(

        title="Ethical Computing Society",
        description="We're sorry, but you didn't verify in time and we had to kick you. You can always rejoin if you want to come back!\nhttps://discord.gg/CkMmZsR",
        color=COLOR,

    )

    WELCOMEMSG = Embed(

        title="Ethical Computing Society",
        description="Welcome to the Ethical Computing Society! To be able to chat, you will need to verify yourself in #verification!",
        color=COLOR,

    )

    DENIEDMSG = Embed(

        title="Ethical Computing Society",
        description="We're sorry, but we suspect you'd break one of our server's rules, so we didn't verify you. You can appeal using the following email taguar258@hash.fyi",
        color=COLOR,

    )

    # No verification channel stuff
    NOVERIFICATION_WELCOMEMSG = Embed(

        title="Ethical Computing Society",
        description="Welcome to the Ethical Computing Society!\nMake sure to read the rules.",
        color=COLOR,

    )

    NOVERIFIEDROLE = 864887304149139516

    NOVERIFICATION_CHANNELNAME = "missing-channels"

    # Log channels
    WELCOMEMSG_CHANNEL = 724238864855597056
    JOINLEAVE_CHANNEL = 726513291286806549
    MUTECHANNEL = 724244723023478806

    # Other important channels
    LOGCHANNEL = 746076232634073118
    MEMBERCOUNTCHANNEL = 755757420021809322
    ROLESCHANNEL = 690219084469895225

    # The message for the reaction roles
    ROLESMSG = 724236686971764767

    # Discord Embeds for Reminders and various other warnings.
    UNMUTEMSG = Embed(

        title="Ethical Computing Society",
        description="You have been unmuted.",
        color=COLOR,

    )

    MUTEMSG = Embed(

        title="Ethical Computing Society",
        description="We're sorry, but you have been muted for violating one of our rules. You can appeal this in the #muteappeal channel!",
        color=COLOR,

    )

    BANMSG = Embed(

        title="Ethical Computing Society",
        description="We're sorry, but you have been banned for violating our rules. You can appeal using the following email taguar258@hash.fyi",
        color=COLOR,

    )

    UNBANMSG = Embed(

        title="Ethical Computing Society",
        description="You have been unbanned.\nhttps://discord.gg/CkMmZsR",
        color=COLOR,

    )

    WARNMSG = Embed(

        title="Ethical Computing Society",
        description="We're sorry, but you have been warned for violating one of our rules.",
        color=COLOR,

    )

    KICKMSG = Embed(

        title="Ethical Computing Society",
        description="We're sorry, but you have been kicked for violating one of our rules.",
        color=COLOR,

    )

    # Variables regarding the public help system
    PHELPCATEGORY = 798177254873235487

    REACT_ERROR = "\u2757"    # https://www.fileformat.info/info/unicode/
    REACT_SUCCESS = "\u2705"  #

    PHELP_MAX_CHANNELS = 10
    PHELP_MAX_TITLE = 20

    PHELP_REMEMBER_AFTER_DAY = 2
    PHELP_DELETE_AFTER_DAY = 4

    PHELP_MUTE_ROLE = 798178561797521459

    # Public and private help messages
    HELP_MESSAGE_MODS = """
/channel new YOUR_TITLE | To create a new channel.
/channel close (-y) | To close your current channel.
/channel list | To list all channels.
/channel info ID | To see more info about a channel.
/channel fclose ID (-y) | To force close a channel.
"""

    HELP_MESSAGE_USER = """
/channel new YOUR_TITLE | To create a new channel.
/channel close (-y) | To close your current channel.
"""

    # Enable/Disable ISS feature
    ISS_INFO_ENABLED = False

    # Command filter
    GREY_COMMANDS = {  # https://regex101.com/

        r"\b(rm|shred|rmdir)\b": ["as it deletes files and/or folders", "Make sure to create a backup before runing this command and look out for the star '*' char, as it patter matches everything."],
        r"\b(chown|chmod)\s*-R\.*\b": ["as it removes all permission to a file or directory", "We would not suggest running this command."],
        r":(){ :\|: & };:": ["as it is a for bomb and will freeze your computer", "We do not recommend running the command."],
        r"(\bdd\b|\bof=/\b)": ["as it could overwrite important data", "We do not recommend running this, if you do not understand what the command does."],
        r"\bgparted\b": ["as it could format important data", "We do not recommend using this, if you do not want to mess with your data."],
        r"\bparted\b": ["as it could format important data", "We do not recommend using this, if you do not want to mess with your data."],
        r"\bmkfs.*": ["as it could format important data", "We do not recommend using this, if you do not want to mess with your data."],
        r"(\s*|)(>|>>)(\s*|)/dev/.*": ["as it could overwrite important data", "We do not recommend runing this, if you do not understand what the command does."],
        r"\bmv (.|\b) /dev/null\b": ["as it moves data into a black hole", "We do not recommend runing this command at all."],
        r"(\b(wget|curl)\s.*(sh|zsh|bash|sudo|\_)\b)|(\b(sh|zsh|bash|sudo|\_)\s.*(wget|curl)\b)": ["as it downloads and executes unknown content", "Do not run this command if it includes any suspicious/untrustful URL."],
        r"\b(sudo|\_)\s*.*(\s*|)(>|>>)(\s*|)(.*\/.*|.*\..*|.*\s*)\b": ["as it can overwrite important data", "Do not run this if you don't want files to be overwritten."],
        r"\\xeb\\x3e\\x5b\\x31\\xc0\\x50\\x54\\x5a": ["as this is part of a very well known malicious code to erase your data", "Do not run this."],  # EXPERIMENTAL
        r"\bcat\s*/dev.*\b": ["as it creates a kernel panic", "We would not suggest running this command."],
        r"\b\^.*\^.*\b": ["as this might be a substitution", "You most likely won't need a substitution, so we suggest you to ignore this command."],
        r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}.*(bash|cmd|sh|zsh))|((bash|cmd|sh|zsh).*\d{3}\.\d{3}\.\d{3}\.\d{3})": ["as this could be a reverse shell", "When running this command, someone could potentially connect with your computer."],
        r"\b-y\b": ["as it automatically executes tasks without double checking for your user input", "It's adviced to run the command without '-y' argument."],
        #r"\A[^\w\W]": ["", ""],  # Needed when less than two cases

    }

    GREY_COMMANDS_COMBINED = "(" + ")|(".join(GREY_COMMANDS.keys()) + ")"

    # Ignored Commands
    IGNORED_COMMANDS = ["d"]

    # Vote Mute
    VOTE_REACTION_MUTE = b"8J+Uhw=="
    VOTE_REACTION_NO_MUTE = b"8J+UiA=="

    MUTE_CHANNEL = 724244723023478806

    TRIP_LEVEL = 0.012


class TestingEnv:
    """ Config for Production Environment
    """

    TOKEN = tokens.TOKENTESTING

    PREFIX = "!"

    COLOR = 0x57408b

    STATUS = "ECS - TESTING!"

    GUILD = 776898177302921286

    DATA_FILES_EMPTY = ProductionEnv.DATA_FILES_EMPTY
    DATA_FILES = ProductionEnv.DATA_FILES

    UNVERIFIEDROLE = 776900475161280514
    VERIFIEDROLE = 776900474552844288
    STAFFROLE = 776900462753480714
    MODROLE = 776900459180458015
    DEVROLE = 776900461630324757
    MUTEDROLE = 776900473391022101

    ROLES = {b"8J+UlA==": ["ping", 776900472358305833],
             b"4oyo77iP": ["coder", 776900472086331452],
             b"8J+Suw==": ["hacker", 776900471004594188],
             b"8J+Upw==": ["hardware", 776900470601154580],
             b"8J+Svw==": ["linux", 796079401544450109]}

    VERIFICATIONCHANNELCAT = 776900479946194955
    VERIFICATIONCHANNELNAME = "verification"
    LOGCHANNEL = 776900515640115250
    MEMBERCOUNTCHANNEL = 776900480521338951

    ROLESCHANNEL = 776900486145900566
    ROLESMSG = 776901414940049438

    WELCOMEMSG_CHANNEL = 776900487886012466
    JOINLEAVE_CHANNEL = 776900514931146792
    MUTECHANNEL = 776900510796087326

    VERIFICATIONCHANNELMESSAGE = ProductionEnv.VERIFICATIONCHANNELMESSAGE

    VERIFICATIONENABLED = True
    NOVERIFIEDROLE = 861011856025059359
    NOVERIFICATION_WELCOMEMSG = ProductionEnv.NOVERIFICATION_WELCOMEMSG
    NOVERIFICATION_CHANNELNAME = ProductionEnv.NOVERIFICATION_CHANNELNAME

    BANDELETEMESSAGES = ProductionEnv.BANDELETEMESSAGES

    WELCOMEMSG = ProductionEnv.WELCOMEMSG
    REMINDERMSG = ProductionEnv.REMINDERMSG
    KICKMSG = ProductionEnv.KICKMSG
    DENIEDMSG = ProductionEnv.DENIEDMSG
    UNMUTEMSG = ProductionEnv.UNMUTEMSG
    MUTEMSG = ProductionEnv.MUTEMSG
    BANMSG = ProductionEnv.BANMSG
    UNBANMSG = ProductionEnv.UNBANMSG
    WARNMSG = ProductionEnv.WARNMSG
    REMINDKICKMSG = ProductionEnv.REMINDKICKMSG

    PHELPCATEGORY = 795634619927363605

    REACT_ERROR = "\u2757"    # https://www.fileformat.info/info/unicode/
    REACT_SUCCESS = "\u2705"  #

    PHELP_MAX_CHANNELS = 10
    PHELP_MAX_TITLE = 20

    PHELP_REMEMBER_AFTER_DAY = 2
    PHELP_DELETE_AFTER_DAY = 4

    PHELP_MUTE_ROLE = 796390021526585364

    HELP_MESSAGE_MODS = ProductionEnv.HELP_MESSAGE_MODS

    HELP_MESSAGE_USER = ProductionEnv.HELP_MESSAGE_USER

    ISS_INFO_ENABLED = False

    GREY_COMMANDS = ProductionEnv.GREY_COMMANDS
    GREY_COMMANDS_COMBINED = ProductionEnv.GREY_COMMANDS_COMBINED

    IGNORED_COMMANDS = ProductionEnv.IGNORED_COMMANDS

    VOTE_REACTION_MUTE = ProductionEnv.VOTE_REACTION_MUTE
    VOTE_REACTION_NO_MUTE = ProductionEnv.VOTE_REACTION_NO_MUTE

    MUTE_CHANNEL = 776900510796087326

    TRIP_LEVEL = ProductionEnv.TRIP_LEVEL


if TESTING:

    config = TestingEnv

else:

    config = ProductionEnv
