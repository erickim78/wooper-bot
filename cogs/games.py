# Dependencies
import random
from threading import Timer
import numpy
import time
import schedule
import threading
from typing import List

# File Imports
import config
import data
import main

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

        self.ozRunTime = 50
        #DB Connection
        self.miscConnection = main.miscConnection
        self.miscCursor = main.miscConnection.cursor()
        self.checkRingTable()

    class ShopButtons(discord.ui.View):
        def __init__(self, parent, *, timeout=90):
            super().__init__(timeout=timeout)
            self.parent = parent

        @discord.ui.button(label="1", style=discord.ButtonStyle.primary)
        async def buttonOne(self, interaction: discord.Interaction, button:discord.ui.Button):
            currentUser = interaction.user

            self.parent.miscCursor.execute(f'SELECT * FROM \'ringTable\' WHERE userid = \'{currentUser.id}\' AND itemname = \'Broken Box Piece x5\' AND itemattribute != \'0\'')
            resultTable = self.parent.miscCursor.fetchall()
            boxPieces = 0
            for row in resultTable:
                boxPieces += int(row[2])

            imgURL = "https://static.wikia.nocookie.net/maplestory/images/b/b1/Use_Hidden_Ring_Box.png/revision/latest?cb=20210914225553"
            cost = 10
            if boxPieces < cost:
                embed=discord.Embed(title="Whooper's Ring Box", description=f'{currentUser.mention} you have {boxPieces} pieces.', color=0xf1d3ed)
                embed.set_thumbnail(url=imgURL)
                embed.add_field(name="Not enough box pieces.", value='\u200b', inline=False)
                embed.add_field(name="Pieces needed:", value=cost-boxPieces, inline=False)
            else:
                updateCursor = self.parent.miscConnection.cursor()
                for row in resultTable:
                    currentPieces = int(row[2])
                    cost = cost-currentPieces
                    if cost > 0:
                        # update row with 0
                        updateCursor.execute(f'UPDATE \'ringTable\' SET itemattribute = \'0\' WHERE userid = \'{currentUser.id}\' AND itemname = \'Broken Box Piece x5\' AND timestamp = \'{row[3]}\'')
                    else:
                        # update row with abs value of remaining cost and exit
                        updateCursor.execute(f'UPDATE \'ringTable\' SET itemattribute = \'{abs(cost)}\' WHERE userid = \'{currentUser.id}\' AND itemname = \'Broken Box Piece x5\' AND timestamp = \'{row[3]}\'')
                        break
                self.parent.miscConnection.commit()

                reward = numpy.random.choice(data.hiddenBox, p=data.hiddenRingOdds)
                rewardURL = data.rewardLinks[reward]
                level = numpy.random.choice(data.ringLevels, p=data.ringLevelOdds)
                self.parent.miscCursor.execute(f'INSERT INTO \'ringTable\' (userid, itemname, itemattribute, timestamp) VALUES (\'{currentUser.id}\',\'{reward}\',\'{level}\', datetime(\'now\'))')
                self.parent.miscConnection.commit()

                embed=discord.Embed(title="Whooper's Ring Box", description=f'Redeemed by {currentUser.mention}.', color=0xf1d3ed)
                embed.set_thumbnail(url=imgURL)
                embed.add_field(name=reward, value=level, inline=False)
                embed.set_image(url=rewardURL)
                embed.set_footer(text=f'Remaining box pieces: {boxPieces-10}')
            await interaction.response.send_message(embed=embed)

        @discord.ui.button(label="2", style=discord.ButtonStyle.primary)
        async def buttonTwo(self, interaction: discord.Interaction, button:discord.ui.Button):
            currentUser = interaction.user
            
            self.parent.miscCursor.execute(f'SELECT * FROM \'ringTable\' WHERE userid = \'{currentUser.id}\' AND itemname = \'Broken Box Piece x5\' AND itemattribute != \'0\'')
            resultTable = self.parent.miscCursor.fetchall()
            boxPieces = 0
            for row in resultTable:
                boxPieces += int(row[2])

            cost = 100
            
            imgURL = "https://static.wikia.nocookie.net/maplestory/images/b/ba/Use_Shiny_Ring_Box.png/revision/latest?cb=20210914225555"
            if boxPieces < cost:
                embed=discord.Embed(title="Whooper's Shiny Ring Box", description=f'{currentUser.mention} you have {boxPieces} pieces.', color=0xf1d3ed)
                embed.set_thumbnail(url=imgURL)
                embed.add_field(name="Not enough box pieces.", value='\u200b', inline=False)
                embed.add_field(name="Pieces needed:", value=cost-boxPieces, inline=False)
            else:
                updateCursor = self.parent.miscConnection.cursor()
                for row in resultTable:
                    currentPieces = int(row[2])
                    cost = cost-currentPieces
                    if cost > 0:
                        # update row with 0
                        updateCursor.execute(f'UPDATE \'ringTable\' SET itemattribute = \'0\' WHERE userid = \'{currentUser.id}\' AND itemname = \'Broken Box Piece x5\' AND timestamp = \'{row[3]}\'')
                    else:
                        # update row with abs value of remaining cost and exit
                        updateCursor.execute(f'UPDATE \'ringTable\' SET itemattribute = \'{abs(cost)}\' WHERE userid = \'{currentUser.id}\' AND itemname = \'Broken Box Piece x5\' AND timestamp = \'{row[3]}\'')
                        break
                self.parent.miscConnection.commit()

                reward = numpy.random.choice(data.shinyBox, p=data.shinyRingOdds)
                rewardURL = data.rewardLinks[reward]
                level = numpy.random.choice(data.shinyBoxLevels, p=data.shinyBoxlevelOdds)
                self.parent.miscCursor.execute(f'INSERT INTO \'ringTable\' (userid, itemname, itemattribute, timestamp) VALUES (\'{currentUser.id}\',\'{reward}\',\'{level}\', datetime(\'now\'))')
                self.parent.miscConnection.commit()

                embed=discord.Embed(title="Whooper's Shiny Ring Box", description=f'Redeemed by {currentUser.mention}.', color=0xf1d3ed)
                embed.set_thumbnail(url=imgURL)
                embed.add_field(name=reward, value=level, inline=False)
                embed.set_image(url=rewardURL)
                embed.set_footer(text=f'Remaining box pieces: {boxPieces-100}')
            await interaction.response.send_message(embed=embed)

        @discord.ui.button(label="3", style=discord.ButtonStyle.secondary)
        async def buttonThree(self, interaction: discord.Interaction, button:discord.ui.Button):
            embed=discord.Embed(color=0xf1d3ed)
            imgURL = "https://static.wikia.nocookie.net/maplestory/images/3/36/Use_Broken_Box_Piece.png/revision/latest?cb=20210910011106"
            embed.set_thumbnail(url=imgURL)
            embed.add_field(name="Tower of Oz", value=f'Prize Redemption for {interaction.user.mention}', inline=False)
            embed.add_field(name="Whoomper's Ring Box", value= '\u200b', inline=False)
            embed.add_field(name="Ring Name Placeholder", value= 'Ring Level Placeholder', inline=False)
            embed.set_footer(text=f'Remaining box pieces: {0}')
            await interaction.response.send_message(embed=embed)

        @discord.ui.button(label="4", style=discord.ButtonStyle.secondary)
        async def buttonFour(self, interaction: discord.Interaction, button:discord.ui.Button):
            embed=discord.Embed(color=0xf1d3ed)
            imgURL = "https://static.wikia.nocookie.net/maplestory/images/3/36/Use_Broken_Box_Piece.png/revision/latest?cb=20210910011106"
            embed.set_thumbnail(url=imgURL)
            embed.add_field(name="Tower of Oz", value=f'Prize Redemption for {interaction.user.mention}', inline=False)
            embed.add_field(name="Whoomper's Ring Box", value= '\u200b', inline=False)
            embed.add_field(name="Ring Name Placeholder", value= 'Ring Level Placeholder', inline=False)
            embed.set_footer(text=f'Remaining box pieces: {0}')
            await interaction.response.send_message(embed=embed)

        @discord.ui.button(label="5", style=discord.ButtonStyle.secondary)
        async def buttonFive(self, interaction: discord.Interaction, button:discord.ui.Button):
            embed=discord.Embed(color=0xf1d3ed)
            imgURL = "https://static.wikia.nocookie.net/maplestory/images/3/36/Use_Broken_Box_Piece.png/revision/latest?cb=20210910011106"
            embed.set_thumbnail(url=imgURL)
            embed.add_field(name="Tower of Oz", value=f'Prize Redemption for {interaction.user.mention}', inline=False)
            embed.add_field(name="Whoomper's Ring Box", value= '\u200b', inline=False)
            embed.add_field(name="Ring Name Placeholder", value= 'Ring Level Placeholder', inline=False)
            embed.set_footer(text=f'Remaining box pieces: {0}')
            await interaction.response.send_message(embed=embed)


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
            del self.usersRunning[memberId]
        else:
            print("Should never reach this statement, check remaining runs before starting a run")
            return
        print(f'User {self.bot.get_user(memberId)} completed an Oz run. Runs Remaining: {self.runsRemaining[memberId]}.')
        
    # Oz Run Starter
    def startOzRun(self, memberId):
        print(f'User {self.bot.get_user(memberId)} is starting an Oz run...')
        self.usersRunning[memberId] = (Timer(self.ozRunTime*60, self.ozRun, [memberId]), time.time())
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
                self.startOzRun(user)
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

    def checkRingTable(self):
        self.miscCursor.execute(f'''SELECT count(name) FROM sqlite_master WHERE type='table' AND name = 'ringTable' ''')
        if self.miscCursor.fetchone()[0] != 1:
            self.miscCursor.execute(f'''CREATE TABLE 'ringTable' (userid TEXT, itemname TEXT, itemattribute TEXT, timestamp datetime)''')
            return False
        return True

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

    @app_commands.command(name='oz', description='View your oz stats')
    async def oz(self, interaction: discord.Interaction, user: discord.User = None) -> None:
        if user is None:
            user = interaction.user

        imgURL = "https://i.imgur.com/dxPvMN8.gif"
        embed=discord.Embed(title="Tower of Oz", description=f'{user.mention}\'s Oz Stats', color=0xf1d3ed)
        embed.set_thumbnail(url=imgURL)
        timeString = "-"

        self.miscCursor.execute(f'SELECT * FROM \'ringTable\' WHERE userid = \'{user.id}\'')
        resultTable = self.miscCursor.fetchall()
        boxesOpened = len(resultTable)
        boxPieces = 0
        for row in resultTable:
            if row [1] == 'Broken Box Piece x5':
                boxPieces += int(row[2])
        
        if user.id not in self.usersRunning or self.usersRunning[user.id] is None:
            timeString = "Not Running"
        else:
            now = time.time()
            start = self.usersRunning[user.id][1]
            timeLeft = max(round((self.ozRunTime*60-now+start)/60), 1)
            timeString = f'{timeLeft} minutes remaining.'

        if user.id not in self.runsRemaining:
            embed.add_field(name="Current Status", value=timeString, inline=False)
            embed.add_field(name="Runs Left", value='5', inline=True)
            embed.add_field(name="Boxes", value='0', inline=True)
            embed.add_field(name="Box Pieces", value=boxPieces, inline=True)
            embed.add_field(name="Boxes Opened", value=boxesOpened, inline=True)
        else:
            embed.add_field(name="Current Status", value=timeString, inline=False)
            embed.add_field(name="Runs Left", value=self.runsRemaining[user.id], inline=True)
            embed.add_field(name="Boxes", value=self.boxes[user.id], inline=True)
            embed.add_field(name="Box Pieces", value=boxPieces, inline=True)
            embed.add_field(name="Boxes Opened", value=boxesOpened, inline=True)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='openbox', description='Open a Tower of Oz Ring Box (if you have one)')
    async def openbox(self, interaction: discord.Interaction) -> None:
        currentUser = interaction.user
        imgURL = "https://i.imgur.com/lu5MIE1.png"
        embed=discord.Embed(title="Tower of Oz", description=f'Box Opening for {currentUser.mention}', color=0xf1d3ed)
        embed.set_thumbnail(url=imgURL)
        if currentUser.id not in self.boxes:
            embed.add_field(name="You have no Ring Boxes.", value='\u200b', inline=False)
            embed.add_field(name="Runs Left", value='5', inline=False)
        elif self.boxes[currentUser.id] < 1:
            embed.add_field(name="You have no Ring Boxes.", value='\u200b', inline=False)
            embed.add_field(name="Runs Left", value=self.runsRemaining[currentUser.id], inline=False)
        else:
            self.decrementBoxes(currentUser.id)
            reward = numpy.random.choice(data.rings, p=data.ringOdds)
            rewardURL = data.rewardLinks[reward]
            level = '\u200b'
            attribute = ""
            if reward in data.nonRings:
                if reward == 'Broken Box Piece x5':
                    attribute = '5'
                elif reward == 'Oz Point Pouch x5':
                    attribute = '5'
                elif reward == '2x EXP Coupon (15 Minute) x3':
                    attribute = '3'
                else:
                    print("In OpenBox Error, should not reach this branch")
            else:
                level = numpy.random.choice(data.ringLevels, p=data.ringLevelOdds)
                attribute = level
            self.miscCursor.execute(f'INSERT INTO \'ringTable\' (userid, itemname, itemattribute, timestamp) VALUES (\'{currentUser.id}\',\'{reward}\',\'{attribute}\', datetime(\'now\'))')
            self.miscConnection.commit()

            embed.add_field(name=reward, value=level, inline=False)
            embed.set_image(url=rewardURL)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='ozhistory', description='View someone\'s most recent rewards')
    async def ozhistory(self, interaction: discord.Interaction, user: discord.User = None):
        if user is None:
            user = interaction.user

        imgURL = "https://i.imgur.com/dxPvMN8.gif"
        embed=discord.Embed(title="Tower of Oz", description=f'{user.mention}\'s Recent Rewards', color=0xf1d3ed)
        embed.set_thumbnail(url=imgURL)

        self.miscCursor.execute(f'SELECT * FROM \'ringTable\' WHERE userid = \'{user.id}\' ORDER BY timestamp DESC')
        resultTable = self.miscCursor.fetchall()
        if len(resultTable) > 0:
            for x in range(min(10, len(resultTable))):
                currentRow = resultTable[x]
                if currentRow[1] in data.nonRings:
                    embed.add_field(name=f'**{x+1}) {currentRow[1]}**', value='\u200b', inline=False)
                else:
                    embed.add_field(name=f'**{x+1}) {currentRow[1]}** {currentRow[2]}', value='\u200b', inline=False)
        else:
            embed.add_field(name='\u200b', value=f'-', inline=False)
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='shop', description='Opens Whooper\'s Box Piece Shop (Active for 90 seconds)')
    async def shop(self, interaction: discord.Interaction):
        user = interaction.user
        self.currentShopInteraction = interaction

        imgURL = "https://static.wikia.nocookie.net/maplestory/images/3/36/Use_Broken_Box_Piece.png/revision/latest?cb=20210910011106"
        embed=discord.Embed(title="Tower of Oz", description=f'Whoomper Shop', color=0xf1d3ed)
        embed.set_thumbnail(url=imgURL)

        embed.add_field(name=f'Select your prize.', value='\u200b', inline=False)

        embed.add_field(name=f'**1.** Whoomper\'s Ring Box', value='10x Box Pieces', inline=False)
        embed.add_field(name=f'**2.** Whoomper\'s Shiny Ring Box', value='100x Box Pieces', inline=False)
        embed.add_field(name=f'**3.** Hand Pics', value = 'Placeholder', inline=False)
        embed.add_field(name=f'**4.** Feet Pics', value = 'Placeholder', inline=False)
        embed.add_field(name=f'**5.** ???', value = 'Placeholder', inline=False)

        await interaction.response.send_message(embed=embed, view=self.ShopButtons(self))

    @app_commands.command(name='givebox', description='TESTING ONLY')
    async def givebox(self, interaction: discord.Interaction, user: discord.User = None, num: int = 1):
        if user is None:
            user = interaction.user

        imgURL = "https://i.imgur.com/dxPvMN8.gif"
        embed=discord.Embed(title="Tower of Oz", description=f'\u200b', color=0xf1d3ed)
        embed.set_thumbnail(url=imgURL)

        if interaction.user.guild_permissions.administrator or interaction.user.id == 125114599249936384:
            if user.id in self.boxes:
                self.boxes[user.id] += num
            else:
                self.boxes[user.id] = num
            embed.add_field(name='\u200b', value=f'Gave {user.mention} {num} boxes.', inline=False)
        else:
            embed.add_field(name='\u200b', value=f'You are not authorized to give boxes.', inline=False)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='givepieces', description='TESTING ONLY')
    async def givepieces(self, interaction: discord.Interaction, user: discord.User = None, num: int = 5):
        if user is None:
            user = interaction.user

        imgURL = "https://static.wikia.nocookie.net/maplestory/images/3/36/Use_Broken_Box_Piece.png/revision/latest?cb=20210910011106"
        if interaction.user.id == 125114599249936384:
            self.miscCursor.execute(f'INSERT INTO \'ringTable\' (userid, itemname, itemattribute, timestamp) VALUES (\'{user.id}\',\'Broken Box Piece x5\',\'{num}\', datetime(\'now\'))')
            self.miscConnection.commit()

            self.miscCursor.execute(f'SELECT * FROM \'ringTable\' WHERE userid = \'{user.id}\' AND itemname = \'Broken Box Piece x5\'')
            resultTable = self.miscCursor.fetchall()
            boxPieces = 0
            for row in resultTable:
                boxPieces += int(row[2])

            
            embed=discord.Embed(title="Box Piece Dispenser", description=f'{user.mention} you now have {boxPieces} pieces.', color=0xf1d3ed)
            embed.set_thumbnail(url=imgURL)
        else:
            embed=discord.Embed(title="Box Piece Dispenser", description=f'{interaction.user} is not authorized to give pieces.', color=0xf1d3ed)
            embed.set_thumbnail(url=imgURL)

        await interaction.response.send_message(embed=embed)

    async def ozleaderboard_autocomplete(self, interaction: discord.Interaction, current: str,) -> List[app_commands.Choice[str]]:
        choices = ['Ring of Restraint', 'Weapon Jump']
        return [
            app_commands.Choice(name=choice, value=choice)
            for choice in choices if current.lower() in choice.lower()
        ]

    @app_commands.command(name='ozleaderboard', description='Display usable rings')
    @app_commands.autocomplete(choices=ozleaderboard_autocomplete)
    async def ozleaderboard(self, interaction: discord.Interaction, ringName: app_commands.Choice[str], ringLevel: str = 4):
        if user is None:
            user = interaction.user

        imgURL = "https://i.imgur.com/dxPvMN8.gif"
        embed = discord.Embed(title="Tower of Oz Leaderboard", description=f'for {ringName} Level {ringLevel}')
        embed.set_thumbnail(url=imgURL)
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Games(bot), guilds=config.guildList)