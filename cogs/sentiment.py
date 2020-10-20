import discord
from discord.ext import commands

import re
import csv
import pprint
import nltk.classify
import pickle

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

class SentimentCog(commands.Cog, name="Sentiment"):

	analyzer = SentimentIntensityAnalyzer()

	def __init__(self, bot):
		self.bot = bot
		print("Initialized Sentiment")

	@commands.Cog.listener()
	async def on_message(self, message):

		if not message.channel.id == 762411266860908574:
			return

		if message.author == self.bot.user:
			return

		vs = self.analyzer.polarity_scores(message.content)
		string = "{}\n{}".format(message.content, str(vs))
		print(string)
		await message.channel.send(string)
		

	@commands.Cog.listener()
	async def on_ready(self):
		await self.initTrainer()

	async def initTrainer(self):
		print("Loaded")


def setup(bot):
	bot.add_cog(SentimentCog(bot))