import discord
import os
from discord.ext import commands
from pathlib import Path
import aiosqlite
import aiohttp
from cogs.util.errors import NotAuthorized
import jthon


async def get_prefix(bot, message):
    prefix = '.'
    if message.guild:
        fetch = await bot.db.execute(f'SELECT Prefix FROM GuildConfig WHERE ID={message.guild.id}')
        result = await fetch.fetchone()
        if result:
            prefix = result[0]
        if not result:
            await bot.db.execute(f"INSERT INTO GuildConfig(ID, Prefix) VALUES (?, ?)", (message.guild.id, prefix))
            await bot.db.commit()
    return commands.when_mentioned_or(*prefix)(bot, message)

# Configure intents
intents = discord.Intents.none()
intents.guilds = True
intents.members = False
intents.voice_states = False
intents.messages = True
intents.reactions = True
bot = commands.AutoShardedBot(command_prefix=get_prefix, dm_help=False, intents=intents)


@bot.event
async def on_guild_join(guild):
    get_guild = await bot.db.execute(f'SELECT ID FROM GuildConfig WHERE ID=?', (guild.id,))
    results = await get_guild.fetchone()
    if not results:
        await bot.db.execute(f"INSERT INTO GuildConfig(ID, Prefix) VALUES (?, ?)", (guild.id, '.'))
        await bot.db.commit()


@bot.event
async def on_guild_remove(guild):
    print(f'left server {guild.name}')



@bot.event
async def on_ready():
    print(f'\n\nLogged in as: {bot.user.name} - {bot.user.id}')
    await bot.change_presence(status=discord.Status.idle, activity=discord.Game(f"Feeding the hamsters"))


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure) or isinstance(error, commands.errors.CommandNotFound):
        return
    if isinstance(error, commands.errors.BadArgument):
        return
    if isinstance(error, NotAuthorized):
        await ctx.send('You are not authorized for this command.')
        pass
    else:
        if ctx.guild:
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
    if not os.path.exists("./photopicker.db"):
        with open('photopicker.db', 'a') as fp:
            pass
        bot.db = await aiosqlite.connect("photopicker.db")
        await bot.db.execute("""CREATE TABLE "Albums" (
                                "ID"	INTEGER,
                                "GuildID"	INTEGER NOT NULL,
                                "AlbumName"	TEXT NOT NULL UNIQUE,
                                "AlbumLink"	TEXT NOT NULL,
                                PRIMARY KEY("ID" AUTOINCREMENT)
                            )""")
        await bot.db.execute("""CREATE TABLE "GuildConfig" (
                                "ID"	INTEGER,
                                "Prefix"	TEXT,
                                "Content"	TEXT,
                                "Title"	TEXT,
                                PRIMARY KEY("ID")
                            )""")
        await bot.db.execute("""CREATE TABLE "Permissions" (
                                "ID"	INTEGER,
                                "MemberID"	INTEGER NOT NULL,
                                "GuildID"	INTEGER NOT NULL,
                                PRIMARY KEY("ID" AUTOINCREMENT)
                            )""")
        await bot.db.commit()
    else:
        bot.db = await aiosqlite.connect("photopicker.db")


class Fetch:
    def __init__(self, bot):
        self.bot = bot

    async def all(self, *arg):
        get = await self.bot.db.execute(*arg)
        results = await get.fetchall()
        return results

    async def one(self, *arg):
        get = await self.bot.db.execute(*arg)
        results = await get.fetchone()
        return results


bot.config = jthon.load('data')['config']
bot.fetch = Fetch(bot)
bot.loop.create_task(create_dbconnect())
bot.loop.create_task(create_aiohttp())
load_extensions()
bot.run(bot.config.get('token'))
