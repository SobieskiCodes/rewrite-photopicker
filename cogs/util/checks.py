from discord.ext import commands
from cogs.util.errors import NotAdded, NotAuthorized

def is_added():
    async def pred(ctx):
        get_user = await ctx.bot.fetch.one(f'SELECT * FROM main WHERE user_id=?', (ctx.author.id, ))
        if not get_user:
            raise NotAdded
        if get_user and ctx.guild is not None:
            return True
        else:
            return False
    return commands.check(pred)


def is_guild_owner():
    def pred(ctx):
        return ctx.guild is not None and ctx.guild.owner_id == ctx.author.id
    return commands.check(pred)


def is_admin():
    """Checks if the message author is the owner or has admin perms"""
    async def predicate(ctx):
        if ctx.guild is None:
            return False

        if ctx.author.id == ctx.guild.owner_id or ctx.author.guild_permissions.manage_guild:
            return True

        get_user = await ctx.bot.fetch.one(f'SELECT * FROM Permissions WHERE MemberID=? AND GuildID=?',
                                           (ctx.author.id, ctx.guild.id))
        if get_user:
            return True
        else:
            raise NotAuthorized
    return commands.check(predicate)