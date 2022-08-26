import discord
from discord.ext import commands

class Initial(commands.Cog):
    def __init__(self, bot):
        print("INITIAL INIT")
        self.bot = bot

    # On Ready
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Logged in as {self.bot.user}')
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id == 125114599249936384:
            await message.channel.send("says the furniture stealer")


async def setup(bot):
    await bot.add_cog(Initial(bot))