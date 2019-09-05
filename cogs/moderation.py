from discord.ext import commands
import discord
from .utils import time
from config import *
import logging
import json
import datetime
import asyncio

with open("punishments.json") as file:
    punishments = json.load(file)

with open("events.json") as file:
    events = json.load(file)

class Reason(commands.Converter):
    async def convert(self, ctx, argument):
        ret = f'{ctx.author} (ID: {ctx.author.id}): {argument}'
        if len(ret) > 512:
            reason_max = 512 - len(ret) - len(argument)
            raise commands.BadArgument(f'reason is too long ({len(argument)}/{reason_max})')
        return ret

class Logs:
    async def warn(self, user, reason):
        if str(user.id) in punishments:
            post = {str(len(punishments[str(user.id)].keys())+1):{
                "Name":user.name,
                "Type":"warn",
                "Date":str(datetime.datetime.utcnow()),
                "Reason":reason
                }
            }
            punishments[str(user.id)].update(post)
        else:
            post = {user.id:{"1":{
            "Name":user.name,
            "Type":"warn",
            "Date":str(datetime.datetime.utcnow()),
            "Reason":reason
                    }
                }
            }
            punishments.update(post)
        with open("punishments.json", "w") as file:
            json.dump(punishments, file)

    async def kick(self, user, reason):
        if str(user.id) in punishments:
            post = {str(len(punishments[str(user.id)].keys())+1):{
                "Name":user.name,
                "Type":"kick",
                "Date":str(datetime.datetime.utcnow()),
                "Reason":reason
                }
            }
            punishments[str(user.id)].update(post)
        else:
            post = {user.id:{"1":{
            "Name":user.name,
            "Type":"kick",
            "Date":str(datetime.datetime.utcnow()),
            "Reason":reason
                    }
                }
            }
            punishments.update(post)
        with open("punishments.json", "w") as file:
            json.dump(punishments, file)

    async def mute(self, user, duration, reason):
        #Main log file system
        if str(user.id) in punishments:
            post = {str(len(punishments[str(user.id)].keys())+1):{
                "Name":user.name,
                "Type":"mute",
                "Date":str(datetime.datetime.utcnow()),
                "Duration":str(duration),
                "Reason":reason
                }
            }
            punishments[str(user.id)].update(post)
        else:
            post = {user.id:{"1":{
            "Name":user.name,
            "Type":"mute",
            "Date":str(datetime.datetime.utcnow()),
            "Duration":str(duration),
            "Reason":reason
                    }
                }
            }
            punishments.update(post)
        with open("punishments.json", "w") as file:
            json.dump(punishments, file)
        #Timed events log system
        # Used for working out if a timed event has ended (tempmute or tempban)
        event = {user.id:{
            "Start":str(datetime.datetime.now()),
            "Duration":str(duration.total_seconds())
        }}
        events.update(event)
        with open("events.json", "w") as file:
            json.dump(events, file)

class Moderation(commands.Cog):
    '''Moderation Commands'''
    def __init__(self, bot):
        self.bot = bot
        self.last_join = None


    def is_new(self, member):
        now = datetime.datetime.utcnow()
        seven_days_ago = now - datetime.timedelta(days=7)
        ninety_days_ago = now - datetime.timedelta(days=90)
        return member.created_at > ninety_days_ago and member.joined_at > seven_days_ago

    def is_fast_join(self, member):
        joined = member.joined_at or datetime.datetime.utcnow()
        if self.last_join is None:
            self.last_join = joined
            return False
        is_fast = (joined - self.last_join).total_seconds() <= 2.0
        self.last_join = joined
        return is_fast

    def is_muted(self, member):
#       if user.id in json punishments file
        pass

    @commands.Cog.listener()
    async def on_member_join(self, member):
        log_channel = self.bot.get_channel(LOG_CHANNEL)
        #if self.is_muted(member):
            #return await mute.apply_mute(self, member, 'Member was previously muted.')


        now = datetime.datetime.utcnow()

        is_new = member.created_at > (now - datetime.timedelta(days=7))

        # Do the broadcasted message to the channel
        title = 'Member Joined'
        if self.is_fast_join(member):
            colour = discord.Color.red() # red
            if is_new:
                title = 'Member Joined (Very New Member)'
        else:
            colour = discord.Color.green() # green

            if is_new:
                colour = discord.Color.gold() # yellow
                title = 'Member Joined (Very New Member)'

        if member.id in punishments[member.id]:
           history = "User has a history of punishments"
        else:
           history = "User has no history of punishments"

        e = discord.Embed(title=title, colour=colour)
        e.timestamp = now
        e.set_author(name=str(member), icon_url=member.avatar_url)
        e.add_field(name='ID', value=member.id)
        e.add_field(name='Mention', value=member.mention)
        e.add_field(name='Joined', value=member.joined_at)
        e.add_field(name='Created', value=time.human_timedelta(member.created_at), inline=False)
        e.add_field(name="History", value=history)
        await log_channel.send(embed=e)

    @commands.command()
    async def test(self, ctx, user: discord.User, *, args):
        mute_role = ctx.guild.get_role(606603089730076685)
        member = ctx.guild.get_member(user.id)
        print(args)
        duration, reason = await time.duration(ctx, args)
        if reason is '' or None:
            reason = f'Action done by {ctx.author} (ID: {ctx.author.id})'
        await Logs.mute(self, user, duration, reason)
        #await member.add_roles(mute_role,reason=reason)
        await ctx.send(f"User {user.mention} has been muted for {duration}")
        await asyncio.sleep(duration.total_seconds())
        #await member.remove_roles(mute_role, reason=f'Auto mute removal system. User muted by {ctx.author} (ID: {ctx.author.id})')
        print(events)
        del events[user.id]



def setup(bot):
    bot.add_cog(Moderation(bot))
