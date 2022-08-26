import discord
from discord.ext import commands

import random

class Games(commands.Cog):
    def __init__(self, bot):
        print("IN INIT")
        self.bot = bot

    @commands.command(name='conch', pass_context = True, aliases=['magicconch'])
    async def conch(self, ctx):
        rand = random.randint(0,17)
    
        responses = ["IT IS CERTAIN.", "IT IS DECIDEDLY SO.", "WITHOUT A DOUBT", "YES - DEFINITELY", "YOU MAY RELY ON IT.", "AS I SEE IT, YES.", "MOST LIKELY.", "SIGNS POINT TO YES.", "TRY ASKING AGAIN",
        "ASK AGAIN LATER.", "BETTER NOT TELL YOU NOW.", "CANNOT PREDICT NOW", "CONCENTRATE AND ASK AGAIN.", " DON'T COUNT ON IT.", "MY REPLY IS NO.", "MY SOURCES SAY NO.", "OUTLOOK NOT SO GOOD.", "VERY DOUBTFUL"]

        imgURL = "https://i.imgur.com/RLsojmN.jpg"
        embed=discord.Embed(color=0xf1d3ed)
        embed.set_image( url = imgURL )
        embed.add_field(name="Magic Conch", value=responses[rand], inline=False)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Games(bot))