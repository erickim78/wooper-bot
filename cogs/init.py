import discord
from discord.ext import commands
import config
import main

class Initial(commands.Cog):
    def __init__(self, bot):
        print("INITIAL INIT")
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_reaction_add(reaction, user):
        simp = user.id
        simped = reaction.message.author.id
        main.cursor.execute(f'''SELECT count(name) FROM sqlite_master WHERE type='table' AND name = '{simped}' ''')
        
        if cursor.fetchone()[0] == 1:
            print()
        else: 
            cursor.execute(f'CREATE TABLE {simped} (id TEXT, count TEXT, PRIMARYT KEY (id))')

async def setup(bot):
    await bot.add_cog(Initial(bot), guilds=config.guildList)