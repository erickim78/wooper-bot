# Dependencies
from sqlite3 import Cursor
import time
import datetime
from datetime import timedelta
from profanity_check import predict
import schedule
import threading

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

        # Simps DB
        self.connection = main.connection
        self.cursor = main.connection.cursor()

        # Time Data
        self.timeSequenceConn = main.timeSequenceConn
        self.timeSequenceCursor = main.timeSequenceConn.cursor()

        # Message Analysis
        self.messageConn = main.messageAnalysis
        self.messageCursor = main.messageAnalysis.cursor()
        
        # Init Connected User List
        self.connectedUsers = {}
        self.timeTracker = {}

        # Lock
        self.timeLock = threading.Lock()

    def initConnectedUsers(self):
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
                        self.timeTracker[currentMember.id] = updateTime
    
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
        if self.cursor.fetchone()[0] != 1:
            self.cursor.execute(f'''CREATE TABLE '{tableName}' (id TEXT, count DECIMAL (38,4), reactions TEXT, PRIMARY KEY (id))''')
            return False
        return True

    def checkTimeTable(self, tableName):
        self.timeSequenceCursor.execute(f''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name = '{tableName}' ''')
        if self.timeSequenceCursor.fetchone()[0] != 1:
            self.timeSequenceCursor.execute(f''' CREATE TABLE '{tableName}' (d date, count DECIMAL(38,4), PRIMARY KEY (d))''')
            return False
        return True

    def checkMessageTable(self, tableName):
        self.messageCursor.execute(f''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name = '{tableName}' ''')
        if self.messageCursor.fetchone()[0] != 1:
            self.messageCursor.execute(f''' CREATE TABLE '{tableName}' (k INT, messages INT, swears INT, PRIMARY KEY (k))''')
            return False
        return True

    def addTime(self, userId, timeToAdd):
        self.checkTimeTable(userId)
        self.timeSequenceCursor.execute(f'INSERT INTO \'{str(userId)}\' (d, count) VALUES (date(\'now\'), {timeToAdd}) ON CONFLICT (d) DO UPDATE SET count = count + {timeToAdd}')
        self.timeSequenceConn.commit()
        print(f'In Time Sequencing Database, added {round(timeToAdd/3600,2)} hours to user {self.bot.get_user(userId).name}')
        return

    def handleConnect(self, userId):
        self.updateTimes()
        self.connectedUsers[userId] = time.time()
        self.timeTracker[userId] = time.time()
        return
        
    def handleDisconnect(self, userId):
        self.updateTimes()
        del self.connectedUsers[userId]
        self.updateTimeOnDisconnect(userId)
        return

    def updateTimeOnDisconnect(self, userId):
        if self.timeTracker[userId] is not None: # Should never be None but just in case of double access conflict
            with self.timeLock:
                timeConnected = time.time() - self.timeTracker[userId]
                self.addTime(userId, timeConnected)
                del self.timeTracker[userId]

    def updateTimeWithoutDisconnect(self, userId):
        if self.timeTracker[userId] is not None:
            currentTime = time.time()
            with self.timeLock:
                timeConnected = currentTime - self.timeTracker[userId]
                self.addTime(userId, timeConnected)
                self.timeTracker[userId] = currentTime
    
    def run_continuously(self, interval = 5):
        cease_continuous_run = threading.Event()
        class ScheduleThread(threading.Thread):
            def run(cls):
                while not cease_continuous_run.is_set():
                    schedule.run_pending()
                    time.sleep(interval)
        continuous_thread = ScheduleThread()
        continuous_thread.start()
        return cease_continuous_run

    def autoUpdateTimes(self):
        print("AUTOMATIC DAILY UPDATE REPORT:")
        for user in self.timeTracker:
            self.updateTimeWithoutDisconnect(user)
        print("============================================================")

    # On Ready
    @commands.Cog.listener()
    async def on_ready(self):
        self.initConnectedUsers()
        print("Scheduling Auto Update")
        schedule.every().day.at("23:59").do(self.autoUpdateTimes)
        self.stop_run_continuously = self.run_continuously()
        print("Initially connected users: ", self.connectedUsers)

    @commands.Cog.listener()
    async def on_message(self, message):
        currentId = message.author.id
        swearCount = predict([message.content])
        print(swearCount[0])
        self.checkMessageTable(currentId)
        self.messageCursor.execute(f'INSERT INTO \'{str(currentId)}\' (k, messages, swears) VALUES ({0}, {1}, {swearCount[0]}) ON CONFLICT (k) DO UPDATE SET messages = messages + 1, swears = swears + {swearCount[0]}')
        self.messageConn.commit()

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        simp = payload.user_id
        simped = message.author.id
        print(f'User {self.bot.get_user(simp).name} reacted with {payload.emoji.name} to user {self.bot.get_user(simped).name}.')

        self.checkTable(simped)
        self.cursor.execute(f'INSERT INTO \'{str(simped)}\' (id, count, reactions) VALUES ({str(simp)}, {0}, {1}) ON CONFLICT (id) DO UPDATE SET reactions = reactions + 1')
        self.connection.commit()
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if after.channel == None:
            if before.afk != True:
                print("disconnect")
                self.handleDisconnect(member.id)
        elif before.channel == None and after.channel != None:
            if after.afk != True:
                print("connect")
                self.handleConnect(member.id)
        else:
            if before.afk == True and after.afk == False:
                print("afk to reg")
                self.handleConnect(member.id)
            elif before.afk == False and after.afk == True:
                print("reg to afk")
                self.handleDisconnect(member.id)
            else:
                print("Non-Connection related voice state change")
        print("\nOn voice status update: ", self.connectedUsers)
        return

    @app_commands.command(name="simps", description='Simp Leaderboard')
    async def simps(self, interaction: discord.Interaction, user: discord.User = None) -> None:
        if user is None:
            user = interaction.user

        # Build Embed Common Fields
        embed = discord.Embed(color=0xf1d3ed)
        embed.set_thumbnail(url=user.avatar.url) 
        userName = user.name

        # Build Simps String
        self.cursor.execute(f'''SELECT count(name) FROM sqlite_master WHERE type='table' AND name = '{user.id}' ''')
        if self.cursor.fetchone()[0] == 1:
            self.cursor.execute(f'SELECT * FROM \'{str(user.id)}\' ORDER BY count DESC, reactions DESC')
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
                    result += f'{i+1}) {currentUser.mention}, **{round((float(currentTime)/referenceTime)*100,2)}% Attendance** \n*Time Together: {round(currentTime//3600)} hrs, {round((currentTime-3600*(currentTime//3600))//60)} mins*\n\n'
                else:
                    result += f'**{i+1}) {currentUser.mention},  {round((float(currentTime)/referenceTime)*100,2)}% Attendance** \n*Time Together: {round(currentTime//3600)} hrs, {round((currentTime-3600*(currentTime//3600))//60)} mins* \n\n\n'
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

    @app_commands.command(name="stats", description='Server Stats')
    async def stats(self, interaction: discord.Interaction, user: discord.User = None) -> None:
        if user is None:
            user = interaction.user

        # Build Embed Common Fields
        embed = discord.Embed(color=0xf1d3ed)
        embed.set_thumbnail(url=user.avatar.url)

        self.cursor.execute(f'''SELECT count(name) FROM sqlite_master WHERE type='table' AND name = '{user.id}' ''')
        if self.cursor.fetchone()[0] == 1:
            self.cursor.execute(f'SELECT * FROM \'{str(user.id)}\' ORDER BY count DESC, reactions DESC')
            simpList = self.cursor.fetchall()

            referenceTime = 0
            delIndex = 0
            reactions = 0
            for x in range(len(simpList)):
                if int(simpList[x][0]) == user.id:
                    delIndex = x
                    referenceTime = float(simpList[x][1])
                else:
                    reactions += int(simpList[x][2])
            del simpList[delIndex]

            self.checkTimeTable(user.id)
            self.timeSequenceCursor.execute(f'''SELECT count(name) FROM sqlite_master WHERE type='table' AND name = '{user.id}' ''')
            self.timeSequenceCursor.execute(f'SELECT * FROM \'{str(user.id)}\' WHERE d = date(\'now\')')
            currentSample = self.timeSequenceCursor.fetchall()
            todays = 0
            for item in currentSample:
                todays += float(item[1])
            todays = round(sum3days/3600,2)

            self.timeSequenceCursor.execute(f'''SELECT count(name) FROM sqlite_master WHERE type='table' AND name = '{user.id}' ''')
            self.timeSequenceCursor.execute(f'SELECT * FROM \'{str(user.id)}\' WHERE d BETWEEN date(\'now\', \'-2 day\') and date(\'now\')')
            currentSample = self.timeSequenceCursor.fetchall()
            sum3days = 0
            for item in currentSample:
                sum3days += float(item[1])
            avg3days = round(sum3days/10800,2)
            sum3days = round(sum3days/10800,2)

            self.timeSequenceCursor.execute(f'SELECT * FROM \'{str(user.id)}\' WHERE d BETWEEN date(\'now\', \'-6 day\') and date(\'now\', \'-1 day\')')
            currentSample = self.timeSequenceCursor.fetchall()
            sum7days = 0
            for item in currentSample:
                sum7days += float(item[1])
            avg7days = round(sum3days/25200,2)
            sum7days = round(sum7days/10800,2)

            self.timeSequenceCursor.execute(f'SELECT * FROM \'{str(user.id)}\' WHERE d BETWEEN date(\'now\', \'-29 day\') and date(\'now\', \'-1 day\')')
            currentSample = self.timeSequenceCursor.fetchall()
            sum30days = 0
            for item in currentSample:
                sum30days += float(item[1])
            avg30days = round(sum3days/108000,2)
            sum30days = round(sum30days/10800,2)

            totalSwears = "-"
            avgSwears = "-"
            messagesSent = 0
            self.checkMessageTable(user.id)
            self.messageCursor.execute(f'SELECT * FROM \'{str(user.id)}\' WHERE k = 0')
            currentSample = self.messageCursor.fetchall()
            for item in currentSample:
                messagesSent = int(currentSample[0][1])
                totalSwears = int(currentSample[0][2])
                avgSwears = round(totalSwears/messagesSent,2)

            # Build Embed
            embed.add_field(name=f'Stats for **{user.name}**', value='\u200b', inline=False)
            embed.add_field(name='Biggest Simp', value=f'{self.bot.get_user(int(simpList[0][0])).mention}', inline=True)
            embed.add_field(name='Messages Sent', value=f'{messagesSent}', inline=True)
            embed.add_field(name='Reactions Farmed', value=f'{reactions}', inline=True)
            embed.add_field(name='Profanities Used', value=f'{totalSwears}', inline=True)
            embed.add_field(name='Reactions Per Message', value=f'{round(reactions/messagesSent,2)}', inline=True)
            embed.add_field(name='Profanites Per Message', value=f'{avgSwears}', inline=True)
            #embed.add_field(name='\u200b', value='\u200b', inline=False)
            embed.add_field(name='\u200b', value='**Total Time On**', inline=False)
            embed.add_field(name='Today', value=f'{todays} hrs', inline=True)
            embed.add_field(name='Last 3 Days', value=f'{sum3days} hrs', inline=True)
            embed.add_field(name='Last 7 Days', value=f'{sum7days} hrs', inline=True)
            embed.add_field(name='Last 30 Days', value=f'{sum30days} hrs', inline=True)
            embed.add_field(name='All Time', value=f'{round(referenceTime/3600,2)} hrs', inline=True)
            #embed.add_field(name='\u200b', value='\u200b', inline=False)
            embed.add_field(name='\u200b', value='**Average Time Per Day**', inline=False)
            embed.add_field(name='Last 3 Days', value=f'{avg3days} hrs', inline=True)
            embed.add_field(name='Last 7 Days', value=f'{avg7days} hrs', inline=True)
            embed.add_field(name='Last 30 Days', value=f'{avg30days} hrs', inline=True)
            # embed.add_field(name='All Time', value=f'{round(referenceTime/3600,2)} hrs', inline=True)
        else:
            embed.add_field(name=f'Stats for **{user.name}**', value='\u200b', inline=False)
            embed.add_field(name='\u200b', value=f'No stats for {user.mention}', inline=False)
            await interaction.response.send_message(embed=embed)
            return
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Simps(bot), guilds=config.guildList)