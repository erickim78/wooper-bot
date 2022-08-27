import config
import discord
from discord.ext import commands
from discord import app_commands
import os
import asyncio
import sqlite3

class MyBot(commands.Bot):

    def __init__(self):
        myIntents = discord.Intents.default()
        myIntents.members = True
        myIntents.message_content = True
        super().__init__(
            command_prefix = "!",
            intents = myIntents,
            application_id = config.clientID
        )

    # Setup Hook
    async def setup_hook(self):
        await load_extensions()
        await bot.tree.sync(guild = config.elliotGuild)
        await bot.tree.sync(guild = config.testGuild)

    # On Ready
    async def on_ready(self):
        print(f'Logged in as {self.user}')

# Load Cogs
async def load_extensions():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')
            print(f'Loaded {filename} Cog')

# Init Sqlite DB
def initDatabase():
    connection = sqlite3.connect("bot.db")
    cursor = connection.cursor()


# Run Main Script
if __name__ == '__main__':
    bot = MyBot()
    bot.run(config.botToken)