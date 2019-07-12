from discord.ext import commands
from .utils import perms
import json

with open("bank.json") as file:
    bank = json.load(file)

class Testing(commands.Cog):
    '''You See Nothing'''
    def __init__(self, bot):
        self.bot = bot

    @perms.owner()
    @commands.command()
    async def add(self, ctx, add: int):
        bank["totals"]["balance"] += add
        with open("bank.json", "w") as file:
            json.dump(bank, file)
        await ctx.send(f'{bank["totals"]["balance"]:,} gems')

    @perms.owner()
    @commands.command()
    async def remove(self, ctx, remove: int):
        bank["totals"]["balance"] -= remove
        with open("bank.json", "w") as file:
            json.dump(bank, file)
        await ctx.send(f'{bank["totals"]["balance"]:,} gems')

    @perms.owner()
    @commands.command()
    async def count(self, ctx):
        await ctx.send(f'{bank["totals"]["balance"]:,} gems')

def setup(bot):
    bot.add_cog(Testing(bot))
