import config.tokens as tokens
from discord import Embed


# target instance
TESTING = True


class ProductionEnv:
    """ Config for Production Environment
    """
    # BOT INFORMATION
    TOKEN = tokens.TOKEN
    PREFIX = "!"  # note some commands will utilize slashcommands
    IGNORED_COMMANDS = ["d"]
    COLOR = 0x57408b

    # GUILD INFORMATION
    GUILD = 690212435306741901

    # ROLES
    ROOTROLE = 690212500784152591
    MODROLE = 690212787087081554
    DEVROLE = 690212865688469545
    TRIALMODROLE = 690232623167045703
    STAFFROLE = 724251714613411851
    HELPERROLE = 690212809648242693
    CRYPTOROLE = 867784404243578940
    BOTLISTINGROLE = 690260998934102080
    VERIFIEDROLE = 690212961876312094
    NOVERIFIEDROLE = 864887304149139516
    UNVERIFIEDROLE = 732212270385332225
    PHELP_MUTE_ROLE = 798178561797521459
    MUTEDROLE = 690254996004012050

    # CATEGORIES
    VERIFICATIONCHANNELCAT = 690212435310936085
    PHELPCATEGORY = 798177254873235487

    # CHANNELS
    MEMBERCOUNTCHANNEL = 755757420021809322
    ROLESCHANNEL = 690219084469895225
    JOINLEAVE_CHANNEL = 726513291286806549
    MUTECHANNEL = 724244723023478806
    LOGCHANNEL = 746076232634073118
    BUMPCHANNEL = 690269195690049637
    CRYPTOANNOUNCMENTCHANNEL = 866331210087006258

    # VOTE MUTE
    VOTE_REACTION_MUTE = b"8J+Uhw=="
    VOTE_REACTION_NO_MUTE = b"8J+UiA=="

    TRIP_LEVEL = 0.012

    # CUSTOM ROLES {b64reaction: [rolename, roleid]}
    ROLESMSG = 870466038624583681
    ROLES = {

        b"8J+UlA==": ["ping", 690239204667818102],
        b"4oyo77iP": ["coder", 690243098533822485],
        b"8J+Suw==": ["hacker", 690243125225980007],
        b"8J+Upw==": ["hardware", 726809084975906856],
        b"8J+Svw==": ["linux", 798178796192006174],
        b"8J+UkA==": ["crypto", 870061882667573278],

    }

    # STATUS MESSAGES
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

    # DATA STORING
    SAVE_FREQUENCY = 300  # seconds
    BACKUP_FREQUENCY = 3600  # seconds

    DATA_FILES_EMPTY = {

        "logs": {"logs": []},
        "punishments": {"punishments": []},
        "public_help": {"current_channels": [], "freeze": False},
        "crypto_challenge": {"solution-hash": ""},

    }

    DATA_FILES = DATA_FILES_EMPTY.keys()

    # MODERATION
    BANDELETEMESSAGES = 2  # Delete messages of last 2 days

    # VERIFICATION CHANNEL
    VERIFICATIONENABLED = True
    VERIFICATIONCHANNELNAME = "verification"
    NOVERIFICATION_CHANNELNAME = "missing-channels"

    VTICKET_AUTOCLOSEREMINDER = "Hello {mention}, here is a quick ping as this ticket has been inactive since one day.\nAnother day of inactivity will result in the closing of your ticket."
    VTICKET_AUTOCLOSEREMINDER_DAY = 1  # delta day until reminder is sent
    VTICKET_AUTOCLOSE_DAY = 1  # delta day until ticket is closed after reminder

    VTICKET_TRANSCRIPT_CHANNEL = "1015780526113705985"
    VTICKET_MEDIA_ROLE = "1015780927131103232"

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

    # PUBLIC HELP
    PHELP_MAX_CHANNELS = 10
    PHELP_MAX_TITLE = 20

    PHELP_REMEMBER_AFTER_DAY = 2
    PHELP_DELETE_AFTER_DAY = 4

    # Enable/Disable ISS feature
    ISS_INFO_ENABLED = False

    # PREDEFINED MESSAGES
    WELCOMEMSG = Embed(

        title="Welcome human!",
        description="We are incredibly sorry to welcome you via direct message as it's annoying to most people. Nevertheless, we **chose to use this method instead of a welcome channel as welcome channels decrease privacy** and pretty much just exist to be muted. All we wanted to inform you about is that we welcome you, are present in case of questions, and **would like you to verify yourself in <#690216616163672136> so that we moderators can provide an annoyance free experience by checking the users intentions**. **We wish you a pleaseant stay** and **ask you to not block this bot** as it is used to inform our members about punishments.",
        color=COLOR,

    )

    ACCEPTEDMSG = Embed(

        title="Thank you so much for your time!",
        description="We just wanted to quickly inform that you were successfully verified.\nWe wish you a pleaseant stay.",
        color=COLOR,

    )

    DENIEDMSG = Embed(

        title="Ethical Computing Society",
        description="We're sorry, but we suspect you'd break one of our server's rules, so we didn't verify you. You can appeal using the following email taguar258@hash.fyi",
        color=COLOR,

    )

    NOVERIFICATION_WELCOMEMSG = Embed(

        title="Welcome human!",
        description="We are incredibly sorry to welcome you via direct message as it's annoying to most people. Nevertheless, we **chose to use this method instead of a welcome channel as welcome channels decrease privacy** and pretty much just exist to be muted. All we wanted to inform you about is that we welcome you and are present in case of questions. **We wish you a pleaseant stay** and **ask you to not block this bot** as it is used to inform our members about punishments.",
        color=COLOR,

    )

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

    # SELF-REACTIONS
    REACT_ERROR = "\u2757"    # https://www.fileformat.info/info/unicode/
    REACT_SUCCESS = "\u2705"  #
    REACT_CONGRATS = u"\U0001F389"  #
    REACT_FIRST_BLOOD = u"\U0001F631"  #
    REACT_VERIFICATION = u"\U0001F6C2"  #

    # COMMAND FILTER
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


