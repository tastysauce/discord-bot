import discord
import os
from discord.ext import commands
from dotenv import load_dotenv

import sys, traceback

load_dotenv()

extensions = [
	"cogs.spice",
	"cogs.voting",
	"cogs.shittyCommands",
	"cogs.moduleControl",
	"cogs.stats",
	"cogs.sentiment"
]

intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.guilds = True
intents.guild_messages = True
bot = commands.Bot(intents=intents, command_prefix="!")

if __name__ == "__main__":
	for extension in extensions:
		try: 
			bot.load_extension(extension)
		except Exception as e:
			print(f"Failed to load extension {extension}.", file=sys.stderr)
			traceback.print_exc()

@bot.event
async def on_ready():
	print(f"Logged in as: {bot.user.name} - {bot.user.id} - {bot.user.name}\nVersion: {discord.__version__}\n")

	
bot.run(os.getenv("DISCORD_TOKEN"), bot=True, reconnect=True)