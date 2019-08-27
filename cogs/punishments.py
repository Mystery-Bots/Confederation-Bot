from discord.ext import commands
from .utils import perms, time
from config import *
import json, datetime, discord, asyncio, typing

with open("punishments.json") as file:
    punishments = json.load(file)

with open("muted.json") as file:
    muted = json.load(file)

class Infractions:
    async def post(user: discord.User, type, submiter ,reason,end, duration = None):
        now = datetime.datetime.now()
        end = end + now
        if duration is None:
            print("idk error")
        else:
            print()
            if str(user.id) in punishments.keys():
                data = {f"{(len(punishments[str(user.id)].keys())+1)}":{"type":type,"date":f"{now}","duration":duration,"reason":reason,"submiter":submiter,"end":f"{end}"}}
                punishments[str(user.id)].update(data)
            else:
                data = {"1":{"type":type,"date":f"{now}","duration":duration,"reason":reason,"submiter":submiter,"end":f"{end}"}}
                punishments.update({f"{user.id}":data})
        with open("punishments.json", "w") as file:
            json.dump(punishments, file)

class MemberID(commands.Converter):
    async def convert(self, ctx, argument):
        try:
            m = await commands.MemberConverter().convert(ctx, argument)
        except commands.BadArgument:
            try:
                return int(argument, base=10)
            except ValueError:
                raise commands.BadArgument("{} is not a valid member or member ID.".format(argument)) from None
        else:
            can_execute = ctx.author.id == ctx.bot.owner_id or \
                          ctx.author == ctx.guild.owner or \
                          ctx.author.top_role > m.top_role

            if not can_execute:
                raise commands.BadArgument('You cannot do this action on this user due to role hierarchy.')
            return m.id

class ActionReason(commands.Converter):
    async def convert(self, ctx, argument):
        ret = '{} (ID: {}): for {}'.format(ctx.author, ctx.author.id, argument)

        if len(ret) > 512:
            reason_max = 512 - len(ret) - len(argument)
            raise commands.BadArgument('reason is too long ({}/{})'.format(len(argument), reason_max))
        return ret


class BannedMember(commands.Converter):
    async def convert(self, ctx, argument):
        ban_list = await ctx.guild.bans()
        try:
            member_id = int(argument, base=10)
            entity = discord.utils.find(lambda u: u.user.id == member_id, ban_list)
        except ValueError:
            entity = discord.utils.find(lambda u: str(u.user) == argument, ban_list)

        if entity is None:
            raise commands.BadArgument("Not a valid previously-banned member.")
        return entity

class Checks:
    def __init__(self):
        self.mute_role_id = 606603089730076685

    def is_muted(self, member):
        return member.id in muted.keys()

    async def apply_mute(self, member, reason):
        if self.mute_role_id:
            await member.add_roles(discord.Object(id=self.mute_role_id), reason=reason)

    def is_fast_join(self, member):
        last_join = None
        joined = member.joined_at or datetime.datetime.utcnow()
        if last_join is None:
            last_join = joined
            return False
        is_fast = (joined - self.last_join).total_seconds() <= 2.0
        self.last_join = joined
        return is_fast



