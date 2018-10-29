from cogs.util import pyson
from discord.ext import commands
import discord
import requests
import io


class imgur:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def aa(self, ctx, link: str=None, album_name: str=None):
        #rework album_name to accept multiple words
        if not link or not album_name:
            await ctx.send('Please include a link to the album and a name for the album.')

        possible_links = ['https://imgur.com/gallery/', 'https://imgur.com/a/']
        if not any(x in link for x in possible_links):
            await ctx.send('That doesnt look like a valid link.')

        else:
            self.bot.serverconfig = pyson.Pyson(f'data/servers/{str(ctx.guild.id)}/config.json')
            albums = self.bot.serverconfig.data.get('albums')
            if album_name not in albums:
                await ctx.send(f'woowoo {album_name}')
            else:
                await ctx.send('already exists fool')


def setup(bot):
    bot.add_cog(imgur(bot))
