from sqlite3 import Cursor
import discord
from discord.ext import commands
import config
import main
from discord import app_commands

class Simps(commands.Cog):
    def __init__(self, bot):
        print("Simps INIT")
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
    async def simps(self, interaction: discord.Interaction, user: discord.User) -> None:
        self.cursor.execute(f'''SELECT count(name) FROM sqlite_master WHERE type='table' AND name = '{user.id}' ''')

        # Build Embed Common Fields
        embed = discord.Embed(color=0xf1d3ed)
        embed.set_thumbnail(url=user.avatar.url)

        userName = user.name
        if userName[-1] == 's':
            embed.add_field(name=f'{user.name}\' simps', value='\u200b', inline=False)
        else:
            embed.add_field(name=f'{user.name}\'s simps', value='\u200b', inline=False)    
        
        # Build Simps String
        if self.cursor.fetchone()[0] == 1:
            self.cursor.execute(f'SELECT * FROM \'{str(user.id)}\' ORDER BY count DESC')
            simpList = self.cursor.fetchall()
            print(simpList)
            result = f''
            for i in range(min(5, len(simpList))):
                currentUser = self.bot.get_user(int(simpList[i][0]))
                if i > 0:
                    result += f'\n{i+1}) {currentUser.mention} \n\n'
                else:
                    result += f'**{i+1}) {currentUser.mention}** \n\n'
                    embed.set_image(url=currentUser.avatar.url)

            embed.add_field(name='\u200b', value=result, inline=False)
            await interaction.response.send_message(embed=embed)
        else:
            embed.add_field(name='\u200b', value=f'{user.mention} has no simps', inline=False)
            await interaction.response.send_message(embed=embed)

        return


async def setup(bot):
    await bot.add_cog(Simps(bot), guilds=config.guildList)