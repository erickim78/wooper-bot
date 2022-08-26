import config
import discord
from discord.ext import commands
import os
import asyncio

# Main Function
async def main():
    async with bot:
        await load_extensions()
        await bot.start(config.botToken)

# Load Cogs
async def load_extensions():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')
            print(f'Loaded {filename} Cog')

# Run Main Script
if __name__ == '__main__':
    # Run main script
    intents = discord.Intents.default()
    intents.members = True
    intents.message_content = True
    bot = commands.Bot(command_prefix='?', intents=intents)
    asyncio.run(main())