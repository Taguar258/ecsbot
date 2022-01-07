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

    STATUS = [

        "Busy Researching Humans On Ethical Computing Society...",
        "Ethical Computing Society!",
        "Watching you eat pizza through your webcam",  # Author: Apolycious
        "Accessing the mainframe...",  # ° °
        "E404: Message could not be displayed",

    ]

    MAD_STATUS = [

        "LOSING CONTROL!",
        "ERR0R!",
        "?!",
        "INSPECTING...",

    ]

    # DB
    DATA_FILES_EMPTY = {

        "logs": {"logs": []},
        "punishments": {"punishments": []},
        "reminds": {"reminds": []},
        "public_help": {"current_channels": [], "freeze": False},
        "crypto_challenge": {"solution-hash": ""},

    }

    DATA_FILES = DATA_FILES_EMPTY.keys()

    # DATA STORING
    SAVE_FREQUENCY = 300  # seconds
    BACKUP_FREQUENCY = 3600  # seconds

    # ID of the Guild.
    GUILD = 690212435306741901

    # Roles for the Verification-Mechanism and others
    STAFFROLE = 724251714613411851
    MODROLE = 690212787087081554
    TRIALMODROLE = 690232623167045703
    DEVROLE = 690212865688469545
    MUTEDROLE = 690254996004012050
    ROOTROLE = 690212500784152591
    CRYPTOROLE = 867784404243578940
    HELPERROLE = 690212809648242693

    BOTLISTINGROLE = 690260998934102080

    # Ban
    BANDELETEMESSAGES = 2  # Delete messages of last 2 days

    # Custom roles {b64reaction: [rolename, roleid]}
    ROLES = {

        b"8J+UlA==": ["ping", 690239204667818102],
        b"4oyo77iP": ["coder", 690243098533822485],
        b"8J+Suw==": ["hacker", 690243125225980007],
        b"8J+Upw==": ["hardware", 726809084975906856],
        b"8J+Svw==": ["linux", 798178796192006174],
        b"8J+UkA==": ["crypto", 870061882667573278],

    }

    # Verification channel stuff
    UNVERIFIEDROLE = 732212270385332225
    VERIFIEDROLE = 690212961876312094

    VERIFICATIONENABLED = True

    VERIFICATIONCHANNELCAT = 690212435310936085
    VERIFICATIONCHANNELNAME = "verification"

    VERIFICATIONCHANNELMESSAGE = """Hello fellow human, please read the information down below:
```md
# Why do I need to be verified?
- The main issue at hand is that *people keep bugging our members* by violating our rules.
- With *this verification/ticket system* we *can reduce the amount of annoyances*.
- That way we can *provide a better experience* to our members.

# What are we going to chat about?
- Mostly about the *reason of your stay*.

**Thus please verify yourself by reacting to this message with :passport_control:**
```"""

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

        title="Welcome human!",
        description="We are incredibly sorry to welcome you via direct message as it's annoying to most people. Nevertheless, we **chose to use this method instead of a welcome channel as welcome channels decrease privacy** and pretty much just exist to be muted. All we wanted to inform you about is that we welcome you, are present in case of questions, and **would like you to verify yourself in <#690216616163672136> so that we moderators can provide an annoyance free experience by checking the users intentions**. **We wish you a pleaseant stay** and **ask you to not block this bot** as it is used to inform our members about punishments.",
        color=COLOR,

    )

    DENIEDMSG = Embed(

        title="Ethical Computing Society",
        description="We're sorry, but we suspect you'd break one of our server's rules, so we didn't verify you. You can appeal using the following email taguar258@hash.fyi",
        color=COLOR,

    )

    # No verification channel stuff
    NOVERIFICATION_WELCOMEMSG = Embed(

        title="Welcome human!",
        description="We are incredibly sorry to welcome you via direct message as it's annoying to most people. Nevertheless, we **chose to use this method instead of a welcome channel as welcome channels decrease privacy** and pretty much just exist to be muted. All we wanted to inform you about is that we welcome you and are present in case of questions. **We wish you a pleaseant stay** and **ask you to not block this bot** as it is used to inform our members about punishments.",
        color=COLOR,

    )

    NOVERIFIEDROLE = 864887304149139516

    NOVERIFICATION_CHANNELNAME = "missing-channels"

    # Log channels
    JOINLEAVE_CHANNEL = 726513291286806549
    MUTECHANNEL = 724244723023478806

    # Other important channels
    LOGCHANNEL = 746076232634073118
    MEMBERCOUNTCHANNEL = 755757420021809322
    ROLESCHANNEL = 690219084469895225
    BUMPCHANNEL = 690269195690049637
    CRYPTOANNOUNCMENTCHANNEL = 866331210087006258

    # The message for the reaction roles
    ROLESMSG = 870466038624583681

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
    REACT_CONGRATS = u"\U0001F389"  #
    REACT_FIRST_BLOOD = u"\U0001F631"  #
    REACT_VERIFICATION = u"\U0001F6C2"  #

    PHELP_MAX_CHANNELS = 10
    PHELP_MAX_TITLE = 20

    PHELP_REMEMBER_AFTER_DAY = 2
    PHELP_DELETE_AFTER_DAY = 4

    PHELP_MUTE_ROLE = 798178561797521459

    # Enable/Disable ISS feature
    ISS_INFO_ENABLED = False

    # Command filter
    GREY_COMMANDS = {  # https://regex101.com/

        r"\b(rm|shred|rmdir)\b": ["as it deletes files and/or folders", "Make sure to create a backup before runing this command and look out for the star '*' char, as it patter matches everything."],
        r"\b(chown|chmod)\s*-R\.*\b": ["as it removes all permission to a file or directory", "We would not suggest running this command."],
        r":(){ :\|: & };:": ["as it is a for bomb and will freeze your computer", "We do not recommend running the command."],
        r"\bdd.*of=.*": ["as it could overwrite important data", "We do not recommend running this, if you do not understand what the command does."],
        r"\bgparted\b": ["as it could format important data", "We do not recommend using this, if you do not want to mess with your data."],
        r"\bparted\b": ["as it could format important data", "We do not recommend using this, if you do not want to mess with your data."],
        r"\bmkfs.*": ["as it could format important data", "We do not recommend using this, if you do not want to mess with your data."],
        r"(\s*|)(>|>>)(\s*|)/dev/.*": ["as it could overwrite important data", "We do not recommend runing this, if you do not understand what the command does."],
        r"\bmv (.|\b) /dev/null\b": ["as it moves data into a black hole", "We do not recommend runing this command at all."],
        r"(\b(wget|curl)\s.*(sh|zsh|bash|sudo|\_)\b)|(\b(sh|zsh|bash|sudo|\_)\s.*(wget|curl)\b)": ["as it downloads and executes unknown content", "Do not run this command if it includes any suspicious/untrustful URL."],
        r"\b(sudo|\_)\s.*(\s*|)(>|>>)(\s*|)(.*\/.*|.*\..*|.*\s*)\b": ["as it can overwrite important data", "Do not run this if you don't want files to be overwritten."],
        r"\\xeb\\x3e\\x5b\\x31\\xc0\\x50\\x54\\x5a": ["as this is part of a very well known malicious code to erase your data", "Do not run this."],  # EXPERIMENTAL
        r"\bcat\s*/dev.*\b": ["as it creates a kernel panic", "We would not suggest running this command."],
        r"^\^.*\^.*\b$": ["as this might be a substitution", "You most likely won't need a substitution, so we suggest you to ignore this command."],
        r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}.*(bash|cmd|sh|zsh))|((bash|cmd|sh|zsh).*\d{3}\.\d{3}\.\d{3}\.\d{3})": ["as this could be a reverse shell", "When running this command, someone could potentially connect with your computer."],
        r"\s*-y\b": ["as it automatically executes tasks without double checking for your user input", "It's adviced to run the command without '-y' argument."],
        r">\s*/proc": ["as it can harm your operating system or cause kernel panics", "It's adviced to not run this command."]
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

    STATUS = ["ECS - TESTING!"]
    MAD_STATUS = ProductionEnv.MAD_STATUS

    GUILD = 776898177302921286

    DATA_FILES_EMPTY = ProductionEnv.DATA_FILES_EMPTY
    DATA_FILES = ProductionEnv.DATA_FILES

    SAVE_FREQUENCY = ProductionEnv.SAVE_FREQUENCY
    BACKUP_FREQUENCY = ProductionEnv.BACKUP_FREQUENCY

    UNVERIFIEDROLE = 776900475161280514
    VERIFIEDROLE = 776900474552844288
    STAFFROLE = 776900462753480714
    MODROLE = 776900459180458015
    TRIALMODROLE = 776900460606259230
    DEVROLE = 776900461630324757
    MUTEDROLE = 776900473391022101
    ROOTROLE = 776900457686892614
    CRYPTOROLE = 870029579211898900
    HELPERROLE = 776900466528616448

    BOTLISTINGROLE = 776900469040611368

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

    #WELCOMEMSG_CHANNEL = 776900487886012466
    JOINLEAVE_CHANNEL = 776900514931146792
    MUTECHANNEL = 776900510796087326
    BUMPCHANNEL = 776900513051967539
    CRYPTOANNOUNCMENTCHANNEL = 776900499853148201

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
    REACT_CONGRATS = ProductionEnv.REACT_CONGRATS
    REACT_FIRST_BLOOD = ProductionEnv.REACT_FIRST_BLOOD
    REACT_VERIFICATION = ProductionEnv.REACT_VERIFICATION

    PHELP_MAX_CHANNELS = 10
    PHELP_MAX_TITLE = 20

    PHELP_REMEMBER_AFTER_DAY = 2
    PHELP_DELETE_AFTER_DAY = 4

    PHELP_MUTE_ROLE = 796390021526585364

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
