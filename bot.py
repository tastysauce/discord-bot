# bot.py
import os
import random
import discord
import asyncio
import emoji
from discord.ext import commands
from dotenv import load_dotenv
from discord.ext.commands import has_permissions

intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.guilds = True
intents.guild_messages = True

load_dotenv()

# GLOBAL VARIABLES LOL
TOKEN = os.getenv("DISCORD_TOKEN")
BOT_CHANNEL_ID = 762411266860908574
SPICE_DELTA = 0.5
SPICE_TERRIBLE_DELTA = 1.25
SPICE_LEVEL = 0 #initially 0 and incremented when someone trips the array
SPICE_DECREMENT_INTERVAL = 600 # ten minutes in seconds
SPICE_CHAMPS = {}
ARRAY_OF_TERRIBLE_WORDS = ["1080p", "1440p", "1080", "1440", "144hz", "144", "90", "90hz", "clown", ":90hz:", "fake", "blm", "trump", "antifa", "alt f4", "altf4", "f4", "intel", "nvidia", "amd"]
ARRAY_OF_BAD_WORDS = ["anal","anus","arse","ass","ballsack","balls","bastard","bitch","biatch","bloody","blowjob","blow" "job","bollock","bollok","boner","butt","buttplug","clitoris","cock","coon","crap","cunt","damn","dick","dildo","dyke","fag","feck","fellate","fellatio","felching","fuck","fudgepacker","fudge" "packer","flange","Goddamn","hell","homo","jerk","jizz","knobend","knob" "end","muff","nigger","nigga","omg","penis","piss","poop","prick","pube","pussy","queer","scrotum","sex","shit","sh1t","slut","smegma","spunk","tit","tosser","turd","twat","vagina","wank","whore"]

SPICE_CHAMP_TO_MUTE = ""


# Load bot (subclass of Client) and make sure it has the intents that can read members or it can't do shit
bot = commands.Bot(intents=intents, command_prefix="!")


# ---
# Bot commands followed by event listeners
# ---

@bot.command(name="toggleMute", help="toggles mute on the target")
@commands.has_role("botmancer")
async def toggleMute(ctx, target):
	target = target.strip("<!@>")
	member = await commands.MemberConverter().convert(ctx, target)

	# This won't mute admins
	# if member.guild_permissions.administrator:
	# 	 await ctx.send("Not muting an admin")
	# 	 return

	shouldMute = not member.voice.mute

	message = ("Muting " + member.name) if shouldMute else ("Unmuting " + member.name)
	await ctx.send(message)
	await member.edit(mute=shouldMute)

# Standard mute with a timeout
@bot.command(name="mute", help="toggles mute on the target")
@commands.has_role("botmancer")
async def mute(ctx, target, duration: int):
	target = target.strip("<!@>")
	member = await commands.MemberConverter().convert(ctx, target)

	# This won't mute admins
	# if member.guild_permissions.administrator:
	# 	 await ctx.send("Not muting an admin")
	# 	 return

    # Mute first
	await ctx.send("Muting " + member.name + " for " + str(duration) + " seconds")
	await member.edit(mute=True)

	# Unmute after duration
	# not sure what stacking up mutes will do.  probably disasterous
	await asyncio.sleep(duration)
	await member.edit(mute=False)
	await ctx.send(member.name + " is free again. They served " + str(duration) + " seconds")

# @commands.has_role("botmancer")
@bot.command(name="yup", help="mutes the champ")
async def muteTheChamp(ctx):
	global SPICE_CHAMP_TO_MUTE

	if SPICE_CHAMP_TO_MUTE == "":
		return

	member = SPICE_CHAMP_TO_MUTE
	# clear out the champ to mute and reset their level
	SPICE_CHAMP_TO_MUTE = ""
	SPICE_CHAMPS[member] = 0

 	# mute em
	await ctx.send("Timing out " + member.name + " for 10 minutes")
	mutedRole = discord.utils.get(member.guild.roles, name="muted")
	await member.add_roles(mutedRole)
	await member.edit(mute=True)
	await asyncio.sleep(600)

	await ctx.send(member.name + " is very calm now")
	await member.remove_roles(mutedRole)
	await member.edit(mute=False)

