import discord
import emoji
from discord.ext import commands

class ModuleControlCog(commands.Cog, name="Module Control"):

    def __init__(self, bot):
        self.bot = bot
        print("Initialized Module Control")

    async def load(self, context, module : str):
        # Loads a module
        try:
            self.bot.load_extension(module)
        except Exception as e:
            await context.send('{}: {}'.format(type(e).__name__, e))
        else:
            await context.send(":thumbsup:")

    async def unload(self, context, module : str):
        # Unloads a module
        try:
            self.bot.unload_extension(module)
        except Exception as e:
            await context.send('{}: {}'.format(type(e).__name__, e))
        else:
            await context.send(":thumbsup:")

    async def reload(self, context, module : str):
        # Reloads a module
        try:
            self.bot.unload_extension(module)
            self.bot.load_extension(module)
        except Exception as e:
            await context.send('{}: {}'.format(type(e).__name__, e))
        else:
            await context.send(":thumbsup:")

    LOAD = "load"
    UNLOAD = "unload"
    RELOAD = "reload"

    functionMap = {
        LOAD: load,
        UNLOAD: unload,
        RELOAD: reload
    }

    @commands.has_role("botmancer")
    @commands.command(name="module")
    async def startBotCommand(self, context, *arguments):
        # Expects array of two arguments
        # first argument is command name
        # second argument is module name
        if not len(arguments) == 2:
            await context.send("Expected two arguments, but got " + str(len(arguments)))
            return

        commandName = arguments[0]
        moduleName = arguments[1]

        function = self.functionMap[commandName]
        await function(self, context, module=moduleName)

def setup(bot):
    bot.add_cog(ModuleControlCog(bot))
