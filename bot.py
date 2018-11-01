import discord
import os
from discord.ext import commands
from pathlib import Path
from cogs.util import pyson
from cogs.imgur import NotAuthorized


def get_prefix(bot, message):
    bot.serverconfig = pyson.Pyson(f'data/servers/{str(message.guild.id)}/config.json')
    prefix = bot.serverconfig.data.get('config').get('prefix')
    if not prefix:
        prefix = '!'
    return commands.when_mentioned_or(*prefix)(bot, message)


bot = commands.AutoShardedBot(command_prefix=get_prefix, formatter=None)


@bot.event
async def on_guild_join(guild):
    if not os.path.exists(f"./data/servers/{str(guild.id)}/config.json"):
        try:
            os.makedirs(f"./data/servers/{str(guild.id)}/")
            open(f'./data/servers/{str(guild.id)}/config.json', 'a').close()
        except OSError as e:
            if e.errno != e.errno.EEXIST:
                raise
    bot.serverconfig = pyson.Pyson(f'data/servers/{str(guild.id)}/config.json')
    bot.serverconfig.data = {"albums": {}, "config": {"admins": [], "prefix": "."}}
    bot.serverconfig.save()


@bot.event
async def on_guild_remove(guild):
    print(f'left server {guild.name}')


@bot.event
async def on_ready():
    print(f'\n\nLogged in as: {bot.user.name} - {bot.user.id}')
    await bot.change_presence(status=discord.Status.idle, activity=discord.Game(f"Mention me for prefix"))


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure) or isinstance(error, commands.errors.CommandNotFound):
        return
    if isinstance(error, commands.errors.BadArgument):
        #still have to handle this for adding admins....
        pass
    if isinstance(error, NotAuthorized):
        await ctx.send('you are not authorized for this command.')
        pass
    else:
        raise error

@bot.check
async def __before_invoke(ctx):
    if not ctx.message.author.bot:
        return True


@bot.event
async def on_message(message):
    if any(mention.name == bot.user.name for mention in message.mentions):
        if len(message.mentions) == 1:
            if message.content == f'<@{message.raw_mentions[0]}>':
                bot.serverconfig = pyson.Pyson(f'data/servers/{str(message.guild.id)}/config.json')
                prefix = bot.serverconfig.data.get('config').get('prefix')
                await message.channel.send(f'my prefix is {prefix}')
    await bot.process_commands(message)


def load_extensions():
    bot.startup_extensions = []
    path = Path('./cogs')
    for dirpath, dirnames, filenames in os.walk(path):
        if dirpath.strip('./') == str(path):
            for cog in filenames:
                extension = 'cogs.'+cog[:-3]
                bot.startup_extensions.append(extension)

    if __name__ == "__main__":
        for extension in bot.startup_extensions:
            try:
                bot.load_extension(extension)
                print('Loaded {}'.format(extension))
            except Exception as e:
                exc = '{}: {}'.format(type(e).__name__, e)
                print('Failed to load extension {}\n{}'.format(extension, exc))


bot.config = pyson.Pyson('data/config/startup.json')
token = bot.config.data.get('config').get('discord_token')
load_extensions()
bot.run(token, bot=True, reconnect=True)
