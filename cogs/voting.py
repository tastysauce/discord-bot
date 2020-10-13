import discord
from discord.ext import commands

class VotingCog(commands.Cog, name="Voting"):

	def __init__(self, bot):
		self.bot = bot
		print("Initialized Voting")

	currentVotes = {}

	@commands.command(name="vote")
	async def voteVoice(self, ctx, target):

		# Get current voice channel where vote originated from
		channel = ctx.author.voice.channel
		target = target.strip("<!@>")
		member = await commands.MemberConverter().convert(ctx, target)

		# Check if there's already a vote for this channel
		if channel in self.currentVotes:
			await ctx.channel.send("There's already a vote for " + channel.name)
			return

		# add empty array of votes
		self.currentVotes[channel] = {}
		# Get the member count of that channel
		channelMembersCount = len(channel.members)

		if channelMembersCount <= 2:
			await ctx.channel.send("Can't start a vote with " + channelMembersCount + " people")
			return

		requiredToMute = round(channelMembersCount / 2)
		self.currentVotes[channel]["REQUIRED_TO_MUTE"] = requiredToMute
		self.currentVotes[channel]["TARGET"] = member

		await ctx.channel.send("Mute " + member.name + " in " + channel.name + "? " + str(requiredToMute) + " votes required.")
		await ctx.channel.send("Vote !yes or !no")

		await asyncio.sleep(60)
		if channel in self.currentVotes:
			await ctx.channel.send("Vote to mute " + member.name + " timed out after 1 minute")
			self.currentVotes.pop(channel, None)
	 

	@commands.command(name="yes")
	async def voteYes(self, ctx):
		channel = ctx.author.voice.channel
		if channel in currentVotes:
			self.currentVotes[channel][ctx.author] = "yes"
			await checkVotes(ctx)

	@commands.command(name="no")
	async def voteNo(self, ctx):

		channel = ctx.author.voice.channel
		if channel in self.currentVotes:
			self.currentVotes[channel][ctx.author] = "no"
			await checkVotes(ctx)

	async def checkVotes(self, ctx):
		channel = ctx.author.voice.channel
		if channel in self.currentVotes:
			member = self.currentVotes[channel]["TARGET"]
			keys = self.currentVotes[channel].keys()
			if len(keys) < self.currentVotes[channel]["REQUIRED_TO_MUTE"]:
				return
			else:
				yesVotes = 0
				for key in keys:
					if self.currentVotes[channel][key] == "yes":
						yesVotes = yesVotes + 1
				if yesVotes >= self.currentVotes[channel]["REQUIRED_TO_MUTE"]:
					await self.recordTimesMuted(member)
					await ctx.send("Muting " + member.name + " for 2 minutes")
					await member.edit(mute=True)
					mutedRole = discord.utils.get(member.guild.roles, name="muted")
					await member.add_roles(mutedRole)

					# Unmute after duration
					# not sure what stacking up mutes will do.  probably disasterous
					await asyncio.sleep(120)
					await member.edit(mute=False)
					await member.remove_roles(mutedRole)
					await ctx.send(member.name + " is free again!")
					currentVotes.pop(channel, None)

	async def recordTimesMuted(self, member):
		stats = self.bot.get_cog("Stats")
		key = stats.TIMES_MUTED
		value = await stats.getValueForKey(member, key) + 1
		await stats.setValueForKey(member, key, value)

def setup(bot):
	bot.add_cog(VotingCog(bot))