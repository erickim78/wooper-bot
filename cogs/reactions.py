from sqlite3 import Cursor
import discord
from discord.ext import commands
import config
import main
from discord import app_commands

class Reactions(commands.Cog):
    def __init__(self, bot):
        print("Reactions INIT")
        self.bot = bot
        self.connection = main.connection
        self.cursor = main.connection.cursor()
    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        print("On Reaction Add")

        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        simp = payload.user_id
        simped = message.author.id

        self.cursor.execute(f'''SELECT count(name) FROM sqlite_master WHERE type='table' AND name = '{simped}' ''')
        
        if self.cursor.fetchone()[0] == 1:
            print()
        else: 
            self.cursor.execute(f'''CREATE TABLE '{simped}' (id TEXT, count TEXT, PRIMARY KEY (id))''')

        self.cursor.execute(f'INSERT INTO \'{str(simped)}\' (id, count) VALUES ({str(simp)}, {1}) ON CONFLICT (id) DO UPDATE SET count = count + 1')
        self.connection.commit()
    
    @app_commands.command(name="simps", description='Simp Leaderboard')
    async def simps(self, interaction: discord.Interaction, user: str) -> None:
        return


async def setup(bot):
    await bot.add_cog(Reactions(bot), guilds=config.guildList)