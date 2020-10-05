import discord
import asyncio
import emoji
import csv
from discord.ext import commands

class ShittyCommands(commands.Cog, name="Shitty Commands"):

	def __init__(self, bot):
		self.bot = bot

	@commands.command(name="shittyMute", help="mutes the champs")
	async def muteTarget(self, ctx, champ, duration):
		await ctx.send("Timing out " + champ.name + " for 5 minutes")
		mutedRole = discord.utils.get(champ.guild.roles, name="muted")
		await champ.add_roles(mutedRole)
		await asyncio.sleep(duration)

		await ctx.send(champ.name + " is very calm now")
		await champ.remove_roles(mutedRole)

		self.spiceChamps.pop(champ, None)
		self.champsToMute.remove(champ)
		self.champsThatHaveBeenWarned.remove(champ)

def setup(bot):
	bot.add_cog(ShittyCommands(bot))