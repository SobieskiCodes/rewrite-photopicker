from cogs.util import pyson
from discord.ext import commands
from imgurpython import ImgurClient
import random
import discord
import requests
import io


class imgur:
    def __init__(self, bot):
        self.bot = bot
        self.clientID = bot.config.data.get('config').get('imgur_client_id')
        self.secretID = bot.config.data.get('config').get('imgur_client_secret')
        self.imgur_client = ImgurClient(self.clientID, self.secretID)

    @commands.command()
    async def aa(self, ctx, link: str=None, album_name: str=None): #rework album_name to accept multiple words
        if not link or not album_name:
            await ctx.send('Please include a link to the album and a name for the album.')

        possible_links = ['https://imgur.com/gallery/', 'https://imgur.com/a/']
        if not any(x in link for x in possible_links):
            await ctx.send('That doesnt look like a valid link.')

        else:
            album_name = album_name.lower()
            self.bot.serverconfig = pyson.Pyson(f'data/servers/{str(ctx.guild.id)}/config.json')
            albums = self.bot.serverconfig.data.get('albums')
            if album_name not in albums:
                self.bot.serverconfig.data['albums'][album_name] = link
                self.bot.serverconfig.save()
                await ctx.send(f'woowoo {album_name}')
            else:
                await ctx.send('already exists fool')

    @commands.command()
    async def da(self, ctx, album_name: str=None):
        if not album_name:
            await ctx.send('please provide an album name')

        if album_name.lower() in self.bot.serverconfig.data.get('albums'):
            self.bot.serverconfig.data['albums'].pop(album_name, None)
            self.bot.serverconfig.save()
            await ctx.send('removed')
            
        else:
            await ctx.send(f'couldnt find an album the name of {album_name}')

    @commands.command()
    async def p1(self, ctx, album_name: str=None):
        if not album_name:
            if len(self.bot.serverconfig.data.get('albums')) >= 2:
                await ctx.send('seems you need to provide an album name')
            elif len(self.bot.serverconfig.data.get('albums')) == 1: #hopefully can rework this, thanks imgur
                emoji = discord.utils.get(self.bot.emojis, name='check')
                await ctx.message.add_reaction(emoji)
                tail = list(self.bot.serverconfig.data.get('albums').values())[0].split('/')[4]
                pick_one = random.choice(list(item.link for item in self.imgur_client.get_album_images(tail)))
                f = discord.File(io.BytesIO(requests.get(pick_one).content), filename="image.png")
                e = discord.Embed(title="I Chose..", colour=discord.Colour(0x278d89), )
                e.set_image(url=f'''attachment://image.png''')
                await ctx.send(file=f, embed=e, content='You asked me to pick a picture...')

            elif not self.bot.serverconfig.data.get('albums'):
                await ctx.send('have you even added an album?')

        #add album names + check for multi phrase


def setup(bot):
    bot.add_cog(imgur(bot))
