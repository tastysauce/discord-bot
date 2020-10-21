import discord
from discord.ext import commands
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from datetime import datetime, timedelta
import pandas as pd

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

		string = "Sentiment for " + member.name + "\n"

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
			if not key in memberSentimentKeys:
				continue
			dayArray = memberSentiment[key]
			sentimentValueCount = sentimentValueCount + len(dayArray)
			for value in dayArray:
				sentimentValue = sentimentValue + value

		weeklySentimentValue = sentimentValue / sentimentValueCount
		roundedSentiment = round(weeklySentimentValue, 3)

		string = "This week: " + "**" + self.sentimentValueToString(roundedSentiment) + "**\n"
		return string

	def sentimentValueToString(self, sentimentValue):
		if sentimentValue <= -0.7:
			return "alt f4 (" + str(sentimentValue) + ")"
		elif sentimentValue > -0.7 and sentimentValue <= -0.5:
			return "mad (" + str(sentimentValue) + ")"
		elif sentimentValue > -0.5 and sentimentValue < -0.05:
			return "bleh (" + str(sentimentValue) + ")"
		elif sentimentValue >= -0.05 and sentimentValue <= 0.05:
			return "neutral (" + str(sentimentValue) + ")"
		elif sentimentValue > 0.05 and sentimentValue <= 0.5:
			return "good day (" + str(sentimentValue) + ")"
		elif sentimentValue > 0.5 and sentimentValue <= 0.6:
			return "great day (" + str(sentimentValue) + ")"
		elif sentimentValue > 0.6:
			return "probably andy (" + str(sentimentValue) + ")"
		else:
			return "mike's a shitty coder and didn't handle this: " + str(sentimentValue)


	FOR = "for"
	TOP = "top"

	functionMap = {
		FOR: sentimentFor
	}

	@commands.command(name="sentiment")
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