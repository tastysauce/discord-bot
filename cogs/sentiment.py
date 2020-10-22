import discord
from discord.ext import commands
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from datetime import datetime, timedelta
from discord.ext import tasks

class SentimentCog(commands.Cog, name="Sentiment"):

	# TODO: Get these keys outta here or out of stats.py
	SENTIMENT = "Sentiment"
	DAYS_SENTIMENT = "sentiment today"
	TIME_FORMAT = "%Y-%m-%d"
	COMPOUND = "compound"


	analyzer = SentimentIntensityAnalyzer()
	stats = None

	def __init__(self, bot):
		self.bot = bot
		print("Initialized Sentiment")

	@commands.Cog.listener()
	async def on_ready(self):
		self.stats = self.bot.get_cog("Stats")
		await self.archiveSentimentPeriodically.start()

	@tasks.loop(seconds=86400.0)
	async def archiveSentimentPeriodically(self):
		print("Archiving sentiment periodically (every 24 hours)")
		await self.archiveAllSentiment()

	@archiveSentimentPeriodically.before_loop
	async def before_printer(self):
		print('Waiting prior to archiving...')
		await self.bot.wait_until_ready()

	@commands.Cog.listener()
	async def on_message(self, message):

		if message.author == self.bot.user:
			return

		sentiment = self.analyzer.polarity_scores(message.content)

		# Store sentiment
		await self.storeSentiment(message, sentiment)

		# Log what's happening if it's in the bot channel
		if message.channel.id == 762411266860908574:
			string = "{}\n{}".format(message.content, str(sentiment))
			print(string)
			# await message.channel.send(string)

	async def archiveAllSentiment(self):
		message = "Compression started..."
		# await context.send(message)
		print(message)
		# This operation is performed for all members in all guilds
		todayKey = datetime.now().strftime(self.TIME_FORMAT)
		for guild in self.bot.guilds:
			# For reporting stats later
			recordsFound = 0
			recordsCompressed = 0

			guildIDString = str(guild.id)
			message = "Looking for data to compress in " + guild.name + " (" + guildIDString+ ")"
			# await context.send(message)
			print(message)
			for member in guild.members:
				memberIDString = str(member.id)
				message = "Fetching sentiment records for " + member.name + " (" + memberIDString+ ")"
				# await context.send(message)
				print(message)

				sentimentDictionary = await self.stats.getValueForKey(member, self.SENTIMENT)
				# Some old users have an int value for sentiment
				if type(sentimentDictionary) is int:
					print("Found invalid sentiment data")
					continue

				print("##### OLD: ")
				print(sentimentDictionary)

				sentimentKeys = sentimentDictionary.keys()
				# Return early if we haven't stored anything
				if len(sentimentKeys) == 0:
					message = "No data stored for " + member.name + "... moving on"
					print(message)
					# await context.send(message)
					continue

				message = str(len(sentimentKeys)) + " days recorded. Checking for compressible data"
				# await context.send(message)
				print(message)

				# new dictionary so that we don't write to something we're reading from
				newSentimentDictionary = { }
				for key in sentimentKeys:

					dayArray = sentimentDictionary[key]
					dayArrayLength = len(dayArray)

					# keep track of stats
					recordsFound = recordsFound + dayArrayLength

					# Don't compress a day that's in progress but abord here so we still record stats
					if key == todayKey:
						newSentimentDictionary[key] = sentimentDictionary[key]
						continue

					# logging
					message = "Found " + str(dayArrayLength) + " records on " + key

					if dayArrayLength <= 1:
						newSentimentDictionary[key] = sentimentDictionary[key]
						message = message + ". Can't compress further"
						# await context.send(message)
						print(message)
						continue

					message = message + ". Compressing..."
					# await context.send(message)
					print(message)

					# average the sentiment and store new array with single value
					sentimentValue = 0
					for record in dayArray:
						recordsCompressed = recordsCompressed + 1
						sentimentValue = sentimentValue + record
					sentimentValue = sentimentValue / dayArrayLength
					newSentimentDictionary[key] = [sentimentValue]

				# sanity check
				oldNumberOfDays = len(sentimentKeys)
				newNumberOfDays = len(newSentimentDictionary.keys())
				message = "Sanity checking...  old days: " + str(oldNumberOfDays) + " new days: " + str(newNumberOfDays)
				if not oldNumberOfDays == newNumberOfDays:
					message = message + " -- bad compression. Aborting."
					# await context.send(message)
					print(message)
					return

				print("##### NEW: ")
				print(newSentimentDictionary)

				await self.stats.setValueForKey(member, self.SENTIMENT, newSentimentDictionary)
				message = message + " -- success"
				# await context.send(message)
				print(message)

			message = "Found " + str(recordsFound) + " records and compressed " + str(recordsCompressed)
			# await context.send(message)
			print(message)

		await self.stats.writeToDisk()



	# We have a ton of sentiment data and it's taking up room in memory and disk
	# We need to compress it
	@commands.has_role("botmancer")
	@commands.command(name="archive")
	async def archiveAllSentimentCommand(self, context):
		context.send("Starting archive...")
		await self.archiveAllSentiment()
		context.send("Archive complete")
		
	async def storeSentiment(self, message, sentiment):

		member = message.author
		newSentiment = sentiment[self.COMPOUND]
		
		todayKey = datetime.now().strftime(self.TIME_FORMAT)
		# key is Y-M-D 

		userSentiment = await self.stats.getValueForKey(member, self.SENTIMENT)
		# clear when this was an int
		if type(userSentiment) is int:
			userSentiment = { }
			print("Converting sentiment from int to fresh dictionary")

		if not todayKey in userSentiment.keys():
			print(member.name + ": No value yet for key: " + todayKey)
			userSentiment[todayKey] = [newSentiment]
			await self.stats.setValueForKey(member, self.SENTIMENT, userSentiment)
			return

		todaysSentiment = userSentiment[todayKey]
		todaysSentiment.append(newSentiment)
		userSentiment[todayKey] = todaysSentiment
		await self.stats.setValueForKey(member, self.SENTIMENT, userSentiment)		

	async def sentimentFor(self, context, member):
		member = member.strip("<!@>")
		member = await commands.MemberConverter().convert(context, member)
		memberSentiment = await self.stats.getValueForKey(member, self.SENTIMENT)

		string = "Titles for " + member.name + "\n"

		# Compute today
		string = string + await self.todayStatsFor(member, memberSentiment)
		string = string + await self.weekStatsFor(member, memberSentiment)

		await context.send(string)


	async def todayStatsFor(self, member, memberSentiment):
		today = datetime.now()
		todayKey = today.strftime(self.TIME_FORMAT)
		todaySentimentValues = memberSentiment[todayKey]
		string = "Today: **No values yet**"
		if len(todaySentimentValues) > 0:
			todayTotal = 0
			for record in todaySentimentValues:
				todayTotal = todayTotal + record
			todaySentiment = todayTotal / len(todaySentimentValues)
			roundedSentiment = round(todaySentiment, 3)
			string = "Today: " + "**" + self.sentimentValueToString(roundedSentiment) + "**\n"
		return string

	async def weekStatsFor(self, member, memberSentiment):
		today = datetime.now()
		startOfWeek = today - timedelta(days=(today.weekday()+1) % 7)

		# generate date keys until current day
		keys = []
		currentDate = startOfWeek
		while currentDate <= today:
			keys.append(currentDate.strftime(self.TIME_FORMAT))
			currentDate = currentDate + timedelta(days=1)

		sentimentValue = 0
		sentimentValueCount = 0
		memberSentimentKeys = memberSentiment.keys()
		for key in keys:
			print(key)
			if not key in memberSentimentKeys:
				continue
			dayArray = memberSentiment[key]
			sentimentValueCount = sentimentValueCount + len(dayArray)
			weeklySentimentValue = 0
			for value in dayArray:
				weeklySentimentValue = weeklySentimentValue + value
				print("adding value " + str(value))
			weeklySentimentValue = weeklySentimentValue / sentimentValueCount
			sentimentValue = sentimentValue + weeklySentimentValue

		roundedSentiment = round(sentimentValue, 3)

		string = "This week: " + "**" + self.sentimentValueToString(roundedSentiment) + "**\n"
		return string

	def sentimentValueToString(self, sentimentValue):
		if sentimentValue < -0.3:
			return "outcast (" + str(sentimentValue) + ")"
		elif sentimentValue < -0.2 and sentimentValue >= -0.3:
			return "despicable (" + str(sentimentValue) + ")"
		elif sentimentValue < -0.1 and sentimentValue >= -0.2:
			return "scoundrel (" + str(sentimentValue) + ")"
		elif sentimentValue < -0.05 and sentimentValue >= -0.1:
			return "unsavory (" + str(sentimentValue) + ")"
		elif sentimentValue < -0.025 and sentimentValue >= -0.05:
			return "rude (" + str(sentimentValue) + ")"
		elif sentimentValue >= -0.025 and sentimentValue <= 0.025:
			return "no title (" + str(sentimentValue) + ")"
		elif sentimentValue > 0.025 and sentimentValue <= 0.05:
			return "fair (" + str(sentimentValue) + ")"
		elif sentimentValue > 0.05 and sentimentValue <= 0.1:
			return "kind (" + str(sentimentValue) + ")"
		elif sentimentValue > 0.1 and sentimentValue <= 0.2:
			return "good (" + str(sentimentValue) + ")"
		elif sentimentValue > 0.2 and sentimentValue <= 0.3:
			return "famed (" + str(sentimentValue) + ")"
		elif sentimentValue > 0.3:
			return "glorious (" + str(sentimentValue) + ")"
		else:
			return "mike's a shitty coder and didn't handle this: " + str(sentimentValue)


	FOR = "for"
	ARCHIVE = "archive"
	TOP = "top"

	functionMap = {
		FOR: sentimentFor,
		ARCHIVE: archiveAllSentimentCommand
	}

	@commands.command(name="title")
	async def getSentimentFor(self, context, *arguments):
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



def setup(bot):
	bot.add_cog(SentimentCog(bot))