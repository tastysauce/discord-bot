import discord
from discord.ext import commands

class VotingCog(commands.Cog, name="Voting"):

	def __init__(self, bot):
		self.bot = bot

	CURRENT_VOTES = {}

	@commands.command(name="vote")
	async def voteVoice(self, ctx, target):

		# Get current voice channel where vote originated from
		channel = ctx.author.voice.channel
		target = target.strip("<!@>")
		member = await commands.MemberConverter().convert(ctx, target)

		# Check if there's already a vote for this channel
		if channel in self.CURRENT_VOTES:
			await ctx.channel.send("There's already a vote for " + channel.name)
			return

		# add empty array of votes
		self.CURRENT_VOTES[channel] = {}
		# Get the member count of that channel
		channelMembersCount = len(channel.members)

		if channelMembersCount <= 2:
			await ctx.channel.send("Can't start a vote with " + channelMembersCount + " people")
			return

		requiredToMute = round(channelMembersCount / 2)
		self.CURRENT_VOTES[channel]["REQUIRED_TO_MUTE"] = requiredToMute
		self.CURRENT_VOTES[channel]["TARGET"] = member

		await ctx.channel.send("Mute " + member.name + " in " + channel.name + "? " + str(requiredToMute) + " votes required.")
		await ctx.channel.send("Vote !yes or !no")

		await asyncio.sleep(60)
		if channel in self.CURRENT_VOTES:
			await ctx.channel.send("Vote to mute " + member.name + " timed out after 1 minute")
			self.CURRENT_VOTES.pop(channel, None)
	 

	@commands.command(name="yes")
	async def voteYes(self, ctx):
		channel = ctx.author.voice.channel
		if channel in CURRENT_VOTES:
			self.CURRENT_VOTES[channel][ctx.author] = "yes"
			await checkVotes(ctx)

	@commands.command(name="no")
	async def voteYes(self, ctx):

		channel = ctx.author.voice.channel
		if channel in self.CURRENT_VOTES:
			self.CURRENT_VOTES[channel][ctx.author] = "no"
			await checkVotes(ctx)

	async def checkVotes(self, ctx):
		channel = ctx.author.voice.channel
		if channel in self.CURRENT_VOTES:
			member = self.CURRENT_VOTES[channel]["TARGET"]
			keys = self.CURRENT_VOTES[channel].keys()
			if len(keys) < self.CURRENT_VOTES[channel]["REQUIRED_TO_MUTE"]:
				return
			else:
				yesVotes = 0
				for key in keys:
					if self.CURRENT_VOTES[channel][key] == "yes":
						yesVotes = yesVotes + 1
				if yesVotes >= self.CURRENT_VOTES[channel]["REQUIRED_TO_MUTE"]:
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
					CURRENT_VOTES.pop(channel, None)

	# @commands.has_role("botmancer")
	@commands.command(name="yup", help="mutes the champ")
	async def muteTheChamp(self, ctx):

		if self.SPICE_CHAMP_TO_MUTE == "":
			return

		member = self.SPICE_CHAMP_TO_MUTE
		# clear out the champ to mute and reset their level
		self.SPICE_CHAMP_TO_MUTE = ""
		self.SPICE_CHAMPS[member] = 0

	 	# mute em
		await ctx.send("Timing out " + member.name + " for 10 minutes")
		mutedRole = discord.utils.get(member.guild.roles, name="muted")
		await member.add_roles(mutedRole)
		await member.edit(mute=True)
		await asyncio.sleep(600)

		await ctx.send(member.name + " is very calm now")
		await member.remove_roles(mutedRole)
		await member.edit(mute=False)

def setup(bot):
	bot.add_cog(VotingCog(bot))