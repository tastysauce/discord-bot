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

    def loadStats(self):
        if os.path.isfile("stats.csv"):
            with open('stats.csv', newline='') as csvFile:
                self.stats = json.loads(csvFile.read())
                print("Loaded stats for guilds: " + str(self.stats.keys()))
        else:
            self.initStats()

    @commands.Cog.listener()
    async def on_ready(self):
        self.loadStats()

    def initStats(self):
        print("Initializing stats")
        for guild in self.bot.guilds:
            guildName = guild.name
            self.stats[guildName] = {}

            for member in guild.members:
                memberName = member.name
                # don't record stats for our bot
                # if memberName == self.bot.user.name:
                #     continue
                self.stats[guildName][memberName] = self.getDefaultDictionary()

        print(self.stats.items())
        csvFile = open("stats.csv","w+")
        csvFile.write(json.dumps(self.stats))

    async def flush(self, context):
        await context.send("Flushing stats to disk...")
        csvFile = open("stats.csv","w+")
        csvFile.write(json.dumps(self.stats))
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

def setup(bot):
    bot.add_cog(StatsCog(bot))