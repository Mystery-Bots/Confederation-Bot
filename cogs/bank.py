from discord.ext import commands
from .utils import perms
from config import *
import json, datetime, discord

with open("bank.json") as file:
    bank = json.load(file)

class Bank(commands.Cog):
    '''Bank Commands'''
    def __init__(self, bot):
        self.bot = bot


    @commands.group(invoke_without_command=True)
    async def bank(self, ctx):
        '''Bank help command'''
        message = ("__**Bank Commands**__\n"
                   "__*Captain+ Commands*__\n"
                   "**;bank update**"
                   "**;bank reset**\n"
                   "__*Officer+ Commands*__"
                   "**;bank add (Donor) (Amount)**\n"
                   "**;bank use (IGN) (Amount) (Reason)**\n"
                    "__*Everyone*__\n"
                    "**;bank donate (IGN) (Amount)**")

    @perms.captain()
    @bank.command()
    async def update(self, ctx):
        '''Updates the bank gem count'''
        bank_channel = self.bot.get_channel(BANK_CHANNEL)
        await bank_channel.send(f'**Gems update**\nGem count as of {datetime.datetime.utcnow().strftime("%B %d %Y - %I:%M%p")}: {bank["totals"]["balance"]:,} gems')

    @perms.captain()
    @bank.command(enabled=False)
    async def reset(self, ctx):
        '''Reset the bank'''
        message = ("@everyone\n"
"The server has reset, which means all clan gems have been reset, as they are not saved. We will try to get more gems in the bank as soon as possible. Please be patient as we have to have time to rank up to be able to get a lot of gems in the clan bank so we can loan it out to you guys. Thanks for your patience.\n"
"*~Confederation of United Clashers Team*")
        bank_channel = self.bot.get_channel(BANK_CHANNEL)
        announcement_channel = self.bot.get_channel(ANNOUNCEMENT_CHANNEL)
        bank["totals"]["balance"] = 0
        bank["totals"]["loans"] = 0
        bank["totals"]["deposits"] = 0
        with open("bank.json", "w") as file:
            json.dump(bank, file)
        await ctx.send("Bank has been reset.")
        await bank_channel.send("**Gem updated** Server has been reset: 0 gems")
        await announcement_channel.send(message)

    @perms.staff()
    @bank.command()
    async def add(self, ctx, user: discord.User, amount: int):
        '''Adds gems to the bank'''
        bank_channel = self.bot.get_channel(BANK_CHANNEL)
        await bank_channel.send(f"**+{amount:,} gems** donation from {user.mention}")
        await ctx.send(f"Donation of {amount:,} gems added")
        bank["totals"]["balance"] += amount
        with open("bank.json", "w") as file:
            json.dump(bank, file)

    @perms.staff()
    @bank.command()
    async def use(self, ctx, ign: str, amount: int, *,reason: str):
        '''Removes gems from the bank'''
        bank_channel = self.bot.get_channel(BANK_CHANNEL)
        await bank_channel.send(f"**-{amount:,} gems** used by `{ign}` for reason: {reason}")
        await ctx.send(f"{amount:,} gems used by `{ign}` for {reason}")
        bank["totals"]["balance"] -= amount
        with open("bank.json", "w") as file:
            json.dump(bank, file)

    @bank.command()
    async def donation(self, ctx, ign: str, amount: int):
        '''Request to give a donation to the clan'''
        todo_channel = self.bot.get_channel(TODO_CHANNEL)
        await todo_channel.send(f"@everyone user {ctx.author.mention} has offered to donate {amount:,} gems to the clan. Their ign is `{ign}`")
        await ctx.send(f"Your donation offer of {amount:,} gems has been sent")

def setup(bot):
    bot.add_cog(Bank(bot))
