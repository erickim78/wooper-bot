# Dependencies
from sqlite3 import Cursor
import time

# File Imports
import config
import main

# Discord
import discord
from discord.ext import commands
from discord import app_commands


class Simps(commands.Cog):
    def __init__(self, bot):
        print("Simps INIT")
        self.bot = bot
        self.connection = main.connection
        self.cursor = main.connection.cursor()
        
        # Init Connected User List
        self.connectedUsers = {}

    def updateConnectedUsers(self):
        updateTime = time.time()
        for guild in self.bot.guilds:
            currentChannels = guild.voice_channels
            for channel in currentChannels:
                if channel == guild.afk_channel:
                    continue
                else:
                    members = channel.members
                    for currentMember in members:
                        self.connectedUsers[currentMember.id] = updateTime
    
    def updateTimes(self):
        disconnectTime = time.time()
        for memberId in self.connectedUsers:
            self.checkTable(memberId)
            for key2 in self.connectedUsers:
                timeDifference = disconnectTime - self.connectedUsers[key2]
                self.cursor.execute(f'INSERT INTO \'{str(memberId)}\' (id, count, reactions) VALUES ({str(key2)}, {timeDifference}, {0}) ON CONFLICT (id) DO UPDATE SET count = count + {timeDifference}')
        self.connection.commit()

        for memberId in self.connectedUsers:
            self.connectedUsers[memberId] = disconnectTime

    def checkTable(self, tableName):
        self.cursor.execute(f'''SELECT count(name) FROM sqlite_master WHERE type='table' AND name = '{tableName}' ''')
        if self.cursor.fetchone()[0] == 1:
            return
        else: 
            self.cursor.execute(f'''CREATE TABLE '{tableName}' (id TEXT, count DECIMAL (38,4), reactions TEXT, PRIMARY KEY (id))''')

    # On Ready
    @commands.Cog.listener()
    async def on_ready(self):
        self.updateConnectedUsers()
        print("Initially connected users: ", self.connectedUsers)
    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        print("On Reaction Add")

        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        simp = payload.user_id
        simped = message.author.id

        self.checkTable(simped)

        self.cursor.execute(f'INSERT INTO \'{str(simped)}\' (id, count, reactions) VALUES ({str(simp)}, {0}, {1}) ON CONFLICT (id) DO UPDATE SET reactions = reactions + 1')
        self.connection.commit()
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if after.channel == None:
            self.updateTimes()
            del self.connectedUsers[member.id]
        elif before.channel == None and after.channel != None:
            self.updateTimes()
            self.connectedUsers[member.id] = time.time()
        
        print("On voice status update: ", self.connectedUsers)
        return

    @app_commands.command(name="simps", description='Simp Leaderboard')
    async def simps(self, interaction: discord.Interaction, user: discord.User) -> None:
        self.cursor.execute(f'''SELECT count(name) FROM sqlite_master WHERE type='table' AND name = '{user.id}' ''')

        # Build Embed Common Fields
        embed = discord.Embed(color=0xf1d3ed)
        embed.set_thumbnail(url=user.avatar.url) 
        userName = user.name
        
        # Build Simps String
        if self.cursor.fetchone()[0] == 1:
            self.cursor.execute(f'SELECT * FROM \'{str(user.id)}\' ORDER BY count DESC')
            simpList = self.cursor.fetchall()

            referenceTime = 0
            delIndex = 0
            for x in range(len(simpList)):
                if int(simpList[x][0]) == user.id:
                    delIndex = x
                    referenceTime = float(simpList[x][1])
                    break

            if userName[-1] == 's':
                embed.add_field(name=f'{user.name}\' simps', value=f'*Online: {round(referenceTime//3600)} hrs, {round((referenceTime-3600*(referenceTime//3600))//60)} mins*', inline=False)
            else:
                embed.add_field(name=f'{user.name}\'s simps', value=f'*Online: {round(referenceTime//3600)} hrs, {round((referenceTime-3600*(referenceTime//3600))//60)} mins*', inline=False)   
            del simpList[delIndex]
            
            result = f''
            for i in range(min(5, len(simpList))):
                currentUser = self.bot.get_user(int(simpList[i][0]))
                currentTime = simpList[i][1]
                if i > 0:
                    result += f'{i+1}) {currentUser.mention}, {round((float(currentTime)/referenceTime)*100)}% Attendance \n*Time Together: {round(currentTime//3600)} hrs, {round((currentTime-3600*(currentTime//3600))//60)} mins*\n\n'
                else:
                    result += f'**{i+1}) {currentUser.mention},  {round((float(currentTime)/referenceTime)*100)}% Attendance** \n*Time Together: {round(currentTime//3600)} hrs, {round((currentTime-3600*(currentTime//3600))//60)} mins* \n\n\n'
                    embed.set_image(url=currentUser.avatar.url)

            embed.add_field(name='\u200b', value=result, inline=True)
            await interaction.response.send_message(embed=embed)
        else:
            if userName[-1] == 's':
                embed.add_field(name=f'{user.name}\' simps', value='\u200b', inline=False)
            else:
                embed.add_field(name=f'{user.name}\'s simps', value='\u200b', inline=False)
            embed.add_field(name='\u200b', value=f'{user.mention} has no simps', inline=False)
            await interaction.response.send_message(embed=embed)

        return


async def setup(bot):
    await bot.add_cog(Simps(bot), guilds=config.guildList)