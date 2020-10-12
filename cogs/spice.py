import discord
import asyncio
import emoji
import csv
from discord.ext import commands

class SpiceCog(commands.Cog, name="Spice"):

	spiceDeltaBadWords = 0.5
	spiceDeltaTerribleWords = 1.25
	spiceLevel = 0 #initially 0 and incremented when someone trips the array
	spiceDecrementInterval = 300 # 5 minutes in seconds

	terribleWords = []
	badWords = []

	spiceChamps = {}
	champsThatHaveBeenWarned = []
	champsToMute = []

	verbose = False

	def __init__(self, bot):
		self.bot = bot
		self.loadWordsFromDisk()
		print("Initialized Spice")

	def loadWordsFromDisk(self):
		with open("badWords.csv", newline='') as csvFile:
			reader = csv.reader(csvFile, delimiter=",")
			for row in reader:
				self.badWords = row
		with open("terribleWords.csv", newline='') as csvFile:
			reader = csv.reader(csvFile, delimiter=",")
			for row in reader:
				self.terribleWords = row

	@commands.Cog.listener()
	async def on_ready(self):
		task = self.bot.loop.create_task(self.periodicallyDecrementSpice(self.spiceDecrementInterval))
		await task

	@commands.command(name="level")
	async def level(self, ctx, target):
		target = target.strip("<!@>")
		member = await commands.MemberConverter().convert(ctx, target)

		levelToDisplay = 0
		if member in self.spiceChamps:
			levelToDisplay = round(self.spiceChamps[member])

		await ctx.channel.send(member.name + "'s spice level: " + self.spiceLevelToEmoji(levelToDisplay))

	@commands.command(name="yup", help="mutes the champs")
	async def muteTheChamp(self, ctx):

		if len(self.champsToMute) == 0:
			print("nobody to mute")
			return

		taskList = []
		for champ in self.champsToMute:
		 	task = asyncio.ensure_future(self.muteTarget(ctx, champ, 300))

	async def muteTarget(self, ctx, champ, duration):
			await ctx.send("Timing out " + champ.name + " for 5 minutes")
			mutedRole = discord.utils.get(champ.guild.roles, name="muted")
			await champ.add_roles(mutedRole)
			await asyncio.sleep(duration)

			await ctx.send(champ.name + " is very calm now")
			await champ.remove_roles(mutedRole)

			self.spiceChamps.pop(champ, None)
			self.champsToMute.remove(champ)
			self.champsThatHaveBeenWarned.remove(champ)

	@commands.Cog.listener()
	async def on_message(self, message):
		# Don't listen to messages from ourself
		if message.author == self.bot.user:
			return

		# Only run in the test channel for now
		# if not message.channel.id == BOT_CHANNEL_ID:
		# 	return

		levelToDisplay = -1

		for badWord in self.badWords:
			if badWord in message.content.split():

				#increment spice level and record name of edgy spice champ
				self.spiceLevel = self.spiceLevel + self.spiceDeltaBadWords

				# maintain a max of 5 peppers
				if self.spiceLevel > 5:
					self.spiceLevel = 5

				# record the value for the user or add an entry for the rising champ
				if message.author in self.spiceChamps:
					newChampLevel = self.spiceChamps[message.author] + self.spiceDeltaBadWords
					self.spiceChamps[message.author] = newChampLevel
					levelToDisplay = round(newChampLevel)
				else:
					self.spiceChamps[message.author] = self.spiceDeltaBadWords
					levelToDisplay = self.spiceDeltaBadWords
				# only allow 1 change per message
				break

		# but what if it's a terrible word
		for terribleWord in self.terribleWords:
			if terribleWord in message.content.split():

				#increment spice level and record name of edgy spice champ
				self.spiceLevel = self.spiceLevel + self.spiceDeltaTerribleWords

				# maintain a max of 5 peppers
				if self.spiceLevel > 5:
					self.spiceLevel = 5

				# record the value for the user or add an entry for the rising champ
				if message.author in self.spiceChamps:
					newChampLevel = self.spiceChamps[message.author] + self.spiceDeltaTerribleWords
					self.spiceChamps[message.author] = newChampLevel
					levelToDisplay = round(newChampLevel)
				else:
					self.spiceChamps[message.author] = self.spiceDeltaTerribleWords
					levelToDisplay = self.spiceDeltaTerribleWords
				# only allow 1 change per message
				break

		# round the level so people can't swear once and achieve pepper status
		# show the new level of someone's having a bad day
		if self.verbose and round(levelToDisplay) >= 3 and round(levelToDisplay) <= 5 and not message.author in self.champsThatHaveBeenWarned:
			await message.channel.send(message.author.name + " spice level: " + self.spiceLevelToEmoji(levelToDisplay))

		# only record if we set the value to something
		if levelToDisplay > -1:
			await self.recordSpiceStat(message.author, levelToDisplay)
		await self.checkToMuteChamps(message)

	async def recordSpiceStat(self, member, value):
		# for cog in self.bot.cogs:
		# 	self.bot.get_cog(cog)
		# 	print(cog.title())
		stats = self.bot.get_cog("Stats")
		key = stats.HIGHEST_SPICE
		oldValue = await stats.getValueForKey(member, key)
		# the value may be a string of peppers
		if isinstance(oldValue, str):
			oldValue = oldValue.count(emoji.demojize("🌶"))
		if value > oldValue:
			await stats.setValueForKey(member, key, self.spiceLevelToEmoji(value))

	async def checkToMuteChamps(self, message):

		lengthOfWarnings = len(self.champsThatHaveBeenWarned)
		listOfChampNames = []

		for champ in self.spiceChamps.keys():
			if self.spiceChamps[champ] >= 5:
				listOfChampNames.append(champ.name)
				if not champ in self.champsToMute:
					self.champsToMute.append(champ)
				if not champ in self.champsThatHaveBeenWarned:
					self.champsThatHaveBeenWarned.append(champ)

		if self.verbose and len(self.champsThatHaveBeenWarned) > lengthOfWarnings:
			messageToSend = "Type !yup to mute the current champs: "  + ", ".join(listOfChampNames)
			await message.channel.send(messageToSend)

	def spiceLevelToEmoji(self, level: int):
		currentLevel = 0
		string = ""

		# return baby level early if level is 0
		if level == 0:
			return emoji.demojize("👶")

		while currentLevel < level:
			string = string + emoji.demojize("🌶")
			currentLevel = currentLevel + 1

		return string

	async def periodicallyDecrementSpice(self, timeout):
		while True:
			await asyncio.sleep(timeout)
			if self.spiceLevel > 0:
				self.spiceLevel = self.spiceLevel - 1
				for key in self.spiceChamps.keys():
					newLevel = self.spiceChamps[key] - 1
					if newLevel < 0:
						newLevel = 0
					self.spiceChamps[key] = newLevel

			if self.spiceLevel <= 0:
				self.spiceLevel = 0
				self.spiceChamps = {}
				self.spiceChampToMute = []

	SET = "set"
	VERBOSE = "verbose"
	SILENT = "silent"

	async def changeVerbosity(self, context, verbosityLevel):
		if verbosityLevel == self.VERBOSE:
			self.verbose = True
			await context.send("Spice module: Verbose")
		elif verbosityLevel == self.SILENT:
			self.verbose = False
			await context.send("Spice module: Silent")

	functionMap = {
		SET: changeVerbosity,
	}

	@commands.has_role("botmancer")
	@commands.command(name="spice")
	async def startBotCommand(self, context, *arguments):

		if not len(arguments) == 2:
			await context.send("Expected two arguments, but got " + str(len(arguments)))
			return

		commandName = arguments[0]
		optionName = arguments[1]

		function = self.functionMap[commandName]
		await function(self, context, optionName)

def setup(bot):
	bot.add_cog(SpiceCog(bot))




