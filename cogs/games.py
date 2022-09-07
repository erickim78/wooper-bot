# Dependencies
import random
from threading import Timer
import numpy
import time
import schedule
import threading

# File Imports
import config
import data

# Discord
import discord
from discord.ext import commands
from discord import app_commands


class Games(commands.Cog):
    def __init__(self, bot):
        print(f'games.cog init')
        self.bot = bot
        self.usersRunning = {}
        self.runsRemaining = {}
        self.boxes = {} # temporary(?)

    # Oz Run Handler for branching
    def ozRun(self, memberId):
        if memberId not in self.runsRemaining:
            self.runsRemaining[memberId] = 4
            self.incrementBoxes(memberId)
            self.startOzRun(memberId)
        elif self.runsRemaining[memberId] > 1:
            self.runsRemaining[memberId] -= 1
            self.incrementBoxes(memberId)
            self.startOzRun(memberId)
        elif self.runsRemaining[memberId] == 1:
            self.runsRemaining[memberId] -= 1
            self.incrementBoxes(memberId)
        else:
            print("Should never reach this statement, check remaining runs before starting a run")
            return
        print(f'User {self.bot.get_user(memberId)} completed an Oz run. Runs Remaining: {self.runsRemaining[memberId]}.')
        
    # Oz Run Starter
    def startOzRun(self, memberId):
        print(f'User {self.bot.get_user(memberId)} is starting an Oz run...')
        self.usersRunning[memberId] = (Timer(3600, self.ozRun, [memberId]), time.time())
        self.usersRunning[memberId][0].start()
        print(f'User {self.bot.get_user(memberId)} started an Oz run.')

    def quitOzRun(self, memberId):
        if self.usersRunning[memberId] is None:
            print('BUG: Users running should not be None')
            return
        self.usersRunning[memberId][0].cancel()
        self.usersRunning[memberId] = None
        print(f'User {self.bot.get_user(memberId)} abandoned an Oz run.')

    # Box Incrementer
    def incrementBoxes(self, memberId):
        if memberId not in self.boxes:
            self.boxes[memberId] = 1
        else:
            self.boxes[memberId] += 1
        print(f'User {self.bot.get_user(memberId)} has received an oz box. Total boxes: {self.boxes[memberId]}.')

    def decrementBoxes(self, memberId):
        if memberId not in self.boxes:
            print('BUG: Member id should exist in boxes')
        else:
            self.boxes[memberId] -= 1
            if self.boxes[memberId] < 0:
                print('BUG: Member should not be allowed to decrement box below 0')
                self.boxes[memberId] = 0

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
        print("RESETTING OZ RUNS:")
        for user in self.runsRemaining:
            if user in self.usersRunning and self.usersRunning[user] is not None:
                self.runsRemaining[user] = 6
            else:
                self.runsRemaining[user] = 5
        print("============================================================")
    
    # Initialize currently connected users
    def initUsersRunning(self):
        for guild in self.bot.guilds:
            currentChannels = guild.voice_channels
            for channel in currentChannels:
                if channel == guild.afk_channel:
                    continue
                else:
                    members = channel.members
                    for currentMember in members:
                        self.startOzRun(currentMember.id)

    # On Ready
    @commands.Cog.listener()
    async def on_ready(self):
        self.initUsersRunning()
        print("Scheduling Oz Run Resets")
        schedule.every().day.at("23:59").do(self.autoUpdateTimes)
        self.stop_run_continuously = self.run_continuously()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        currentId = member.id
        if after.channel == None:
            if before.afk != True:
                # print(f'User {self.connectedUsers} disconnected.')
                self.quitOzRun(currentId)
        elif before.channel == None and after.channel != None:
            if after.afk != True:
                # print(f'User {self.connectedUsers} connected.')
                self.startOzRun(currentId)
        else:
            if before.afk == True and after.afk == False:
                # print(f'User {self.connectedUsers} returned from afk.')
                self.startOzRun(currentId)
            elif before.afk == False and after.afk == True:
                # print(f'User {self.connectedUsers} went afk.')
                self.quitOzRun(currentId)
            else:
                # print(f'User {self.connectedUsers} made a non-connection related voice status update.')
                return
        return

    @app_commands.command(name='conch', description='Ask the Magic Conch for an answer.')
    async def conch(self, interaction: discord.Interaction, question: str) -> None:
        rand = random.randint(0,17)
        imgURL = "https://i.imgur.com/RLsojmN.jpg"
        embed=discord.Embed(color=0xf1d3ed)
        embed.set_image( url = imgURL )
        embed.add_field(name="Magic Conch", value=question, inline=False)
        embed.add_field(name=data.conchResponses[rand], value='\u200b', inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='ozstatus', description='View your oz stats')
    async def ozstatus(self, interaction: discord.Interaction, user: discord.User = None) -> None:
        if user is None:
            user = interaction.user

        imgURL = "https://i.imgur.com/dxPvMN8.gif"
        embed=discord.Embed(title="Tower of Oz", description=f'Welcome {user.mention}', color=0xf1d3ed)
        embed.set_thumbnail(url=imgURL)
        timmeString = "-"
        if user.id not in self.usersRunning or self.usersRunning[user.id] is None:
            timeString = "Not Running"
        else:
            now = time.time()
            start = self.usersRunning[user.id][1]
            timeLeft = max(round(60-(now-start)/60), 1)
            timeString = f'{timeLeft} minutes remaining.'

        if user.id not in self.runsRemaining:
            embed.add_field(name="Current Run", value=timeString, inline=True)
            embed.add_field(name="Boxes", value='0', inline=True)
            embed.add_field(name="Runs Left", value='5', inline=True)
            embed.add_field(name="Completed Runs", value='Placeholder', inline=True)
        else:
            embed.add_field(name="Current Run", value=timeString, inline=True)
            embed.add_field(name="Boxes", value=self.boxes[user.id], inline=True)
            embed.add_field(name="Runs Left", value=self.runsRemaining[user.id], inline=True)
            embed.add_field(name="Completed Runs", value='Placeholder', inline=True)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='oz', description='Open a Tower of Oz Ring Box (if you have one)')
    async def oz(self, interaction: discord.Interaction) -> None:
        currentUser = interaction.user
        imgURL = "https://i.imgur.com/lu5MIE1.png"
        embed=discord.Embed(title="Tower of Oz", description=f'Box Opening for {currentUser.mention}', color=0xf1d3ed)
        embed.set_thumbnail(url=imgURL)
        if currentUser.id not in self.boxes:
            embed.add_field(name="You have no Ring Boxes.", value='\u200b', inline=True)
            embed.add_field(name="Runs Left", value='5', inline=True)
        elif self.boxes[currentUser.id] < 1:
            embed.add_field(name="You have no Ring Boxes.", value='\u200b', inline=True)
            embed.add_field(name="Runs Left", value=self.runsRemaining[currentUser.id], inline=True)
        else:
            self.decrementBoxes(currentUser.id)
            reward = numpy.random.choice(data.rings, p=data.ringOdds)
            rewardURL = data.rewardLinks[reward]
            if reward in data.nonRings:
                embed.add_field(name=reward, value='\u200b', inline=False)
            else:
                level = numpy.random.choice(data.ringLevels, p=data.ringLevelOdds)
                embed.add_field(name=reward, value=level, inline=False)
            embed.set_image(url=rewardURL)
            #embed.add_field(name='\u200b', value='**Boxes Left**', inline=True)
            #embed.add_field(name=self.boxes[currentUser.id], value='**Runs Left**', inline=True)
            #embed.add_field(name=self.runsRemaining[currentUser.id], value='\u200b', inline=True)
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Games(bot), guilds=config.guildList)