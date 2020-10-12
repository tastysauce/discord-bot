import discord
import emoji
import json
import os
from datetime import datetime
from discord.ext import commands

class StatsCog(commands.Cog, name="Stats"):

    TOTAL_MESSAGES = "Total messages"
    TEXT_MESSAGES = "Text-only messages"
    IMAGE_MESSAGES = "Image-only messages"
    LAST_MESSAGE = "Last message"
    TIME_FORMAT = "%m/%d/%Y %H:%M:%S"

    stats = { }

    def __init__(self, bot):
        self.bot = bot
        print("Initialized Stats")


    def getDefaultDictionary(self):
        dictionary = { 
            self.TOTAL_MESSAGES: 0,
            self.TEXT_MESSAGES: 0,
            self.IMAGE_MESSAGES: 0,
            self.LAST_MESSAGE: "Not recorded"
        }
        return dictionary

    @commands.Cog.listener()
    async def on_ready(self):
        await self.initStats()

    async def initStats(self):
        if os.path.isfile("stats.csv"):
            await self.loadExistingStats()
            await self.checkForNewGuildsAndMembers()
        else:            
            await self.createNewStatsFile()

    async def loadExistingStats(self):
        with open('stats.csv', newline='') as csvFile:
            self.stats = json.loads(csvFile.read())
            print("Loaded stats for guilds: " + str(self.stats.keys()))

    async def checkForNewGuildsAndMembers(self):
        print("Checking for new servers or members")
        # See if the bot is in guilds that we aren't tracking yet
        for guild in self.bot.guilds:
            # Add new guild
            if not guild.name in self.stats.keys():
                print("Found new guild: " + guild.name)
                self.stats[guild.name] = self.getDefaultDictionary()
                for member in guild.members:
                    # don't record stats for our bot
                    # if memberName == self.bot.user.name:
                    #     continue
                    self.stats[guild.name][member.name] = self.getDefaultDictionary()
            # Check members
            else:
                for member in guild.members:
                    if not member.name in self.stats[guild.name].keys():
                        print("Found new member, " + member.name + ", in " + guild.name)
                        self.stats[guild.name][member.name] = self.getDefaultDictionary()
        print("Completed new server and member check")

    async def createNewStatsFile(self):
        print("Initializing stats")
        for guild in self.bot.guilds:
            guildName = guild.name
            self.stats[guildName] = {}
            print("Adding server: " + guildName)

            for member in guild.members:
                print("Adding " + member.name + " to " + guild.name)
                memberName = member.name
                # don't record stats for our bot
                # if memberName == self.bot.user.name:
                #     continue
                self.stats[guildName][memberName] = self.getDefaultDictionary()

        await self.writeToDisk()
        print("Completed initializing stats")

    async def writeToDisk(self):
        print("Writing stats to disk")
        csvFile = open("stats.csv","w+")
        csvFile.write(json.dumps(self.stats))
        print("Completed writing stats to disk")

    async def flush(self, context):
        await context.send("Flushing stats to disk...")
        self.writeToDisk()
        await context.send("Done flushing stats to stats.csv")

    async def get(self, context, target):
        target = target.strip("<!@>")
        target = await commands.MemberConverter().convert(context, target)

        targetStats = self.stats[target.guild.name][target.name]
        await context.send(targetStats.items())

    FLUSH = "flush"
    GET = "get"

    functionMap = {
        FLUSH: flush,
        GET: get
    }

    @commands.has_role("botmancer")
    @commands.command(name="stats")
    async def startBotCommand(self, context, *arguments):
        commandName = arguments[0]
        function = self.functionMap[commandName]
        if len(arguments) == 1:
            await function(self, context)
        if len(arguments) == 2:
            optionName = arguments[1]
            await function(self, context, optionName)
        elif len(arguments) == 3:
            thirdArg = arguments[3]
            await function(self, context, thirdArg)

    @commands.Cog.listener()
    async def on_message(self, message):
        memberName = message.author.name
        guildName = message.author.guild.name
        totalMessages = self.stats[guildName][memberName][self.TOTAL_MESSAGES] + 1
        self.stats[guildName][memberName][self.TOTAL_MESSAGES] = totalMessages

    @commands.Cog.listener()
    async def on_member_join(self, member):
        print("New member named " + member.name + " joined the " + member.guild.name + " server")
        if not member.name in self.stats[member.guild.name].keys():
            print("Added record for " + member.name + " in the " + member.guild.name + " server")
            self.stats[member.guild.name][member.name] = self.getDefaultDictionary()

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        print("We've joined a new guild named " + guild.name)
        if not member.name in self.stats[member.guild.name].keys():
            print("Added record for " + guild.name)
            self.stats[guild.name] = {}
            for member in guild.members:
                memberName = member.name
                # don't record stats for our bot
                # if memberName == self.bot.user.name:
                #     continue
                self.stats[guildName][memberName] = self.getDefaultDictionary()


def setup(bot):
    bot.add_cog(StatsCog(bot))