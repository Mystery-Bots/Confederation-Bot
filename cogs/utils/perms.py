from discord.ext import commands

bot_owners = [295798251020484608, 210221099173019650]
owner_role = 506655968554254358
captain_role = 506656534487367700
staff_role = 615666549222539336

#Bot Owner
def is_owner_check(ctx):
    return ctx.message.author.id in bot_owners

def owner_id_check(_id):
    return _id in bot_owners

def owner():
    return commands.check(is_owner_check)

