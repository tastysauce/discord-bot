import discord
import asyncio
import emoji
from discord.ext import commands

class SpiceCog(commands.Cog, name="Spice"):

	SPICE_DELTA = 0.5
	SPICE_TERRIBLE_DELTA = 1.25
	SPICE_LEVEL = 0 #initially 0 and incremented when someone trips the array
	SPICE_DECREMENT_INTERVAL = 300 # 5 minutes in seconds
	
	SPICE_CHAMPS = {}
	ARRAY_OF_TERRIBLE_WORDS = ["1080p", "1440p", "1080", "1440", "144hz", "144", "90", "90hz", "clown", ":90hz:", "fake", "blm", "trump", "antifa", "alt f4", "altf4", "f4", "intel", "nvidia", "amd"]
	ARRAY_OF_BAD_WORDS = ["anal","anus","arse","ass","ballsack","balls","bastard","bitch","biatch","bloody","blowjob","blow" "job","bollock","bollok","boner","butt","buttplug","clitoris","cock","coon","crap","cunt","damn","dick","dildo","dyke","fag","feck","fellate","fellatio","felching","fuck","fudgepacker","fudge" "packer","flange","Goddamn","hell","homo","jerk","jizz","knobend","knob" "end","muff","nigger","nigga","omg","penis","piss","poop","prick","pube","pussy","queer","scrotum","sex","shit","sh1t","slut","smegma","spunk","tit","tosser","turd","twat","vagina","wank","whore"]
	SPICE_CHAMP_TO_MUTE = ""

	def __init__(self, bot):
		self.bot = bot

	# Spicy meter

	@commands.Cog.listener()
	async def on_ready(self):
		task = self.bot.loop.create_task(self.periodicallyDecrementSpice(self.SPICE_DECREMENT_INTERVAL))
		await task

	@commands.command(name="level")
	async def level(self, ctx, target):
		target = target.strip("<!@>")
		member = await commands.MemberConverter().convert(ctx, target)

		levelToDisplay = 0
		if member in self.SPICE_CHAMPS:
			levelToDisplay = round(self.SPICE_CHAMPS[member])

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

		for badWord in self.ARRAY_OF_BAD_WORDS:
			if badWord in message.content.split():

				#increment spice level and record name of edgy spice champ
				self.SPICE_LEVEL = self.SPICE_LEVEL + self.SPICE_DELTA

				# maintain a max of 5 peppers
				if self.SPICE_LEVEL > 5:
					self.SPICE_LEVEL = 5

				# record the value for the user or add an entry for the rising champ
				if message.author in self.SPICE_CHAMPS:
					newChampLevel = self.SPICE_CHAMPS[message.author] + self.SPICE_DELTA
					self.SPICE_CHAMPS[message.author] = newChampLevel
					levelToDisplay = round(newChampLevel)
				else:
					self.SPICE_CHAMPS[message.author] = self.SPICE_DELTA
					levelToDisplay = self.SPICE_DELTA
				# only allow 1 change per message
				break

		# but what if it's a terrible word
		for terribleWord in self.ARRAY_OF_TERRIBLE_WORDS:
			if terribleWord in message.content.split():

				#increment spice level and record name of edgy spice champ
				self.SPICE_LEVEL = self.SPICE_LEVEL + self.SPICE_TERRIBLE_DELTA

				# maintain a max of 5 peppers
				if self.SPICE_LEVEL > 5:
					self.SPICE_LEVEL = 5

				# record the value for the user or add an entry for the rising champ
				if message.author in self.SPICE_CHAMPS:
					newChampLevel = self.SPICE_CHAMPS[message.author] + self.SPICE_TERRIBLE_DELTA
					self.SPICE_CHAMPS[message.author] = newChampLevel
					levelToDisplay = round(newChampLevel)
				else:
					self.SPICE_CHAMPS[message.author] = self.SPICE_TERRIBLE_DELTA
					levelToDisplay = self.SPICE_TERRIBLE_DELTA
				# only allow 1 change per message
				break

		# round the level so people can't swear once and achieve pepper status
		# show the new level of someone's having a bad day
		if round(levelToDisplay) == 3:
			await message.channel.send(message.author.name + " spice level: " + spiceLevelToEmoji(levelToDisplay))

		if levelToDisplay >= 5:
			await message.channel.send("MUTE THE SPICE CHAMP?? Type !yup to mute " + message.author.name)
			self.SPICE_CHAMP_TO_MUTE = message.author
		else: 
			self.SPICE_CHAMP_TO_MUTE = ""

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
			if self.SPICE_LEVEL > 0:
				self.SPICE_LEVEL = self.SPICE_LEVEL - 1
				for key in self.SPICE_CHAMPS.keys():
					newLevel = self.SPICE_CHAMPS[key] - 1
					if newLevel < 0:
						newLevel = 0
					self.SPICE_CHAMPS[key] = newLevel

			if self.SPICE_LEVEL <= 0:
				self.SPICE_LEVEL = 0
				self.SPICE_CHAMPS = {}

def setup(bot):
	bot.add_cog(SpiceCog(bot))




