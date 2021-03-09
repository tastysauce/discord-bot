import discord
from discord.ext import commands
from discord.ext import tasks

class RandoCog(commands.Cog, name="Rando"):

	def __init__(self, bot):
		self.bot = bot
		print("Initialized Rando")

	@commands.Cog.listener()
	async def on_member_join(self, member):
		randoRole = discord.utils.get(member.guild.roles, name="rando")
		await member.add_roles(randoRole)

def setup(bot):
	bot.add_cog(RandoCog(bot))