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

	spiceChamps = {}
	terribleWords = []
	badWords = []
	spiceChampToMute = ""

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
		print(self.terribleWords)

	# Spicy meter

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

	@commands.Cog.listener()
	async def on_message(self, message):
		# Don't listen to messages from ourself
		if message.author == self.bot.user:
			return

		# Only run in the test channel for now
		# if not message.channel.id == BOT_CHANNEL_ID:
		# 	return

		levelToDisplay = 0

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
		if round(levelToDisplay) == 3:
			await message.channel.send(message.author.name + " spice level: " + spiceLevelToEmoji(levelToDisplay))

		if levelToDisplay >= 5 and self.spiceChampToMute == "":
			await message.channel.send("MUTE THE SPICE CHAMP?? Type !yup to mute " + message.author.name)
			self.spiceChampToMute = message.author
		else: 
			self.spiceChampToMute = ""

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

def setup(bot):
	bot.add_cog(SpiceCog(bot))




