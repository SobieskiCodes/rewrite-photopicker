from cogs.util import pyson
from discord.ext import commands
from imgurpython import ImgurClient
from imgurpython.helpers.error import ImgurClientError
from cogs.util.errorhandling import NotAuthorized
import random
import discord
import io


def is_admin():
    '''Checks if the message author is the owner or has admin perms'''
    def predicate(ctx):
        if ctx.author.id == ctx.message.guild.owner.id or ctx.author.guild_permissions.manage_guild:
            return True

        if ctx.author.id in pyson.Pyson(f'data/servers/{str(ctx.guild.id)}/config.json').data.get('config').get('admins'):
            return True

        else:
            raise NotAuthorized
    return commands.check(predicate)


class imgur(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.clientID = bot.config.data.get('config').get('imgur_client_id')
        self.secretID = bot.config.data.get('config').get('imgur_client_secret')
        self.imgur_client = ImgurClient(self.clientID, self.secretID)

    @is_admin()
    @commands.command(aliases=['addalbum', 'aa'])
    async def album(self, ctx, link: str=None, *, album_name: str=None):
        '''addalbum [album link] [album name] - Adds an album, link, and name.
        ex; .addalbum https://imgur.com/gallery/MnIjj3n a phone
        and 'pickone a phone' would call this album.
        '''
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
                await ctx.send(f'"{album_name}" has been added!')
            else:
                await ctx.send(f'"{album_name}" already exists.')

    @is_admin()
    @commands.command(aliases=['delalbum', 'remalbum', 'da', 'ra'])
    async def deletealbum(self, ctx, *, album_name: str=None):
        '''deletealbum [album name] - Deletes an album, name.
        ex; .deletealbum a phone
        '''
        if not album_name:
            await ctx.send('Please provide an album name.')

        if album_name.lower() in self.bot.serverconfig.data.get('albums'):
            self.bot.serverconfig.data['albums'].pop(album_name, None)
            self.bot.serverconfig.save()
            await ctx.send(f'Removed album "{album_name}"')

        else:
            await ctx.send(f'Couldnt find an album the name of "{album_name}"')

    @commands.command(aliases=['p1', 'po', 'pick'])
    async def pickone(self, ctx, *, album_name: str=None):
        '''pickone (Optional album name) - picks a random image from the album.
        ex; .pickone a phone
        If only one album exists you do not provide an album name.
        '''
        if len(self.bot.serverconfig.data.get('albums')) is 0:
            await ctx.send('You should probably add an album first..')
            return

        content = self.bot.serverconfig.data.get('config').get('content')
        title = self.bot.serverconfig.data.get('config').get('title')
        if content is None and title is None:
            content = 'You asked me to pick a picture...'
            title = 'I Chose...'

        if not album_name:
            if len(self.bot.serverconfig.data.get('albums')) >= 2:
                await ctx.send('Seems you forgot to provide an album name!')
                return

            elif len(self.bot.serverconfig.data.get('albums')) == 1: #will swap this to local storage soon.
                await ctx.message.add_reaction(discord.utils.get(self.bot.emojis, name='check'))
                try:
                    self.bot.serverid = f'{ctx.guild.id}'
                    self.bot.serveralbum = pyson.Pyson(f'data/servers/{self.bot.serverid}/config.json')
                    tail = list(self.bot.serveralbum.data.get('albums').values())[0].split('/')[4]
                    print(f'serverid: {self.bot.serverid} tail:  {tail}')
                    the_list = list(item.link for item in self.imgur_client.get_album_images(tail))
                    item = random.choice(the_list)
                    item_id = item.split('/')[3][0:-4]
                    if title in ['album title', 'Album Title']:
                        title = self.imgur_client.get_album(tail).title
                    if content in ['description', 'Description']:
                        content = self.imgur_client.get_image(item_id).description

                    async with self.bot.aiohttp.get(item) as resp:
                        link = await resp.read()
                        f = discord.File(io.BytesIO(link), filename="image.png")
                        e = discord.Embed(title=title, colour=discord.Colour(0x278d89), )
                        e.set_image(url=f'''attachment://image.png''')
                        await ctx.send(file=f, embed=e, content=content)

                except Exception as e:
                    print(f'{e} - single album')
                    print(f"albums = {list(self.bot.serverconfig.data.get('albums'))}")
                    print(f"length = {len(list(self.bot.serverconfig.data.get('albums')))}")
                    for album in list(self.bot.serverconfig.data.get('albums')):
                        print(f"name: {album} link: {self.bot.serverconfig.data.get('albums').get(album)}")
                    if isinstance(e, ImgurClientError):
                        print(f'{e.error_message}')
                        await ctx.send(f'{e.error_message}')
                    elif not isinstance(e, ImgurClientError):
                        await ctx.send('There was an issue processing this command.')

            elif not self.bot.serverconfig.data.get('albums'):
                await ctx.send('It doesnt seem that you have added an ablum.')

        elif album_name:
            if album_name.lower() in self.bot.serverconfig.data.get('albums'):
                await ctx.message.add_reaction(discord.utils.get(self.bot.emojis, name='check'))
                try:
                    self.bot.serveridmulti = f'{ctx.guild.id}'
                    self.bot.serveralbummulti = pyson.Pyson(f'data/servers/{self.bot.serveridmulti}/config.json')
                    tail = self.bot.serveralbummulti.data.get('albums').get(album_name.lower()).split('/')[4]
                    the_list = list(item.link for item in self.imgur_client.get_album_images(tail))
                    item = random.choice(the_list)
                    item_id = item.split('/')[3][0:-4]
                    if title in ['album title', 'Album Title']:
                        title = self.imgur_client.get_album(tail).title
                    if content in ['description', 'Description']:
                        content = self.imgur_client.get_image(item_id).description

                    async with self.bot.aiohttp.get(item) as resp:
                        link = await resp.read()
                        f = discord.File(io.BytesIO(link), filename="image.png")
                        e = discord.Embed(title=title, colour=discord.Colour(0x278d89), )
                        e.set_image(url=f'''attachment://image.png''')
                        await ctx.send(file=f, embed=e, content=content)

                except Exception as e:
                    print(f'{e} - multialbum')
                    print(f'message = {ctx.message.content}')
                    print(f"albums = {list(self.bot.serverconfig.data.get('albums'))}")
                    for album in list(self.bot.serverconfig.data.get('albums')):
                        print(f"name: {album} link: {self.bot.serverconfig.data.get('albums').get(album)}")
                    if isinstance(e, ImgurClientError):
                        print(f'{e.error_message}')
                        await ctx.send(f'{e.error_message}')
                    elif not isinstance(e, ImgurClientError):
                        await ctx.send('There was an issue processing this command.')

            elif album_name.lower() not in self.bot.serverconfig.data.get('albums'):
                await ctx.send(f'I couldnt find an album by the name of "{album_name}"')

    @commands.command(aliases=['al', 'list'])
    async def albumlist(self, ctx):
        '''albumlist - displays all currently added albums by name.
        '''
        if len(self.bot.serverconfig.data.get('albums')) is not 0:
            await ctx.send(f"The list of albums I see are: {', '.join(list(self.bot.serverconfig.data.get('albums')))}.")

        else:
            await ctx.send('It doesnt seem that you have added an ablum.')

    @is_admin()
    @commands.command(aliases=['adda', 'admin'])
    async def addadmin(self, ctx, member: discord.Member = None):
        '''addadmin [user name] - Adds an admin
        ex; .addadmin @ProbsJustin#0001
        You can attempt to use just a string name; eg ProbsJustin but recommend a mention.
        '''
        if not member:
            await ctx.send('You should probably include a member.')
            return
        else:
            if not member.id in self.bot.serverconfig.data.get('config').get('admins'):
                self.bot.serverconfig.data['config']['admins'].append(member.id)
                self.bot.serverconfig.save()
                await ctx.send(f'{member.mention} has been added as an admin.')
            else:
                await ctx.send('That user is already an admin!')

    @is_admin()
    @commands.command(aliases=['remadmin', 'deladmin', 'deleteadmin'])
    async def removeadmin(self, ctx, member: discord.Member = None):
        '''removeadmin [user name] - Remove an admin
        ex; .removeadmin @ProbsJustin#0001
        You can attempt to use just a string name; eg ProbsJustin but recommend a mention.
        '''
        if not member:
            await ctx.send('You should probably include a member.')
            return
        else:
            if member.id in self.bot.serverconfig.data.get('config').get('admins'):
                self.bot.serverconfig.data['config']['admins'].remove(member.id)
                self.bot.serverconfig.save()
                await ctx.send(f'{member.mention} has been removed as an admin.')
            else:
                await ctx.send('I couldnt find that user in the admin list.')

    @addadmin.error
    @removeadmin.error
    async def member_not_found_error(self, ctx, exception): #so this is a thing.
        if not isinstance(exception, NotAuthorized):
            await ctx.send('Member not found! Try mentioning them instead.')

    @is_admin()
    @commands.command()
    async def set(self, ctx, content_title: str=None, *, message: str=''):
        '''set [content/title] [name] - Change the title/content from "I Chose..." "you asked.."'''
        editable_args = ['content', 'title']
        if not content_title:
            await ctx.send(f"Please provide either {' or '.join(editable_args)}.")
            return

        if content_title.lower() in editable_args:
            self.bot.serverconfig.data['config'][content_title.lower()] = message
            self.bot.serverconfig.save()
            await ctx.send(f'{content_title.lower()} updated.')

        else:
            await ctx.send("Invalid parameters.")


def setup(bot):
    bot.add_cog(imgur(bot))