# ---
# Event monitoring
# ---

@bot.event
async def on_ready():
	# periodically decrease spice level to 0 every 15 minutes
	task = bot.loop.create_task(periodicallyDecrementSpice(SPICE_DECREMENT_INTERVAL))
	await task

# Spicy meter

def spiceLevelToEmoji(level: int):
	currentLevel = 0
	string = ""

	# return baby level early if level is 0
	if level == 0:
		return emoji.demojize("👶")

	while currentLevel < level:
		string = string + emoji.demojize("🌶")
		currentLevel = currentLevel + 1

	return string

async def periodicallyDecrementSpice(timeout):
	global SPICE_LEVEL
	global SPICE_CHAMPS
	while True:
		await asyncio.sleep(timeout)
		if SPICE_LEVEL > 0:
			await bot.get_channel(BOT_CHANNEL_ID).send("spice level is cooling down: " + spiceLevelToEmoji(SPICE_LEVEL))
			SPICE_LEVEL = SPICE_LEVEL - 1
		if SPICE_LEVEL < 0:
			SPICE_LEVEL = 0
			SPICE_CHAMPS = {}

@bot.event
async def on_message(message):
	global ARRAY_OF_TERRIBLE_WORDS
	global SPICE_LEVEL
	global SPICE_CHAMPS
	global SPICE_CHAMP_TO_MUTE

	# process commands as usual
	await bot.process_commands(message)

	# Don't listen to messages from ourself
	if message.author == bot.user:
		return

	# Only run in the test channel for now
	# if not message.channel.id == BOT_CHANNEL_ID:
	# 	return

	levelToDisplay = 0

	for badWord in ARRAY_OF_BAD_WORDS:
		if badWord in message.content:

			#increment spice level and record name of edgy spice champ
			SPICE_LEVEL = SPICE_LEVEL + SPICE_DELTA

			# maintain a max of 5 peppers
			if SPICE_LEVEL > 5:
				SPICE_LEVEL = 5

			# record the value for the user or add an entry for the rising champ
			if message.author in SPICE_CHAMPS:
				newChampLevel = SPICE_CHAMPS[message.author] + SPICE_DELTA
				SPICE_CHAMPS[message.author] = newChampLevel
				levelToDisplay = round(newChampLevel)
			else:
				SPICE_CHAMPS[message.author] = SPICE_DELTA
				levelToDisplay = SPICE_DELTA
			# only allow 1 change per message
			break

	# but what if it's a terrible word
	for terribleWord in ARRAY_OF_TERRIBLE_WORDS:
		if terribleWord in message.content:

			#increment spice level and record name of edgy spice champ
			SPICE_LEVEL = SPICE_LEVEL + SPICE_TERRIBLE_DELTA

			# maintain a max of 5 peppers
			if SPICE_LEVEL > 5:
				SPICE_LEVEL = 5

			# record the value for the user or add an entry for the rising champ
			if message.author in SPICE_CHAMPS:
				newChampLevel = SPICE_CHAMPS[message.author] + SPICE_TERRIBLE_DELTA
				SPICE_CHAMPS[message.author] = newChampLevel
				levelToDisplay = round(newChampLevel)
			else:
				SPICE_CHAMPS[message.author] = SPICE_TERRIBLE_DELTA
				levelToDisplay = SPICE_TERRIBLE_DELTA
			# only allow 1 change per message
			break

	# round the level so people can't swear once and achieve pepper status
	# show the new level of someone's having a bad day
	if levelToDisplay > 0:
		await message.channel.send(message.author.name + " is HEATING UP: " + spiceLevelToEmoji(levelToDisplay))
		await message.channel.send("channel spice level: " + spiceLevelToEmoji(SPICE_LEVEL))

	if levelToDisplay >= 5:
		await message.channel.send("MUTE THE SPICE CHAMP?? Type !yup to mute " + message.author.name)
		SPICE_CHAMP_TO_MUTE = message.author
	else: 
		SPICE_CHAMP_TO_MUTE = ""

@bot.event
async def on_command_error(ctx, error):
	if isinstance(error, (commands.MissingRole, commands.MissingAnyRole)):
		await ctx.send(error)
	else:
		print(error)


bot.run(TOKEN)





