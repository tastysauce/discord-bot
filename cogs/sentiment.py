import discord
from discord.ext import commands
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from datetime import datetime
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
			await message.channel.send(string)
		
	async def storeSentiment(self, message, sentiment):

		member = message.author
		newSentiment = sentiment[self.COMPOUND]
		
		todayKey = datetime.now().strftime(self.TIME_FORMAT)
		# key is Y-M-D 

		userSentiment = await self.stats.getValueForKey(member, self.SENTIMENT)
		if not todayKey in userSentiment.keys():
			print(member.name + ": No value yet for key: " + todayKey)
			userSentiment[todayKey] = [newSentiment]
			await self.stats.setValueForKey(member, self.SENTIMENT, userSentiment)
			return

		todaysSentiment = userSentiment[todayKey]
		todaysSentiment.append(newSentiment)
		userSentiment[todayKey] = todaysSentiment
		await self.stats.setValueForKey(member, self.SENTIMENT, userSentiment)		

	@commands.command(name="sentiment")
	async def getSentimentFor(self, context, target):
		target = target.strip("<!@>")
		target = await commands.MemberConverter().convert(context, target)
		targetStats = await self.stats.getValueForKey(target, self.SENTIMENT)


		# Yearly

		await context.send(targetStats.items())



def setup(bot):
	bot.add_cog(SentimentCog(bot))