class TestingEnv(ProductionEnv):
    """ Config for Production Environment
    """
    # BOT INFORMATION
    TOKEN = tokens.TOKENTESTING

    # STATUS MESSAGES
    STATUS = ["ECS - TESTING!"]

    # GUILD INFORMATION
    GUILD = 776898177302921286

    # ROLES
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
    NOVERIFIEDROLE = 861011856025059359
    PHELP_MUTE_ROLE = 796390021526585364
    VTICKET_MEDIA_ROLE = 932091114545090630

    # CUSTOM ROLES {b64reaction: [rolename, roleid]}
    ROLESMSG = 776901414940049438
    ROLES = {
        b"8J+UlA==": ["ping", 776900472358305833],
        b"4oyo77iP": ["coder", 776900472086331452],
        b"8J+Suw==": ["hacker", 776900471004594188],
        b"8J+Upw==": ["hardware", 776900470601154580],
        b"8J+Svw==": ["linux", 796079401544450109],
    }

    # CATEGORIES
    VERIFICATIONCHANNELCAT = 776900479946194955
    PHELPCATEGORY = 795634619927363605

    # CHANNELS
    LOGCHANNEL = 776900515640115250
    MEMBERCOUNTCHANNEL = 776900480521338951
    ROLESCHANNEL = 776900486145900566
    JOINLEAVE_CHANNEL = 776900514931146792
    MUTECHANNEL = 776900510796087326
    BUMPCHANNEL = 776900513051967539
    CRYPTOANNOUNCMENTCHANNEL = 776900499853148201
    VTICKET_TRANSCRIPT_CHANNEL = 932087834607779850


if TESTING:

    config = TestingEnv

else:

    config = ProductionEnv
