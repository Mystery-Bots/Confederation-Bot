from discord.ext import commands
from .utils import perms
import logging, discord, datetime

logger = logging.getLogger('BOT CONSOLE')


class Owner(commands.Cog):
    """Mystery's Private Commands"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    @perms.owner()
    async def load(self, ctx, *, cog: str):
        """Loads a cog."""
        try:
            self.bot.load_extension("cogs."+cog)
        except Exception as e:
            await ctx.send('**`ERROR:`** {} - {}'.format(type(e).__name__,e))
        else:
            await ctx.send('**`SUCCESS`**')

    @commands.command(hidden=True)
    @perms.owner()
    async def unload(self, ctx, *, cog: str):
        """Unloads a cog."""
        try:
            self.bot.unload_extension("cogs."+cog)
        except Exception as e:
            await ctx.send('**`ERROR:`** {} - {}'.format(type(e).__name__,e))
        else:
            await ctx.send('**`SUCCESS`**')

    @commands.command(hidden=True)
    @perms.owner()
    async def reload(self, ctx, *, cog: str):
        """Reloads a cog."""
        try:
            self.bot.reload_extension("cogs."+cog)
        except Exception as e:
            await ctx.send('**`ERROR:`** {} - {}'.format(type(e).__name__,e))
        else:
            await ctx.send('**`SUCCESS`**')

    @commands.command(aliases=["cogs"], hidden=True)
    @perms.owner()
    async def coglist(self, ctx):
        """List of loaded cogs"""
        cogs = []
        for i in self.bot.cogs.keys():
            cogs.append(i)
        if len(cogs) == 1:
            await ctx.send("Loaded Cog\n"+"".join(cogs))
        else:
            await ctx.send("Loaded Cogs\n"+", ".join(cogs))

    @perms.owner()
    @commands.command(hidden=True)
    async def shutdown(self, ctx):
        """Shuts down the bot"""
        logger.info("Shutdown command run")
        print("Shutdown command run")
        start = self.bot.uptime
        embed = discord.Embed(title="Bot Uptime", description=str(datetime.datetime.now()-start),color=discord.Color.red())
        embed.add_field(name="Key", value="Hours:Minutes:Seconds.Microsecond")
        await ctx.send(embed=embed)
        await self.bot.close()

def setup(bot):
    bot.add_cog(Owner(bot))
