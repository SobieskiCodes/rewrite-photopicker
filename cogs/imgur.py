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

    @commands.command() #need to create check for admins/owners only to use this
    async def aa(self, ctx, link: str=None, album_name: str=None): #rework album_name to accept multiple words
        if not link or not album_name:
            await ctx.send('Please include a link to the album and a name for the album.')
            return

        possible_links = ['https://imgur.com/gallery/', 'https://imgur.com/a/'] #leaving this for additions later
        if not any(x in link for x in possible_links):
            await ctx.send('That doesnt look like a valid link.')

        else:
            album_name = album_name.lower()
            self.bot.serverconfig = pyson.Pyson(f'data/servers/{str(ctx.guild.id)}/config.json')
            if album_name not in self.bot.serverconfig.data.get('albums'):
                self.bot.serverconfig.data['albums'][album_name] = link
                self.bot.serverconfig.save()
                await ctx.send(f'woowoo {album_name}')
            else:
                await ctx.send('already exists fool')

    @commands.command() #need to create check for admins/owners only to use this
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
        if len(self.bot.serverconfig.data.get('albums')) is 0:
            await ctx.send('you should probably add an album first..')
            return

        if not album_name:
            if len(self.bot.serverconfig.data.get('albums')) >= 2:
                await ctx.send('seems you need to provide an album name')
                return

            elif len(self.bot.serverconfig.data.get('albums')) == 1: #will swap this to local storage soon.
                await ctx.message.add_reaction(discord.utils.get(self.bot.emojis, name='check'))
                tail = list(self.bot.serverconfig.data.get('albums').values())[0].split('/')[4]
                pick_one = random.choice(list(item.link for item in self.imgur_client.get_album_images(tail)))
                f = discord.File(io.BytesIO(requests.get(pick_one).content), filename="image.png")
                e = discord.Embed(title="I Chose..", colour=discord.Colour(0x278d89), )
                e.set_image(url=f'''attachment://image.png''')
                await ctx.send(file=f, embed=e, content='You asked me to pick a picture...')

            elif not self.bot.serverconfig.data.get('albums'):
                await ctx.send('have you even added an album?')

        if album_name in self.bot.serverconfig.data.get('albums'):
            await ctx.message.add_reaction(discord.utils.get(self.bot.emojis, name='check'))
            tail = self.bot.serverconfig.data.get('albums').get(album_name).split('/')[4]
            pick_one = random.choice(list(item.link for item in self.imgur_client.get_album_images(tail)))
            f = discord.File(io.BytesIO(requests.get(pick_one).content), filename="image.png")
            e = discord.Embed(title="I Chose..", colour=discord.Colour(0x278d89), )
            e.set_image(url=f'''attachment://image.png''')
            await ctx.send(file=f, embed=e, content='You asked me to pick a picture...')

        elif not album_name and len(self.bot.serverconfig.data.get('albums')) >= 2:
            await ctx.send(f'i couldnt find an album the name of {album_name}')

    @commands.command()
    async def al(self, ctx):
        if len(self.bot.serverconfig.data.get('albums')) is not 0:
            await ctx.send(f"list of albums i see are {', '.join(list(self.bot.serverconfig.data.get('albums')))}")

        else:
            await ctx.send('do you even have any albums added bro?')

    @commands.command() #need to create check for admins/owners only to use this
    async def adda(self, ctx, member: discord.Member = None):
        if not member:
            await ctx.send('you should probably include a member.')
            return
        else:
            self.bot.serverconfig.data['config']['admins'].append(member.id)
            self.bot.serverconfig.save()
            await ctx.send(f'{member.mention} has been added as an admin.')

    @adda.error
    async def pic_error(self, ctx, exception): #so this is a thing.
        await ctx.send('Member not found! Try mentioning them instead.')


def setup(bot):
    bot.add_cog(imgur(bot))