class Punishments(commands.Cog,name="Moderation"):
    '''Moderation Commands'''
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        logs_channel = self.bot.get_channel(507619591933919232)
        if Checks.is_muted(self, member=member):
            return await Checks.apply_mute(member, 'Member was previously muted.')
        now = datetime.datetime.utcnow()
        is_new = member.created_at > (now - datetime.timedelta(days=7))
        # Do the broadcasted message to the channel
        title = 'Member Joined'
        if Checks.is_fast_join(self, member=member):
            colour = 0xdd5f53 # red
            if is_new:
                title = 'Member Joined (Very New Member)'
        else:
            colour = 0x53dda4 # green

            if is_new:
                colour = 0xdda453 # yellow
                title = 'Member Joined (Very New Member)'

        e = discord.Embed(title=title, colour=colour)
        e.timestamp = now
        e.set_author(name=str(member), icon_url=member.avatar_url)
        e.add_field(name='ID', value=member.id)
        e.add_field(name='Joined', value=member.joined_at)
        e.add_field(name='Created', value=time.human_timedelta(member.created_at), inline=False)
        await logs_channel.send(embed=e)

    @commands.command()
    async def warn(self, ctx, user: discord.User, *, reason: ActionReason = None):
        if reason is None:
            reason = f"Warned by {ctx.author.name}#{ctx.author.discriminator} (ID: {ctx.author.id})"
        else:
            reason = f"Warned by {reason}"
        await ctx.send(reason)

    @commands.has_permissions(kick_members=True)
    @commands.command()
    async def kick(self, ctx, user: discord.User, *, reason: ActionReason = None):
        if reason is None:
            reason = f"Kicked by {ctx.author.name}#{ctx.author.discriminator} (ID: {ctx.author.id})"
        else:
            reason = f"Kicked by {reason}"
        await ctx.send(reason)

    @commands.has_permissions(ban_members=True)
    @commands.command()
    async def ban(self, ctx, user: discord.User, *, reason):
        '''Perm'''
        if reason is None:
            reason = f"Banned by {ctx.author.name}#{ctx.author.discriminator} (ID: {ctx.author.id}). Ending in: Perm Ban"
        else:
            reason = f"Banned by {ctx.author.name}#{ctx.author.discriminator} (ID: {ctx.author.id} for {reason}. Ending in: Perm Ban"
        await ctx.send(reason)

    @commands.has_permissions(ban_members=True)
    @commands.command()
    async def tempban(self, ctx, user: discord.User, *, args):
        '''Temporarily bans a member for the specified duration.'''
        duration, reason = await time.duration(ctx, args)
        if reason is None:
            reason = f"Banned by {ctx.author.name}#{ctx.author.discriminator} (ID: {ctx.author.id}). Ending in: {duration}"
        else:
            reason = f"Banned by {ctx.author.name}#{ctx.author.discriminator} (ID: {ctx.author.id} for {reason}. Ending in: {duration}"
        await user.send(reason)
        await ctx.send(reason)
        await ctx.guild.ban(user, reason=reason)
        await Infractions.post(user=user, type="Ban", submiter=ctx.author.name, reason=reason, duration=duration.seconds,end=duration)
        await asyncio.sleep(duration.seconds)
        await ctx.guild.unban(discord.Object(id=user.id), reason=f"Automatic unban from ban made by {ctx.author.name}#{ctx.author.discriminator} (ID: {ctx.author.id})")


    @tempban.error
    async def on_command_error(self, ctx, error):
        await ctx.send(error)

    @commands.command()
    async def mute(self, ctx, user: discord.User, *, args):
        try:
            reason = args.split("-r")[1]
        except IndexError:
            reason = f"Warned by {ctx.author.name}#{ctx.author.discriminator} (ID: {ctx.author.id})"
        duration = args.split("-r")[0]
        print("duration "+ duration)
        duration = time.duration(duration.strip())
        if duration is False:
            await ctx.send("Your time had an error in it please try again")
            return
        await asyncio.sleep(duration)
        await ctx.send(f"{reason} {duration}")

    @commands.command(allies=['hist'])
    async def history(self, ctx, user: discord.User, limit: int = 10):
        embed = discord.Embed()
        embed.set_author(name=str(user), icon_url=user.avatar_url)
        for i in punishments[str(user.id)].keys():
            print(i)
            print(i.keys())
            embed.add_field(name=str(i),value=f"Type: **{str(i['type'])}**\nDuration: {str(i['duration'])}seconds\nReason: {str(i['reason'])}\nModerator: {str(i['submiter'])}")
        await ctx.send(embed=embed)

    @commands.command()
    async def test(self, ctx, *,test):
        duration, reason = await time.duration(test)
        #try:
            #reason = test.split("-r")[1]
        #except IndexError:
            #reason = f"Warned by {ctx.author.name}#{ctx.author.discriminator} (ID: {ctx.author.id})"
        #duration = test.split("-r")[0]
        #duration = await time.duration(duration.strip())
        #await asyncio.sleep(duration)
        await ctx.send(f"{duration}, {reason}")
        #print(time.human_timedelta(duration))
        #Infractions.post(self=self,user=user, type="mute", submiter=ctx.author.name,reason=reason, duration=duration)

def setup(bot):
    bot.add_cog(Punishments(bot))
