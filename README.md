# Photopicker

This is a rewrite of the rewrite version(branch) of my async branch [photopicker](https://github.com/SobieskiCodes/discord_bots_ASYNC/tree/master/photopicker)
Written to handle asynchronous compatibility with aiohttp requests, SQLite storage, and local image caching (spoiler alert, it never happened).
This is likely to be the final version with the deprecation of discord.py


[invite](https://discordapp.com/oauth2/authorize?client_id=451153773859962881&scope=bot&permissions=511040)


### Commands
[]Indicates required ()Indicates Options *Is an available alias ~Requires manage guild perms or added as an admin
# Owner Commands - Not available in public bot
```
load [cog name] - Loads a cog you've uploaded, case sensitive.
unload [cog name] - Unloads a cog you have enabled, case sensitive.
reload [cog name] - Reloads a cog you've changed thats active, case sensitive.
echo (message) - Replies back in channel provided text.
vme - Displays info about the bot, version, server count, member count, uptime.
sts [message] - Changes the presence of the bot
ui [message] - Updates the <info> command text
```
# Guild Owner Commands
```
setprefix [prefix] *sp - Set the prefix for the guild, if no prefix is provided it will spit the current prefix (works with mention)
invite *inv - Send the invite link to the channel
```
# General Commands
```
album [link] [name] ~ *addalbum, aa - Add an album ex; album https://imgur.com/gallery/MnIjj3n a phone
deletealbum [name] ~ *delalbum,remalbum,da,ra - Delete an album ex; delalbum a phone
addadmin [name/mention] ~ *adda,admin - Adds an admin to the bot, can be a case sensitive name or mention
removeadmin [name/mention] ~ *remadmin,deladmin,deleteadmin - Removes and admin, same as addadmin
pickone [album] *p1,po,pick - Pick a random image from the album, if only one album it will not require an album name
albumlist *al,list - Lists all albums in the server
info - Displays custom text set by owner of the bot
set [content/title](message) ~ - Change the title/content from "I Chose..." "you asked.." can be blank
To set the content/title to the title/description from imgur use the setup below:
['album title', 'Album Title'] title must be set to one of those; ~set title album title
['description', 'Description'] content needs to be set to one of those; ~set content description
```

### Requirements
python3.6+

```
discord.py==1.7.3
jthon==1.0.2
aiosqlite==0.17.0
```

And a json file under /data/config name 'startup.json'

```
{
    "config": {
        "discord_token": "Discord token here",
        "imgur_client_id": "client id here",
        "imgur_client_secret": "client secret here",
        "info": "what you want the info command to say here \n breaks are supported"
    }
}
```



## Built With

* [Discord.py](https://github.com/Rapptz/discord.py/) - a modern, easy to use, feature-rich, and async ready API wrapper for Discord.

## Authors

* **Justin Sobieski** - [Sobieski.Codes](https://sobieski.codes)

## License

This project is licensed under the The Unlicense - see the [LICENSE.md](LICENSE) file for details

## Acknowledgments

* Special thanks to [stroupbslayen](https://github.com/stroupbslayen) for the snippets and constant answers for stupid questions.

