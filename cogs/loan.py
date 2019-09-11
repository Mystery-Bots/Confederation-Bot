from discord.ext import commands
from config import *
from .utils import perms
import discord, json, asyncio

with open("bank.json") as file:
    bank = json.load(file)


class Loan(commands.Cog):
    '''Loan Commands'''
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    async def loan(self,ctx):
        '''Loan help command'''
        message = ("__**Loan Commands**__\n"
                   "__*Captain+ Commands*__\n"
                   "**;loan accept** (Discord) (Amount Loaned) (Amount Owed)\n"
                   "**;loan deny** (Discord) (Amount Loaned) (Reason)\n"
                   "__*Oficer Commands*__\n"
                   "**;loan payback** (Discord) (Amount Paidback)\n"
                   "**;loan update**\n"
                   "__*Everyone*__\n"
                   "**;loan request** (IGN) (Amount Loaned) (Amount Owed)")
        await ctx.send(message)

    @commands.has_any_role(perms.captain_role, perms.owner_role)
    @loan.command()
    async def accept(self,ctx, user: discord.User, loaned: int, payback: int):
        '''Accept a loan'''
        if (loaned) >= ((bank["totals"]["balance"]-bank["totals"]["deposits"])// 25):
            await ctx.send(f"The loan of {loaned:,} gems is too big and will take us under our 25% reserve. Please decline this loan")
        else:
            todo_channel = self.bot.get_channel(TODO_CHANNEL)
            bank_channel = self.bot.get_channel(BANK_CHANNEL)
            await todo_channel.send(f"{ctx.author.mention} **, collect {payback:,} gems from {user.mention}.** They borrowed {loaned:,} gems from the Confederate Bank.")
            await bank_channel.send(f"**-{loaned:,} gems** Loaned to {user.mention}. Will pay back {payback:,} gems.")
            bank["totals"]["balance"] -= loaned
            bank["totals"]["loans"] += payback
            with open("bank.json", "w") as file:
                json.dump(bank, file)
            await ctx.send(f"You have given {user.mention} a loan of {loaned:,} gems. They will pay back with {payback:,} gems.")

    @commands.has_any_role(perms.captain_role, perms.owner_role)
    @loan.command()
    async def deny(self, ctx, user: discord.User, amount: int, *, reason):
        '''Decline a loan'''
        await ctx.send(f"{user} has been denied of their {amount:,} gems loan.")
        await user.send(f"You loan of {amount:,} gems has been denied. Reason: {reason}")


    @commands.has_role(perms.staff_role)
    @loan.command()
    async def payback(self, ctx, user: discord.User, paidback: int):
        '''Confirm a users loan repayment'''
        bank_channel = self.bot.get_channel(BANK_CHANNEL)
        bank["totals"]["balance"] += paidback
        await bank_channel.send(f"**+{paidback:,} gems** Loan payment from {user.mention}")
        with open("bank.json", "w") as file:
            json.dump(bank, file)
        await ctx.send(f"Loan payment from {user.mention} of {paidback:,} gems. Processed")

    @loan.command()
    async def request(self, ctx, ign: str, amount: int, payback: int):
        '''Request a loan from the clan'''
        loan_channel = self.bot.get_channel(LOAN_CHANNEL)
        await loan_channel.send(f"@everyone, discord user {ctx.author.mention} has requested a {amount:,} gem loan. They have offered to pay back {payback:,} gems, and their IGN is `{ign}`. Do !loan {ctx.author.mention} {amount} {payback} to accept their loan, or if their loan is denied, do !loan deny {ctx.author.mention} {amount} reason")
        await ctx.send(f"Your loan request for {amount:,} gems has been sent. You have offered to pay back the loan with {payback:,} gems. ")

    @commands.has_role(perms.staff_role)
    @loan.command()
    async def update(self, ctx):
        '''Gets an update on number of gems loaned to users'''
        loan_amount = bank["totals"]["loans"]
        await ctx.send(f"Total amount of gems waiting to be paid back from loans is {loan_amount:,} gems")

def setup(bot):
    bot.add_cog(Loan(bot))
