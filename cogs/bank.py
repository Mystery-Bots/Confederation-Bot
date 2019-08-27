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
                   "**;bank update**\n"
                   "**;bank reset**\n"
                   "**;bank withdraw** (User) (Amount)\n"
                   "__*Officer+ Commands*__\n"
                   "**;bank add** (Donor) (Amount)\n"
                   "**;bank use** (IGN) (Amount) (Reason)\n"
                   "__*Everyone*__\n"
                   "**;bank donate** (IGN) (Amount)\n")
        await ctx.send(message)

    @commands.has_any_role(perms.captain_role, perms.owner_role)
    @bank.command()
    async def update(self, ctx):
        '''Updates the bank gem count'''
        bank_channel = self.bot.get_channel(BANK_CHANNEL)
        await bank_channel.send(f'**Gems update**\nGem count as of {datetime.datetime.utcnow().strftime("%B %d %Y - %I:%M%p")}: {bank["totals"]["balance"]:,} gems')

    @commands.has_any_role(perms.captain_role, perms.owner_role)
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

    @commands.has_role(perms.staff_role)
    @bank.command()
    async def add(self, ctx, user: discord.User, amount: int):
        '''Adds gems to the bank'''
        bank_channel = self.bot.get_channel(BANK_CHANNEL)
        await bank_channel.send(f"**+{amount:,} gems** donation from {user.mention}")
        await ctx.send(f"Donation of {amount:,} gems added")
        bank["totals"]["balance"] += amount
        with open("bank.json", "w") as file:
            json.dump(bank, file)

    @commands.has_role(perms.staff_role)
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

    @commands.group(invoke_without_command=True)
    async def deposit(self, ctx):
        message = ("__**Deposit Commands**__\n"
                   "__*Officer+ Comamnds*__\n"
                   "**;deposit confirm** (User) (Amount)\n"
                   "__*Everyone Commands*__\n"
                   "**;deposit request** (IGN) (Amount)")
        await ctx.send(message)

    @deposit.command()
    async def request(self, ctx, ign: str, amount: int):
        '''Request to deposit gems'''
        todo_channel = self.bot.get_channel(TODO_CHANNEL)
        await todo_channel.send(f"@everyone user {ctx.author.mention} would like to deposit {amount:,} gems to the clan for safe keepings. Their ign is `{ign}`")
        await ctx.send(f"Your deposit request of {amount:,} gems has been sent")

    @commands.has_role(perms.staff_role)
    @deposit.command()
    async def confirm(self, ctx, user: discord.User, amount: int):
        bank_channel = self.bot.get_channel(BANK_CHANNEL)
        if user.name in bank["deposits"].keys():
            bank["deposits"].update({user.name:bank["deposits"][user.name]+amount})
        else:
            bank["deposits"].update({user.name:amount})
        bank["totals"]["deposits"] += amount
        await bank_channel.send(f'**+{amount} gems** deposit from {user.mention} *(Will be paid back)*')
        await ctx.send(f'Deposit of {amount} gems added for {user.name}')
        with open("bank.json", "w") as file:
            json.dump(bank, file)

    @commands.group(invoke_without_command=True)
    async def withdraw(self, ctx):
        message = ("__**Deposit Commands**__\n"
                   "__*Captain+ Commands**__\n"
                   "**;withdraw confirm** (User) (Amount)\n"
                   "__*Everyone Commands*__\n"
                   "**;withdraw request** (IGN) (Amount)")
        await ctx.send(message)

    @commands.has_any_role(perms.captain_role, perms.owner_role)
    @withdraw.command()
    async def confirm(self, ctx, user: discord.User, amount: int):
        bank_channel = self.bot.get_channel(BANK_CHANNEL)
        if user.name in bank["deposits"].keys():
            bank["deposits"].update({user.name:bank["deposits"][user.name]-amount})
        else:
            await ctx.send(f"User {user.mention} doesn't have a deposit")
            return
        bank["totals"]["deposits"] += amount
        await bank_channel.send(f'**-{amount} gems** withdrawn from {user.mention} *(Will be paid back)*')
        await ctx.send(f'Deposit of {bank["deposits"][user.name]} gems withdrawn for {user.name}')
        with open("bank.json", "w") as file:
            json.dump(bank, file)

    @withdraw.command()
    async def request(self, ctx, ign: str, amount: int):
        '''Request to withdraw gems'''
        todo_channel = self.bot.get_channel(TODO_CHANNEL)
        await todo_channel.send(f"@everyone user {ctx.author.mention} would like to withdraw {amount:,} gems from the clan. Their ign is `{ign}`")
        await ctx.send(f"Your withdraw request of {amount:,} gems has been sent")

def setup(bot):
    bot.add_cog(Bank(bot))
