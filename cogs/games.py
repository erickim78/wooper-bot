import discord
from discord.ext import commands
from discord import app_commands

import random
import config

class Games(commands.Cog):
    def __init__(self, bot):
        print("IN INIT")
        self.bot = bot

    @app_commands.command(name='conch', description='Ask the Magic Conch for an answer.')
    async def conch(self, interaction: discord.Interaction, question: str) -> None:
        rand = random.randint(0,17)
    
        responses = ["IT IS CERTAIN.", "IT IS DECIDEDLY SO.", "WITHOUT A DOUBT", "YES - DEFINITELY", "YOU MAY RELY ON IT.", "AS I SEE IT, YES.", "MOST LIKELY.", "SIGNS POINT TO YES.", "TRY ASKING AGAIN",
        "ASK AGAIN LATER.", "BETTER NOT TELL YOU NOW.", "CANNOT PREDICT NOW", "CONCENTRATE AND ASK AGAIN.", " DON'T COUNT ON IT.", "MY REPLY IS NO.", "MY SOURCES SAY NO.", "OUTLOOK NOT SO GOOD.", "VERY DOUBTFUL"]

        imgURL = "https://i.imgur.com/RLsojmN.jpg"
        embed=discord.Embed(color=0xf1d3ed)
        embed.set_image( url = imgURL )
        embed.add_field(name="Magic Conch", value=question, inline=False)
        embed.add_field(name=responses[rand], value='\u200b', inline=False)
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Games(bot), guilds=config.guildList)