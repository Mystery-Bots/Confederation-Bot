from discord.ext import commands

owners = [295798251020484608]
captains = [295798251020484608, 499720078770831360]
staffs = [295798251020484608, 499720078770831360]

#Bot Owner
def is_owner_check(ctx):
    return ctx.message.author.id in owners

def owner_id_check(_id):
    return _id in owners

def owner():
    return commands.check(is_owner_check)

#Server Staff

def is_captain_check(ctx):
    return ctx.message.author.id in captains

def captain_id_check(_id):
    return _id in captains

def captain():
    return commands.check(is_captain_check)

def is_staff_check(ctx):
    return ctx.message.author.id in staffs

def staff_id_check(_id):
    return _id in staffs

def staff():
    return commands.check(is_staff_check)
