import discord
import asyncio
import random
from discord.ext import commands

class ShittyCommands(commands.Cog, name="Shitty Commands"):

	def __init__(self, bot):
		self.bot = bot
		print("Initialized ShittyCommands")

	# list of members
	shittyMutedUsers = []
	# member, target
	shittyMutesInProgress = {}

	@commands.command(name="shittymute", help="mutes the champs")
	async def startShittyMute(self, ctx, target):

		target = target.strip("<!@>")
		target = await commands.MemberConverter().convert(ctx, target)

		if target in self.shittyMutedUsers:
			await ctx.send(target.name + " is already muted")
			return

		if ctx.message.author in self.shittyMutesInProgress.keys():
			print("author already muting someone")
			return

		await ctx.send(ctx.author.name + ": Pick a # between 1 and 3")

		# self.shittyMutesInProgress[ctx.author] = target

		# Wait for response
		def check(message: discord.Message):
			return message.author == ctx.author and self.convertMessageToInt(message)

		try:
			guess = await self.bot.wait_for('message', check=check, timeout=30)
		except asyncio.TimeoutError:
			await ctx.author.channel.send(ctx.author.name + " never guessed!")
			return

		if self.determineSuccess(int(guess.content)):
			await ctx.send("Success! Timing out " + target.name + " for 1 minute")
			await self.recordShittymuteSuccess(ctx.author)
			await self.muteTarget(ctx, target)
		else:
			await ctx.send(ctx.author.name + " accidentally muted themself for a minute!")
			await self.muteTarget(ctx, ctx.message.author)

	async def muteTarget(self, ctx, target):
		await self.recordTimesMuted(target)
		mutedRole = discord.utils.get(target.guild.roles, name="muted")
		await target.add_roles(mutedRole)
		await asyncio.sleep(60)
		await ctx.send(target.name + " has escaped shittymute")
		await target.remove_roles(mutedRole)

	def determineSuccess(self, value):
		randomNumber = random.randint(1,3)
		return value == randomNumber

	def convertMessageToInt(self, message):
		try:
			int(message.content)
			return True
		except ValueError:
			return False

	async def recordShittymuteSuccess(self, member):
		stats = self.bot.get_cog("Stats")
		key = stats.SHITTY_MUTES
		value = await stats.getValueForKey(member, key) + 1
		await stats.setValueForKey(member, key, value)

	async def recordTimesMuted(self, member):
		stats = self.bot.get_cog("Stats")
		key = stats.TIMES_MUTED
		value = await stats.getValueForKey(member, key) + 1
		await stats.setValueForKey(member, key, value)
		

def setup(bot):
	bot.add_cog(ShittyCommands(bot))