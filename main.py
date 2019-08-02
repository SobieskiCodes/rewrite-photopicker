import discord
import os
from discord.ext import commands
from pathlib import Path
import aiosqlite
import aiohttp
from cogs.util.errorhandling import NotAuthorized
import jthon


async def get_prefix(bot, message):
    fetch = await bot.db.execute(f'SELECT Prefix FROM GuildConfig WHERE ID={message.guild.id}')
    result = await fetch.fetchone()
    if not result:
        prefix = '.'
    else:
        prefix = result[0]
    return commands.when_mentioned_or(*prefix)(bot, message)


bot = commands.AutoShardedBot(command_prefix=get_prefix)


@bot.event
async def on_guild_join(guild):
    get_guild = await bot.db.execute(f'SELECT ID FROM GuildConfig WHERE ID={guild.id}')
    results = await get_guild.fetchone()
    if not results:
        await bot.db.execute(f"INSERT INTO GuildConfig(ID, Prefix) VALUES (?, ?)", (guild.id, '.'))
        await bot.db.commit()


@bot.event
async def on_guild_remove(guild):
    print(f'left server {guild.name}')
    #remove guild


@bot.event
async def on_ready():
    print(f'\n\nLogged in as: {bot.user.name} - {bot.user.id}')
    await bot.change_presence(status=discord.Status.idle, activity=discord.Game(f"Mention me for prefix"))


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure) or isinstance(error, commands.errors.CommandNotFound):
        return
    if isinstance(error, commands.errors.BadArgument):
        return
    if isinstance(error, NotAuthorized):
        #pretty-fi this
        await ctx.send('You are not authorized for this command.')
        pass
    else:
        print(f'Error in {ctx.guild.id} with message {ctx.message.content}')
        raise error


@bot.check
async def __before_invoke(ctx):
    if not ctx.message.author.bot:
        return True


def load_extensions():
    bot.startup_extensions = []
    path = Path('./cogs')
    for dirpath, dirnames, filenames in os.walk(path):
        if dirpath.strip('./') == str(path):
            for cog in filenames:
                if cog.endswith('.py'):
                    extension = 'cogs.'+cog[:-3]
                    bot.startup_extensions.append(extension)

    if __name__ == "__main__":
        for extension in bot.startup_extensions:
            try:
                bot.load_extension(extension)
                print(f'Loaded {extension}')
            except Exception as e:
                exc = f'{type(e).__name__}: {e}'
                print(f'Failed to load extension {extension}\n{exc}')


async def create_aiohttp():
    bot.aiohttp = aiohttp.ClientSession()


async def create_dbconnect():
    bot.db = await aiosqlite.connect("photopicker.db")


bot.loop.create_task(create_aiohttp())
bot.loop.create_task(create_dbconnect())
bot.config = jthon.load('data')
token = bot.config.get('config').get('token').data
load_extensions()
bot.run(token)
