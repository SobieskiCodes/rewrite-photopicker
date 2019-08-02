from discord.ext import commands
from imgurpython import ImgurClient
from imgurpython.helpers.error import ImgurClientError
from cogs.util.errorhandling import NotAuthorized
import random
import discord
import io


def is_admin():
    async def predicate(ctx):
        if ctx.author.id == ctx.message.guild.owner.id or ctx.author.guild_permissions.administrator:
            return True
        get_admins = await imgur.fetch_all(ctx, f'SELECT AdminID FROM GuildAdmins WHERE GuildID={ctx.guild.id}')
        if get_admins and ctx.author.id in list(userid[0] for userid in get_admins):
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

    async def fetch_one(self, arg):
        get = await self.bot.db.execute(arg)
        results = await get.fetchone()
        return results

    async def fetch_all(self, arg):
        get = await self.bot.db.execute(arg)
        results = await get.fetchall()
        return results

    @is_admin()
    @commands.command(aliases=['addalbum', 'aa'])
    async def album(self, ctx, link: str = None, *, album_name: str = None):
        """addalbum [album link] [album name] - Adds an album, link, and name.
        ex; .addalbum https://imgur.com/gallery/MnIjj3n a phone
        and 'pickone a phone' would call this album.
        """
        if not link or not album_name:
            await ctx.send('Please include a link to the album and a name for the album.')
            return

        possible_links = ['https://imgur.com/gallery/', 'https://imgur.com/a/'] #leaving this for additions later
        if not any(x in link for x in possible_links):
            await ctx.send('That doesnt look like a valid link.')

        else:
            album_name = album_name.lower()
            get_albums = await imgur.fetch_all(self, f'SELECT AlbumLink FROM GuildAlbums WHERE GuildID={ctx.guild.id}')
            if link not in list(albumlink[0] for albumlink in get_albums):
                await self.bot.db.execute(f"INSERT INTO GuildAlbums(GuildID, AlbumLink, AlbumName) "
                                          f"VALUES (?, ?, ?)", (ctx.guild.id, link, album_name))
                await self.bot.db.commit()
                await ctx.send(f'"{album_name}" has been added!')
            else:
                albums_name = await imgur.fetch_one(self, f'SELECT AlbumName FROM GuildAlbums WHERE AlbumLink="{link}"')
                await ctx.send(f'{link} already exists as {albums_name[0]}.')

    @is_admin()
    @commands.command(aliases=['delalbum', 'remalbum', 'da', 'ra'])
    async def deletealbum(self, ctx, *, album_name: str=None):
        """deletealbum [album name] - Deletes an album, name.
        ex; .deletealbum a phone
        """
        if not album_name:
            await ctx.send('Please provide an album name.')
        get_albums = await imgur.fetch_all(self, f'SELECT AlbumName FROM GuildAlbums WHERE GuildID={ctx.guild.id}')
        if album_name.lower() in list(albumnames[0] for albumnames in get_albums):
            await self.bot.db.execute(f'DELETE FROM GuildAlbums WHERE GuildID=? and AlbumName=?',
                                      (ctx.guild.id, album_name.lower()))
            await self.bot.db.commit()
            await ctx.send(f'Removed album "{album_name}"')

        else:
            await ctx.send(f'Couldnt find an album the name of "{album_name}"')

    @commands.command(aliases=['p1', 'po', 'pick'])
    async def pickone(self, ctx, *, album_name: str = None):
        """pickone (Optional album name) - picks a random image from the album.
        ex; .pickone a phone
        If only one album exists you do not provide an album name.
        """
        album_names = await imgur.fetch_all(self, f'SELECT AlbumName FROM GuildAlbums WHERE GuildID={ctx.guild.id}')
        if not album_names:
            await ctx.send('You should probably add an album first..')
            return

        content = await imgur.fetch_one(self, f'SELECT Content FROM GuildConfig WHERE ID={ctx.guild.id}')
        title = await imgur.fetch_one(self, f'SELECT Title FROM GuildConfig WHERE ID={ctx.guild.id}')
        await ctx.message.add_reaction(discord.utils.get(self.bot.emojis, name='check'))
        content = 'You asked me to pick a picture...' if not content[0] else content[0]
        title = 'I Chose...' if not title[0] else title[0]
        if album_name:
            if album_name.lower() in list(albumnames[0] for albumnames in album_names):
                album_link = await imgur.fetch_one(self, f'SELECT AlbumLink FROM GuildAlbums WHERE '
                                                         f'AlbumName="{album_name.lower()}" and GuildID={ctx.guild.id}')
                tail = album_link[0].split('/')[4]
                the_list = list(item.link for item in self.imgur_client.get_album_images(tail))
            else:
                await ctx.send(f'I couldnt find an album by the name of "{album_name}"')

        if not album_name:
            if len(album_names) >= 2:
                await ctx.send('Seems you forgot to provide an album name!')
                return
            if len(album_names) == 1:
                album_link = await imgur.fetch_one(self, f'SELECT AlbumLink FROM GuildAlbums WHERE '
                                                         f'AlbumName="{album_names[0][0]}" and GuildID={ctx.guild.id}')
                tail = album_link[0].split('/')[4]
                the_list = list(item.link for item in self.imgur_client.get_album_images(tail))
        try:
            item = random.choice(the_list)
            item_id = item.split('/')[3][0:-4]
            if title in ['album title', 'Album Title']:
                title = self.imgur_client.get_album(tail).title
            if content in ['description', 'Description']:
                content = self.imgur_client.get_image(item_id).description
            async with self.bot.aiohttp.get(item) as resp:
                link = await resp.read()
                if item.endswith('.gif'):
                    f = discord.File(io.BytesIO(link), filename="image.gif")
                    e = discord.Embed(title=title, colour=discord.Colour(0x278d89))
                    e.set_image(url=f'''attachment://image.gif''')
                else:
                    f = discord.File(io.BytesIO(link), filename="image.png")
                    e = discord.Embed(title=title, colour=discord.Colour(0x278d89))
                    e.set_image(url=f'''attachment://image.png''')
                await ctx.send(file=f, embed=e, content=content)

        except Exception as e:
            if isinstance(e, ImgurClientError):
                print(f'{e.error_message}')
                await ctx.send(f'{e.error_message}')
            elif not isinstance(e, ImgurClientError):
                await ctx.send(f'There was an issue processing this command. {e}')

    @commands.command(aliases=['al', 'list'])
    async def albumlist(self, ctx):
        """albumlist - displays all currently added albums by name.
        """
        album_names = await imgur.fetch_all(self, f'SELECT AlbumName FROM GuildAlbums WHERE GuildID={ctx.guild.id}')
        if len(album_names) is not 0:
            await ctx.send(f"The list of albums I see are: {', '.join(list(an[0] for an in album_names))}.")
        else:
            await ctx.send('It doesnt seem that you have added an ablum.')

    @is_admin()
    @commands.command(aliases=['adda', 'admin'])
    async def addadmin(self, ctx, member: discord.Member = None):
        """addadmin [user name] - Adds an admin
        ex; .addadmin @ProbsJustin#0001
        You can attempt to use just a string name; eg ProbsJustin but recommend a mention.
        """
        if not member:
            await ctx.send('You should probably include a member.')
            return
        else:
            get_admins = await imgur.fetch_all(self, f'SELECT AdminID FROM GuildAdmins WHERE GuildID={ctx.guild.id}')
            if member.id not in list(admin[0] for admin in get_admins):
                await self.bot.db.execute(f"INSERT INTO GuildAdmins(GuildID, AdminID) VALUES (?, ?)",
                                          (ctx.guild.id, member.id))
                await self.bot.db.commit()
                await ctx.send(f'{member.mention} has been added as an admin.')
            else:
                await ctx.send('That user is already an admin!')

    @is_admin()
    @commands.command(aliases=['remadmin', 'deladmin', 'deleteadmin'])
    async def removeadmin(self, ctx, member: discord.Member = None):
        """removeadmin [user name] - Remove an admin
        ex; .removeadmin @ProbsJustin#0001
        You can attempt to use just a string name; eg ProbsJustin but recommend a mention.
        """
        if not member:
            await ctx.send('You should probably include a member.')
            return
        else:
            get_admins = await imgur.fetch_all(self, f'SELECT AdminID FROM GuildAdmins WHERE GuildID={ctx.guild.id}')
            if member.id in list(admin[0] for admin in get_admins):
                await self.bot.db.execute(f'DELETE FROM GuildAdmins WHERE GuildID=? and AdminID=?',
                                          (ctx.guild.id, member.id))
                await self.bot.db.commit()
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
    async def set(self, ctx, content_title: str = None, *, message: str = ''):
        """set [content/title] [name] - Change the title/content from "I Chose..." "you asked.." """
        editable_args = ['content', 'title']
        if not content_title:
            await ctx.send(f"Please provide either {' or '.join(editable_args)}.")
            return

        if content_title.lower() in editable_args:
            await self.bot.db.execute(f'UPDATE GuildConfig SET {content_title.title()}="{message}" '
                                      f'WHERE ID={ctx.guild.id}')
            await self.bot.db.commit()
            await ctx.send(f'{content_title.lower()} updated.')

        else:
            await ctx.send("Invalid parameters.")


def setup(bot):
    bot.add_cog(imgur(bot))
