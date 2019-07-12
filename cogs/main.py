from discord.ext import commands
import datetime, discord

class Main(commands.Cog,name="General"):
    '''General Commands'''
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        '''Checks bot latency'''
        await ctx.send(f"Bot ping is {round(self.bot.latency * 1000)}ms")

    @commands.command()
    async def uptime(self, ctx):
        '''Gets bot uptime'''
        start = self.bot.uptime
        embed = discord.Embed(title="Bot Uptime", description=str(datetime.datetime.now()-start),color=discord.Color.red())
        embed.add_field(name="Key", value="Hours:Minutes:Seconds.Microsecond")
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Main(bot))
