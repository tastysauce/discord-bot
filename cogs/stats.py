import discord
import emoji
import json
import os
from datetime import datetime
from discord.ext import commands
from discord.ext import tasks

class StatsCog(commands.Cog, name="Stats"):

    TOTAL_MESSAGES = "Total messages"
    TEXT_MESSAGES = "Text messages"
    IMAGE_MESSAGES = "Images sent"
    LAST_MESSAGE = "Last message"
    HIGHEST_SPICE = "Highest Spice Level"
    SHITTY_MUTES = "Successful shittymutes"
    TIMES_MUTED = "Times muted"
    TIME_FORMAT = "%m/%d/%Y %H:%M:%S"
    SENTIMENT = "Sentiment"

    stats = { }

    def __init__(self, bot):
        self.bot = bot

    def getDefaultDictionary(self):
        defaultDictionary = { 
            self.TOTAL_MESSAGES: 0,
            self.TEXT_MESSAGES: 0,
            self.IMAGE_MESSAGES: 0,
            self.HIGHEST_SPICE: 0,
            self.SHITTY_MUTES: 0,
            self.TIMES_MUTED: 0,
            self.LAST_MESSAGE: "Not recorded",
            self.SENTIMENT: {}
        }
        return defaultDictionary

    @tasks.loop(seconds=600.0)
    async def flushStatsPeriodically(self):
        print("Flushing stats periodically (every 10 minutes)")
        await self.writeToDisk()

    @flushStatsPeriodically.before_loop
    async def before_printer(self):
        print('Waiting prior to flushing...')
        await self.bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_ready(self):
        await self.initStats()

    async def initStats(self):
        if os.path.isfile("stats.csv"):
            await self.loadExistingStats()
            await self.checkForNewGuildsAndMembers()
        else:            
            await self.createNewStatsFile()

        print("Initialized Stats")
        await self.flushStatsPeriodically.start()

    async def loadExistingStats(self):
        with open('stats.csv', newline='') as csvFile:
            self.stats = json.loads(csvFile.read())
            print("Loaded stats for guilds: " + str(self.stats.keys()))

    async def checkForNewGuildsAndMembers(self):
        print("Checking for new servers or members")
        # See if the bot is in guilds that we aren't tracking yet
        print("Existing keys " + str(self.stats.keys()))
        for guild in self.bot.guilds:
            # Add new guild
            guildIDString = str(guild.id)
            if not guildIDString in self.stats.keys():
                print("Found new guild: " + guildIDString)
                self.stats[guildIDString] = self.getDefaultDictionary()
                for member in guild.members:
                    memberIDString = str(member.id)
                    self.stats[guildIDString][memberIDString] = self.getDefaultDictionary()
            # Check members
            else:
                for member in guild.members:
                    memberIDString = str(member.id)
                    if not memberIDString in self.stats[guildIDString].keys():
                        print("Found new member, " + member.name + ", in " + guild.name)
                        self.stats[guildIDString][memberIDString] = self.getDefaultDictionary()
        print("Completed new server and member check")

    async def createNewStatsFile(self):
        print("Initializing stats")
        for guild in self.bot.guilds:
            guildIDString = str(guild.id)
            self.stats[guildIDString] = {}
            print("Adding server: " + guild.name + " with id: " + str(guild.id))

            for member in guild.members:
                memberIDString = str(member.id)
                print("Adding " + member.name + " to " + guild.name)
                self.stats[guildIDString][memberIDString] = self.getDefaultDictionary()

        await self.writeToDisk()
        print("Completed initializing stats")

    async def writeToDisk(self):
        print("Writing stats to disk")
        csvFile = open("stats.csv","w+")
        csvFile.write(json.dumps(self.stats))
        print("Completed writing stats to disk")

    async def flush(self, context):
        await context.send("Flushing stats to disk...")
        await self.writeToDisk()
        await context.send("Done flushing stats to stats.csv")

    async def statsFor(self, context, target):
        target = target.strip("<!@>")
        target = await commands.MemberConverter().convert(context, target)
        targetStats = self.stats[str(target.guild.id)][str(target.id)]
        stats = "Stats for **" + target.name + "**:" + " *(id: " + str(target.id) + ")*\n"
        for key, value in targetStats.items():
            if key == self.SENTIMENT:
                continue
            stats = stats + (key + ": **" + str(value)) + "**\n"
        await context.send(stats)

    # Types
    OVERALL_TYPE = "overall"
    TEXT_TYPE = "text"
    IMAGE_TYPE = "images"
    SPICE_TYPE = "spice"
    SHITTY_MUTES_TYPE = "shittymutes"
    TIMES_MUTED_TYPE = "muted"
    UNKNOWN_TYPE = "unknown"

    typeToKeyMap = {
        OVERALL_TYPE: TOTAL_MESSAGES,
        TEXT_TYPE: TEXT_MESSAGES,
        IMAGE_TYPE: IMAGE_MESSAGES,
        SPICE_TYPE: HIGHEST_SPICE,
        SHITTY_MUTES_TYPE: SHITTY_MUTES,
        TIMES_MUTED_TYPE: TIMES_MUTED
    }

    async def listTop(self, context, inputType):
        # Validate the input
        sortKey = self.UNKNOWN_TYPE
        if inputType in self.typeToKeyMap.keys():
            sortKey = self.typeToKeyMap[inputType]
        if sortKey == self.UNKNOWN_TYPE:
            await context.send("Unrecognized type: " + inputType)
            return

        # Get list of all users and sort it
        serverID = str(context.message.author.guild.id)
        members = self.stats[serverID]
        sortedMembers = []        
        if sortKey == self.HIGHEST_SPICE:
            sortedMembers = sorted(members.items(), key=lambda x: str(x[1][sortKey]).count(emoji.demojize("🌶")), reverse=True)
        else:
            sortedMembers = sorted(members.items(), key=lambda x: x[1][sortKey], reverse=True)

        message = "**" + sortKey + "**" + "\n"
        for memberID, dictionary in sortedMembers:
            try:
                member = await commands.MemberConverter().convert(context, memberID)
                value = dictionary[sortKey]
                message = message + member.name + ": " + str(value) + "\n"
            except Exception:
                pass

        await context.send(message)

    FLUSH = "flush"
    FOR = "for"
    TOP = "top"

    functionMap = {
        FLUSH: flush,
        FOR: statsFor,
        TOP: listTop
    }

    @commands.command(name="stats")
    async def startBotCommand(self, context, *arguments):
        commandName = arguments[0]
        function = self.functionMap[commandName]
        if len(arguments) == 1:
            await function(self, context)
        elif len(arguments) == 2:
            secondArg = arguments[1]
            await function(self, context, secondArg)
        elif len(arguments) == 3:
            secondArg = arguments[1]
            thirdArg = arguments[2]
            await function(self, context, secondArg, thirdArg)

    @commands.Cog.listener()
    async def on_message(self, message):
        memberID = str(message.author.id)
        guildID = str(message.author.guild.id)

        # last message
        self.stats[guildID][memberID][self.LAST_MESSAGE] = datetime.now().strftime(self.TIME_FORMAT)

        # total
        totalMessages = self.stats[guildID][memberID][self.TOTAL_MESSAGES] + 1
        self.stats[guildID][memberID][self.TOTAL_MESSAGES] = totalMessages

        # images
        if len(message.attachments) > 0:
            totalImages = self.stats[guildID][memberID][self.IMAGE_MESSAGES] + 1
            self.stats[guildID][memberID][self.IMAGE_MESSAGES] = totalImages

        # text
        if len(message.content) > 0:
            totalText = self.stats[guildID][memberID][self.TEXT_MESSAGES] + 1
            self.stats[guildID][memberID][self.TEXT_MESSAGES] = totalText


    @commands.Cog.listener()
    async def on_member_join(self, member):
        print("New member named " + member.name + " joined the " + member.guild.name + " server")
        if not str(member.id) in self.stats[str(member.guild.id)].keys():
            print("Added record for " + member.name + " in the " + member.guild.name + " server")
            self.stats[str(member.guild.id)][str(member.id)] = self.getDefaultDictionary()

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        print("We've joined a new guild named " + guild.name)
        if not str(member.id) in self.stats[str(member.guild.id)].keys():
            print("Added record for " + guild.name)
            self.stats[str(guild.id)] = {}
            for member in guild.members:
                self.stats[str(guild.id)][str(member.id)] = self.getDefaultDictionary()

    # other modules can access this
    async def setValueForKey(self, member, key, value):
        print("Setting " + key + " for " + member.name + " in " + member.guild.name)
        self.stats[str(member.guild.id)][str(member.id)][key] = value

    # other modules can access this
    async def getValueForKey(self, member, key):
        # Check that the key exists
        if not key in self.stats[str(member.guild.id)][str(member.id)].keys():
            self.stats[str(member.guild.id)][str(member.id)][key] = 0

        print("Getting " + key + " for " + member.name + " in " + member.guild.name)
        return self.stats[str(member.guild.id)][str(member.id)][key]


def setup(bot):
    bot.add_cog(StatsCog(bot))