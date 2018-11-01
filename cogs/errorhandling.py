from discord.ext import commands


class NotAuthorized(commands.CommandError):
    message = """Exception raised when the message author is not an owner/admin/has bot rights of the bot."""
    pass
