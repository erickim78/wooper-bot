# Discord
import discord
from discord.ext import commands
from discord import app_commands

import data
import config

from datetime import datetime, timezone
import pytz
from typing import List

class Helpers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def timezone_autocomplete(self, interaction: discord.Interaction, current: str,) -> List[app_commands.Choice[str]]:
        choices = data.timezones
        return [
            app_commands.Choice(name=choice, value=choice)
            for choice in choices if current.lower() in choice.lower()
        ]

    @app_commands.command(name="time", description='Check the time')
    @app_commands.autocomplete(timezone=timezone_autocomplete)
    async def time(self, interaction: discord.Interaction, timezone: str = 'Maple') -> None:
        currentTime = ""
        if timezone == 'Maple':
            currentTime = datetime.now(pytz.utc)
        elif timezone == 'Florence':
            currentTime = datetime.now(pytz.timezone('Australia/Melbourne'))
        elif timezone == 'Frame':
            currentTime = datetime.now(pytz.timezone('America/Los_Angeles'))
        elif timezone == 'Elliot':
            currentTime = datetime.now(pytz.timezone('America/New_York'))
        elif timezone == 'Char':
            currentTime = datetime.now(pytz.timezone('America/Chicago'))
        else:
            print("Errror")
            return

        imgURL = "https://static.wikia.nocookie.net/maplestory/images/3/35/Mob_Papulatus_Clock.png/revision/latest?cb=20110901131435"
        embed = discord.Embed(title="Papulatus Clock", description=f'Timezone: {timezone}', color=0xf1d3ed)
        embed.set_thumbnail( url = imgURL )
        embed.add_field(name=f'It is currently {currentTime.strftime("%I:%M %p")} in {timezone}', value='\u200b', inline=False)
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Helpers(bot), guilds=config.guildList)