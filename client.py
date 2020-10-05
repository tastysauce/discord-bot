# bot.py
import os

import discord
intents = discord.Intents.default()
intents.members = True
intents.messages = True

from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == GUILD:
            break

    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})\n'
    )

    members = '\n - '.join([member.name for member in guild.members])
    print(f'Guild Members:\n - {members}')

    # channel = '\n - '.join([channel.name for channel in guild.channels])
    # print(f'Guild channels:\n - {channel}')

    # emojis = '\n - '.join([emoji.name for emoji in guild.emojis])
    # print(f'Guild emojis:\n - {emojis}')

@client.event
async def on_message(message):
	if message.author == client.user:
		return

	if message.content == "test":
		await message.channel.send("sup")

client.run(TOKEN)