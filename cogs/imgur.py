from cogs.util.checks import is_admin
from discord.ext import commands
from imgurpython import ImgurClient
from imgurpython.helpers.error import ImgurClientError
from cogs.util.errors import NotAuthorized
import random
import discord
import io


class imgur(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.clientID = bot.config.get('imgur_client_id')
        self.secretID = bot.config.get('imgur_client_secret')
        self.imgur_client = ImgurClient(self.clientID, self.secretID)


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
            fetch_albums = await self.bot.fetch.all(f"SELECT * FROM Albums WHERE GuildID=?", (ctx.guild.id,))
            fetch_album_names = list([album[2] for album in fetch_albums]) if fetch_albums else []
            if album_name not in fetch_album_names:
                await self.bot.db.execute(f"INSERT INTO Albums(GuildID, AlbumName, AlbumLink) VALUES (?, ?, ?)",
                                          (ctx.guild.id, album_name, link,))
                await self.bot.db.commit()
                await ctx.send(f'"{album_name}" has been added!')
            else:
                await ctx.send(f'"{album_name}" already exists')

    @is_admin()
    @commands.command(aliases=['delalbum', 'remalbum', 'da', 'ra'])
    async def deletealbum(self, ctx, *, album_name: str = None):
        """
        deletealbum [album name] - Deletes an album, name.
        ex; .deletealbum a phone
        """
        if not album_name:
            await ctx.send('Please provide an album name.')

        if album_name:
            album_name = album_name.lower()
            fetch_album = await self.bot.fetch.one(f"SELECT * FROM Albums WHERE GuildID=? AND AlbumName=?",
                                                   (ctx.guild.id, album_name))
            if fetch_album:
                await self.bot.db.execute(f"DELETE FROM Albums WHERE GuildID=? And AlbumName=?",
                                          (ctx.guild.id, album_name,))
                await self.bot.db.commit()
                await ctx.send(f'Removed album "{album_name}"')

            else:
                await ctx.send(f'Couldn\'t find an album the name of "{album_name}"')

    @commands.command(aliases=['p1', 'po', 'pick'])
    async def pickone(self, ctx, *, album_name: str = None):
        """
        pickone (Optional album name) - picks a random image from the album.
        ex; .pickone a phone
        If only one album exists you do not provide an album name.
        """
        grab_content_title_config = await self.bot.fetch.one(f"SELECT Content, Title FROM GuildConfig WHERE ID=?",
                                                             (ctx.guild.id,))
        content = grab_content_title_config[0]
        title = grab_content_title_config[1]
        if content is None and title is None:
            content = 'You asked me to pick a picture...'
            title = 'I Chose...'

        if album_name:
            album_name = album_name.lower()
            fetch_album = await self.bot.fetch.one(f"SELECT * FROM Albums WHERE GuildID=? AND AlbumName=?",
                                                    (ctx.guild.id, album_name,))
            if not fetch_album:
                return await ctx.send("Couldnt find an album by that name")

            if len(fetch_album) == 0:
                return await ctx.send('You should probably add an album first..')
            imgur_link = fetch_album[3]

        if not album_name:
            fetch_albums = await self.bot.fetch.all(f"SELECT AlbumName, AlbumLink FROM Albums WHERE GuildID=?",
                                                    (ctx.guild.id,))
            if not fetch_albums:
                return await ctx.send("Might want to add an album first!")

            if len(fetch_albums) >= 2:
                return await ctx.send('Seems you forgot to provide an album name!')
            imgur_link = fetch_albums[0][1]

        try:
            await ctx.message.add_reaction(discord.utils.get(self.bot.emojis, name='check'))
        except:
            pass

        try:
            tail = imgur_link.split('/')[4]
            the_list = list(item.link for item in self.imgur_client.get_album_images(tail))
            item = random.choice(the_list)
            item_id = item.split('/')[3][0:-4]
            if title in ['album title', 'Album Title']:
                title = self.imgur_client.get_album(tail).title
            if content in ['description', 'Description']:
                content = self.imgur_client.get_image(item_id).description
            if (self.imgur_client.get_image(item_id).size * 1e-6) > 8.0:
                return await ctx.send(f"{self.imgur_client.get_image(item_id).link} was too big to send.")
            get_stream_status = await self.bot.fetch.one(f"SELECT Stream FROM GuildConfig WHERE ID=?", (ctx.guild.id,))
            stream = get_stream_status[0]
            async with self.bot.aiohttp.get(item) as resp:
                link = await resp.read()
                if item.endswith('.gif'):
                    f = discord.File(io.BytesIO(link), filename="image.gif")
                    e = discord.Embed(title=title, colour=discord.Colour(0x278d89), )
                    if stream:
                        e.set_image(url=f'''attachment://image.gif''')
                    else:
                        e.set_image(url=f'{self.imgur_client.get_image(item_id).link}')
                else:
                    f = discord.File(io.BytesIO(link), filename="image.png")
                    e = discord.Embed(title=title, colour=discord.Colour(0x278d89), )
                    if stream:
                        e.set_image(url=f'''attachment://image.png''')
                    else:
                        e.set_image(url=f'{self.imgur_client.get_image(item_id).link}')

                e.set_footer(text=f'storage is currently: {"link" if not stream else "stream"} \n'
                                  f'if images aren\'t showing up, try toggling this with .stream')
                if stream:
                    await ctx.send(file=f, embed=e, content=content)

                if not stream:
                    await ctx.send(embed=e, content=content)

        except Exception as e:
            print(f'{e}, tail: {tail if tail else None} link: {imgur_link}, item: {item if item else None}')
            if isinstance(e, ImgurClientError):
                print(f'{e.error_message}')
                return await ctx.send(f'{e.error_message}')
            elif not isinstance(e, ImgurClientError):
                return await ctx.send(f'There was an issue processing this command.\nDebug: `{e}`')

    @commands.command(aliases=['al', 'list'])
    async def albumlist(self, ctx):
        """albumlist - displays all currently added albums by name.

        """
        fetch_albums = await self.bot.fetch.all(f"SELECT * FROM Albums WHERE GuildID=?", (ctx.guild.id,))
        if fetch_albums:
            list_album_names = ", ".join(list([album[2] for album in fetch_albums]))
            await ctx.send(f"{list_album_names}")
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
            check_if_pwr_user = await self.bot.fetch.one(f"SELECT * FROM Permissions WHERE MemberID=? AND GuildID=?",
                                                            (ctx.author.id, ctx.guild.id,))
            if not check_if_pwr_user:
                await self.bot.db.execute(f"INSERT INTO Permissions(MemberID, GuildID) VALUES (?, ?)",
                                          (ctx.author.id, ctx.guild.id,))
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
            chck_if_usr_is_admin = await self.bot.fetch.one(f"SELECT * FROM Permissions WHERE MemberID=? AND GuildID=?",
                                                            (ctx.author.id, ctx.guild.id,))
            if chck_if_usr_is_admin:
                await self.bot.db.execute(f"DELETE FROM Permissions WHERE MemberID=? AND GuildID=?",
                                                            (ctx.author.id, ctx.guild.id,))
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
        content_title = content_title.lower()
        if content_title in editable_args:
            if content_title == "title":
                await self.bot.db.execute(f"UPDATE GuildConfig SET Title=? WHERE ID=?",
                                          (message, ctx.guild.id,))
            if content_title == 'content':
                await self.bot.db.execute(f"UPDATE GuildConfig SET Content=? WHERE ID=?",
                                          (message, ctx.guild.id,))

            await self.bot.db.commit()
            await ctx.send(f'{content_title.lower()} updated.')

        else:
            await ctx.send("Invalid parameters.")

    @is_admin()
    @commands.command()
    async def stream(self, ctx):
        """
        Toggles how the images are sent to discord, if images aren't showing up try toggling this.
        """
        get_stream_status = await self.bot.fetch.one(f"SELECT Stream FROM GuildConfig WHERE ID=?", (ctx.guild.id,))
        update_stream_status = await self.bot.db.execute(f"UPDATE GuildConfig SET Stream=? WHERE ID=?",
                                                   (not get_stream_status[0], ctx.guild.id))
        await self.bot.db.commit()
        await ctx.send(f"Streaming turned {'on' if not get_stream_status[0] else 'off'}")
        # opposite because we don't re-fetch the current we just assume the database changed.


def setup(bot):
    bot.add_cog(imgur(bot))
