import traceback, sys, discord, logging, datetime, asyncio, aiohttp
from discord.ext import commands
from cogs.utils import perms
from config import *

#initial_extensions = ("lottery", "main", "owner", "loan", "bank")
initial_extensions = ("moderation", "owner")

#LOGGING
logger = logging.getLogger('BOT CONSOLE')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename=f'logs/{datetime.datetime.now().strftime("%d.%m.%Y")}.log', encoding='utf-8', mode='a')
handler.setFormatter(logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s',datefmt='%d/%m/%Y %I:%M:%S%p'))
logger.addHandler(handler)

#Start up system

bot = commands.Bot(command_prefix=PREFIX, description="Bot for the Confederation of United Clashers")


@bot.event
async def on_ready():
    if SPECIAL_MESSAGE is "":
        await bot.change_presence(status=discord.Status.dnd,activity=discord.Game(name="Confederation Bot | ;help"))
    else:
        await bot.change_presence(status=discord.Status.dnd, activity=discord.Game(name=f"{SPECIAL_MESSAGE} | ;help"))
    bot.uptime = datetime.datetime.now()
    logger.info(f'Ready: {bot.user} (ID: {bot.user.id}) (Time:{datetime.datetime.now().strftime("%d/%m/%Y, %I:%M:%S%p").lower()})')
    print(f'Ready: {bot.user} (ID: {bot.user.id}) (Time:{datetime.datetime.now().strftime("%d/%m/%Y, %I:%M:%S%p").lower()})')

@bot.event
async def on_resumed():
    bot.uptime = datetime.datetime.now()
    logger.info(f'Resumed... {datetime.datetime.now().strftime("%d/%m/%Y, %I:%M:%S%p").lower()}')
    print(f'Resumed... {datetime.datetime.now().strftime("%d/%m/%Y, %I:%M:%S%p").lower()}')

@bot.event
async def on_disconnect():
    logger.info(f"Bot stopped. Uptime: {datetime.datetime.now()-bot.uptime}")
    print(f"Bot stopped. Uptime: {datetime.datetime.now()-bot.uptime}")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Missing required argument")
    elif isinstance(error, commands.MissingRole):
        await ctx.send(f"You are missing the role that is needed to run this command")
    elif isinstance(error, commands.NoPrivateMessage):
        await ctx.author.send('This command cannot be used in private messages.')
    elif isinstance(error, commands.DisabledCommand):
        await ctx.send('Sorry. This command is disabled and cannot be used.')
    elif isinstance(error, commands.CommandInvokeError):
        original = error.original
        if not isinstance(original, discord.HTTPException):
            print(f'In {ctx.command.qualified_name}:', file=sys.stderr)
            traceback.print_tb(original.__traceback__)
            print(f'{original.__class__.__name__}: {original}', file=sys.stderr)
    elif isinstance(error, commands.ArgumentParsingError):
        await ctx.send(error)

@bot.event
async def on_message(message):
    channel = message.channel
    if message.content.startswith(';') and message.author.id is not bot.user.id:
        guild = bot.get_guild(506650935788044290)
        role = guild.get_role(615666549222539336)
        if role not in message.author.roles:
            await channel.send("I am not released yet. Please wait till I am released to try use me.", delete_after=5)
        else:
            await bot.process_commands(message)

if __name__ == '__main__':
        for extension in initial_extensions:
            try:
                bot.load_extension("cogs."+ extension)
            except Exception as e:
                print(f'Failed to load extension {extension}.', file=sys.stderr)
                logger.warning(f'Failed to load extension {extension}.', file=sys.stderr)
                traceback.print_exc()

try:
    bot.run(TOKEN, reconnect=True)
except aiohttp.client_exceptions.ClientConnectorError:
    print("Could not connect to discord")
