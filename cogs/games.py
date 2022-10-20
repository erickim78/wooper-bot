# Dependencies
from curses.ascii import isdigit
from email import message
from multiprocessing import parent_process
import random
from threading import Timer
from attr import attr
import numpy
import time
import schedule
import threading
from typing import List
import pickle
import os

# File Imports
import config
import data
import main

# Discord
import discord
from discord.ext import commands
from discord import app_commands

class RPSView(discord.ui.View):
    def __init__(self, parent, originalUser, *, timeout=90):
        super().__init__(timeout=timeout)
        self.wager = 1
        self.attack = "-"
        self.parent = parent
        self.originalUser = originalUser
        self.maxWager = parent.checkBoxPieces(originalUser.id)
        self.url = "https://i.imgur.com/qf6kzdn.jpg"
        self.embed=discord.Embed(title="RPS Battle", description=f'{self.originalUser.mention} will fight Quagsire.', color=0xf1d3ed)
    
    def updateEmbed(self):
        self.embed=discord.Embed(title="RPS Battle", description=f'{self.originalUser.mention} will fight Quagsire.', color=0xf1d3ed)
        self.embed.set_thumbnail(url=self.url)
        self.embed.add_field(name=f'Wager (max {self.maxWager}):', value=f'{self.wager} box piece(s)', inline=True)
        self.embed.add_field(name="Selected Attack:", value=f'{self.attack}', inline=True)

    @discord.ui.select(placeholder='Your Attack', options = [
            discord.SelectOption(label='Flamethrower', emoji='🟥'),
            discord.SelectOption(label='Razor Leaf', emoji='🟩'),
            discord.SelectOption(label='Bubblebeam', emoji='🟦'),
        ])
    async def select(self, interaction: discord.Interaction, select):
        if interaction.user != self.originalUser:
            return

        self.attack = select.values[0]
        if self.attack == "Flamethrower":
            self.attack = "🟥 "+self.attack
        elif self.attack == "Razor Leaf":
            self.attack = "🟩 "+self.attack
        elif self.attack =="Bubblebeam":
            self.attack = "🟦 "+self.attack
        else:
            print("Error in parsing command")
        self.updateEmbed()
        await interaction.response.edit_message(embed=self.embed)

    @discord.ui.button(label='FIGHT', style=discord.ButtonStyle.success)
    async def buttonOne(self, interaction: discord.Interaction, button:discord.ui.Button):
        if interaction.user != self.originalUser:
            return

        self.stop()
        currentUser = interaction.user
        imgURL = "https://i.imgur.com/qf6kzdn.jpg"
        embed=discord.Embed(title="RPS Battle", description=f'{currentUser.mention} wagered {self.wager} box pieces.', color=0xf1d3ed)
        embed.set_thumbnail(url=imgURL)

        if self.parent.tryDeductingBoxPieces(currentUser.id, self.wager) is True:
            if self.parent.tryDeductingWhoompTickets(currentUser.id, 1) is False:
                print("REALLY BAD ERROR IN DEDUCTING TICKETS")
                return

            quagAttack = random.choice(data.attacks)
            embed.add_field(name=f'{currentUser.name}\'s attack:', value=self.attack, inline=True)
            embed.add_field(name="Quagsire used:", value=quagAttack, inline=True)
            if quagAttack == self.attack:
                self.parent.miscCursor.execute(f'INSERT INTO \'ringTable\' (userid, itemname, itemattribute, timestamp) VALUES (\'{currentUser.id}\',\'Broken Box Piece x5\',\'{self.wager}\', datetime(\'now\'))')
                embed.add_field(name="...but nothing happened", value=f'Returned {self.wager} box pieces.', inline=False)
                embed.set_image(url="https://i.imgur.com/0K1MjHZ.png")
            elif data.weakness[quagAttack] == self.attack:
                self.parent.miscCursor.execute(f'INSERT INTO \'ringTable\' (userid, itemname, itemattribute, timestamp) VALUES (\'{currentUser.id}\',\'Broken Box Piece x5\',\'{self.wager*3}\', datetime(\'now\'))')
                self.parent.miscCursor.execute(f'INSERT INTO \'gamblingTable\' (userid, game, count, timestamp) VALUES (\'{currentUser.id}\',\'rps\', {self.wager*2}, datetime(\'now\'))')
                embed.add_field(name="YOU WIN", value=f'Gained {self.wager*3} box pieces.', inline=False)
                embed.set_image(url="https://i.imgur.com/LbM4jXk.jpeg")
            else:
                embed.add_field(name="YOU LOSE", value=f'Lost {self.wager} box pieces.', inline=False)
                self.parent.miscCursor.execute(f'INSERT INTO \'gamblingTable\' (userid, game, count, timestamp) VALUES (\'{currentUser.id}\',\'rps\', {-self.wager}, datetime(\'now\'))')
                embed.set_image(url="https://i.imgur.com/tMXcy9Z.jpeg")
            self.parent.miscConnection.commit()
        else:
            embed.add_field(name="Not enough box pieces.", value=f'\u200b', inline=False)
        await interaction.response.send_message(embed=embed)

    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.danger)
    async def buttonTwo(self, interaction: discord.Interaction, button:discord.ui.Button):
        if interaction.user != self.originalUser:
            return

        self.stop()
        self.embed=discord.Embed(title="RPS Battle", description=f'{self.originalUser.mention} will fight Quagsire.', color=0xf1d3ed)
        self.embed.set_thumbnail(url=self.url)
        self.embed.add_field(name="FIGHT CANCELLED", value=f'\u200b', inline=True)
        await interaction.response.edit_message(embed=self.embed)

    @discord.ui.button(label='+1', style=discord.ButtonStyle.secondary)
    async def buttonThree(self, interaction: discord.Interaction, button:discord.ui.Button):
        if interaction.user != self.originalUser:
            return

        self.wager += 1
        if self.wager > self.maxWager:
            self.wager = self.maxWager

        self.updateEmbed()
        await interaction.response.edit_message(embed=self.embed)

    @discord.ui.button(label='-1', style=discord.ButtonStyle.secondary)
    async def buttonFour(self, interaction: discord.Interaction, button:discord.ui.Button):
        if interaction.user != self.originalUser:
            return

        self.wager -= 1
        if self.wager < 1:
            self.wager = 1
        self.updateEmbed()
        await interaction.response.edit_message(embed=self.embed)
    
    @discord.ui.button(label='+5', style=discord.ButtonStyle.secondary)
    async def buttonFive(self, interaction: discord.Interaction, button:discord.ui.Button):
        if interaction.user != self.originalUser:
            return

        self.wager += 5
        if self.wager > self.maxWager:
            self.wager = self.maxWager
        self.updateEmbed()
        await interaction.response.edit_message(embed=self.embed)

class BerryView(discord.ui.View):
    def __init__(self, parent, originalUser, *, timeout=90):
        super().__init__(timeout=timeout)
        self.wager = 1
        self.guess = 0
        self.berry = "-"
        self.parent = parent
        self.originalUser = originalUser
        self.maxWager = parent.checkBoxPieces(originalUser.id)
        self.url = "https://i.imgur.com/qf6kzdn.jpg"
        self.embed=discord.Embed(title="Berry Hungry Quagsire", description=f'{originalUser.mention}, how many Berries did Quagsire eat today?', color=0xf1d3ed)

    
    def updateEmbed(self):
        self.embed=discord.Embed(title="Berry Hungry Quagsire", description=f'{self.originalUser.mention}, how many Berries did Quagsire eat today?', color=0xf1d3ed)
        self.embed.set_thumbnail(url=self.url)
        self.embed.add_field(name=f'Wager (max {self.maxWager}):', value=f'1 box piece(s) (increase with the buttons)', inline=True)
        self.embed.add_field("# of Berries:")
        self.embed.add_field(name="(BONUS) Berry:", value=f'-', inline=True)

    @discord.ui.select(placeholder='Your Berry Good Guess', options = [
        discord.SelectOption(label='1 Berry'),
        discord.SelectOption(label='2 Berries'),
        discord.SelectOption(label='3 Berries'),
        discord.SelectOption(label='4 Berries'),
        discord.SelectOption(label='5 Berries'),
        discord.SelectOption(label='6 Berries'),
        discord.SelectOption(label='7 Berries'),
        discord.SelectOption(label='8 Berries'),
        discord.SelectOption(label='9 Berries'),
        discord.SelectOption(label='10 Berries'),
    ])
    async def selectOne(self, interaction: discord.Interaction, select):
        if interaction.user != self.originalUser:
            return

        self.attack = select.values[0]
        if self.attack == "Flamethrower":
            self.attack = "🟥 "+self.attack
        elif self.attack == "Razor Leaf":
            self.attack = "🟩 "+self.attack
        elif self.attack =="Bubblebeam":
            self.attack = "🟦 "+self.attack
        else:
            print("Error in parsing command")
        self.updateEmbed()
        await interaction.response.edit_message(embed=self.embed)

    @discord.ui.select(placeholder='Your Attack', options = [
            discord.SelectOption(label='Flamethrower', emoji='🟥'),
            discord.SelectOption(label='Razor Leaf', emoji='🟩'),
            discord.SelectOption(label='Bubblebeam', emoji='🟦'),
        ])
    async def selectTwo(self, interaction: discord.Interaction, select):
        if interaction.user != self.originalUser:
            return

        self.attack = select.values[0]
        if self.attack == "Flamethrower":
            self.attack = "🟥 "+self.attack
        elif self.attack == "Razor Leaf":
            self.attack = "🟩 "+self.attack
        elif self.attack =="Bubblebeam":
            self.attack = "🟦 "+self.attack
        else:
            print("Error in parsing command")
        self.updateEmbed()
        await interaction.response.edit_message(embed=self.embed)

    @discord.ui.button(label='FIGHT', style=discord.ButtonStyle.success)
    async def buttonOne(self, interaction: discord.Interaction, button:discord.ui.Button):
        if interaction.user != self.originalUser:
            return

        self.stop()
        currentUser = interaction.user
        imgURL = "https://i.imgur.com/qf6kzdn.jpg"
        embed=discord.Embed(title="RPS Battle", description=f'{currentUser.mention} wagered {self.wager} box pieces.', color=0xf1d3ed)
        embed.set_thumbnail(url=imgURL)

        if self.parent.tryDeductingBoxPieces(currentUser.id, self.wager) is True:
            if self.parent.tryDeductingWhoompTickets(currentUser.id, 1) is False:
                print("REALLY BAD ERROR IN DEDUCTING TICKETS")
                return

            quagAttack = random.choice(data.attacks)
            embed.add_field(name=f'{currentUser.name}\'s attack:', value=self.attack, inline=True)
            embed.add_field(name="Quagsire used:", value=quagAttack, inline=True)
            if quagAttack == self.attack:
                self.parent.miscCursor.execute(f'INSERT INTO \'ringTable\' (userid, itemname, itemattribute, timestamp) VALUES (\'{currentUser.id}\',\'Broken Box Piece x5\',\'{self.wager}\', datetime(\'now\'))')
                embed.add_field(name="...but nothing happened", value=f'Returned {self.wager} box pieces.', inline=False)
                embed.set_image(url="https://i.imgur.com/0K1MjHZ.png")
            elif data.weakness[quagAttack] == self.attack:
                self.parent.miscCursor.execute(f'INSERT INTO \'ringTable\' (userid, itemname, itemattribute, timestamp) VALUES (\'{currentUser.id}\',\'Broken Box Piece x5\',\'{self.wager*3}\', datetime(\'now\'))')
                self.parent.miscCursor.execute(f'INSERT INTO \'gamblingTable\' (userid, game, count, timestamp) VALUES (\'{currentUser.id}\',\'rps\', {self.wager*2}, datetime(\'now\'))')
                embed.add_field(name="YOU WIN", value=f'Gained {self.wager*3} box pieces.', inline=False)
                embed.set_image(url="https://i.imgur.com/LbM4jXk.jpeg")
            else:
                embed.add_field(name="YOU LOSE", value=f'Lost {self.wager} box pieces.', inline=False)
                self.parent.miscCursor.execute(f'INSERT INTO \'gamblingTable\' (userid, game, count, timestamp) VALUES (\'{currentUser.id}\',\'rps\', {-self.wager}, datetime(\'now\'))')
                embed.set_image(url="https://i.imgur.com/tMXcy9Z.jpeg")
            self.parent.miscConnection.commit()
        else:
            embed.add_field(name="Not enough box pieces.", value=f'\u200b', inline=False)
        await interaction.response.send_message(embed=embed)

    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.danger)
    async def buttonTwo(self, interaction: discord.Interaction, button:discord.ui.Button):
        if interaction.user != self.originalUser:
            return

        self.stop()
        self.embed=discord.Embed(title="RPS Battle", description=f'{self.originalUser.mention} will fight Quagsire.', color=0xf1d3ed)
        self.embed.set_thumbnail(url=self.url)
        self.embed.add_field(name="FIGHT CANCELLED", value=f'\u200b', inline=True)
        await interaction.response.edit_message(embed=self.embed)

    @discord.ui.button(label='+1', style=discord.ButtonStyle.secondary)
    async def buttonThree(self, interaction: discord.Interaction, button:discord.ui.Button):
        if interaction.user != self.originalUser:
            return

        self.wager += 1
        if self.wager > self.maxWager:
            self.wager = self.maxWager

        self.updateEmbed()
        await interaction.response.edit_message(embed=self.embed)

    @discord.ui.button(label='-1', style=discord.ButtonStyle.secondary)
    async def buttonFour(self, interaction: discord.Interaction, button:discord.ui.Button):
        if interaction.user != self.originalUser:
            return

        self.wager -= 1
        if self.wager < 1:
            self.wager = 1
        self.updateEmbed()
        await interaction.response.edit_message(embed=self.embed)
    
    @discord.ui.button(label='+5', style=discord.ButtonStyle.secondary)
    async def buttonFive(self, interaction: discord.Interaction, button:discord.ui.Button):
        if interaction.user != self.originalUser:
            return

        self.wager += 5
        if self.wager > self.maxWager:
            self.wager = self.maxWager
        self.updateEmbed()
        await interaction.response.edit_message(embed=self.embed)


class ShopButtons(discord.ui.View):
    def __init__(self, parent, *, timeout=90):
        super().__init__(timeout=timeout)
        self.parent = parent

    @discord.ui.button(label="1", style=discord.ButtonStyle.primary)
    async def buttonOne(self, interaction: discord.Interaction, button:discord.ui.Button):
        currentUser = interaction.user
        imgURL = "https://static.wikia.nocookie.net/maplestory/images/b/b1/Use_Hidden_Ring_Box.png/revision/latest?cb=20210914225553"
        boxPieces = self.parent.checkBoxPieces(currentUser.id)
        if self.parent.tryDeductingBoxPieces(currentUser.id, 10):
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
        else:
            embed=discord.Embed(title="Whooper's Ring Box", description=f'{currentUser.mention} you have {boxPieces} pieces.', color=0xf1d3ed)
            embed.set_thumbnail(url=imgURL)
            embed.add_field(name="Not enough box pieces.", value='\u200b', inline=False)
            embed.add_field(name="Pieces needed:", value=10-boxPieces, inline=False)

        await interaction.response.send_message(embed=embed)

    @discord.ui.button(label="2", style=discord.ButtonStyle.primary)
    async def buttonTwo(self, interaction: discord.Interaction, button:discord.ui.Button):
        currentUser = interaction.user
        imgURL = "https://static.wikia.nocookie.net/maplestory/images/b/ba/Use_Shiny_Ring_Box.png/revision/latest?cb=20210914225555"
        boxPieces = self.parent.checkBoxPieces(currentUser.id)
        if self.parent.tryDeductingBoxPieces(currentUser.id, 100):
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
        else:
            embed=discord.Embed(title="Whooper's Shiny Ring Box", description=f'{currentUser.mention} you have {boxPieces} pieces.', color=0xf1d3ed)
            embed.set_thumbnail(url=imgURL)
            embed.add_field(name="Not enough box pieces.", value='\u200b', inline=False)
            embed.add_field(name="Pieces needed:", value=100-boxPieces, inline=False)
        await interaction.response.send_message(embed=embed)

    @discord.ui.button(label="RPS Battle", style=discord.ButtonStyle.primary, disabled=False)
    async def buttonThree(self, interaction: discord.Interaction, button:discord.ui.Button):
        currentUser = interaction.user
        imgURL = "https://i.imgur.com/qf6kzdn.jpg"
        boxPieces = self.parent.checkBoxPieces(currentUser.id)
        whoompTickets = self.parent.checkWhoompTickets(currentUser.id)
        if boxPieces < 1 or whoompTickets < 1:
            embed=discord.Embed(title="RPS Battle", description=f'{currentUser.mention} you have {boxPieces} box pieces, {whoompTickets} tickets.', color=0xf1d3ed)
            embed.set_thumbnail(url=imgURL)
            embed.add_field(name="Not enough box pieces or tickets.", value='\u200b', inline=False)
            embed.add_field(name="Pieces needed:", value=1-boxPieces, inline=True)
            embed.add_field(name="Tickets needed:", value=1-whoompTickets, inline=True)
            await interaction.response.send_message(embed=embed)
        else:
            embed=discord.Embed(title="RPS Battle", description=f'{currentUser.mention} will fight Quagsire.', color=0xf1d3ed)
            embed.set_thumbnail(url=imgURL)
            embed.add_field(name=f'Wager (max {boxPieces}):', value=f'1 box piece(s) (increase with the buttons)', inline=True)
            embed.add_field(name="Selected Attack:", value=f'-', inline=True)
            await interaction.response.send_message(embed=embed, view=RPSView(self.parent, currentUser))
            return

    @discord.ui.button(label="Berry Hungry Quagsire", style=discord.ButtonStyle.secondary, disabled=True)
    async def buttonFour(self, interaction: discord.Interaction, button:discord.ui.Button):
        currentUser = interaction.user
        imgURL = "https://i.imgur.com/qf6kzdn.jpg"
        boxPieces = self.parent.checkBoxPieces(currentUser.id)
        whoompTickets = self.parent.checkWhoompTickets(currentUser.id)
        if boxPieces < 1 or whoompTickets < 1:
            embed=discord.Embed(title="Berry Hungry Quagsire", description=f'{currentUser.mention} you have {boxPieces} box pieces, {whoompTickets} tickets.', color=0xf1d3ed)
            embed.set_thumbnail(url=imgURL)
            embed.add_field(name="Not enough box pieces or tickets.", value='\u200b', inline=False)
            embed.add_field(name="Pieces needed:", value=1-boxPieces, inline=True)
            embed.add_field(name="Tickets needed:", value=1-whoompTickets, inline=True)
            await interaction.response.send_message(embed=embed)
        else:
            embed=discord.Embed(title="Berry Hungry Quagsire", description=f'{currentUser.mention}, how many Berries did Quagsire eat today?', color=0xf1d3ed)
            embed.set_thumbnail(url=imgURL)
            embed.add_field(name=f'Wager (max {boxPieces}):', value=f'1 box piece(s) (increase with the buttons)', inline=True)
            embed.add_field("# of Berries:")
            embed.add_field(name="(BONUS) Berry:", value=f'-', inline=True)
            await interaction.response.send_message(embed=embed, view=RPSView(self.parent, currentUser))
            return

    @discord.ui.button(label="5", style=discord.ButtonStyle.secondary, disabled=True)
    async def buttonFive(self, interaction: discord.Interaction, button:discord.ui.Button):
        embed=discord.Embed(color=0xf1d3ed)
        imgURL = "https://static.wikia.nocookie.net/maplestory/images/3/36/Use_Broken_Box_Piece.png/revision/latest?cb=20210910011106"
        embed.set_thumbnail(url=imgURL)
        embed.add_field(name="Tower of Oz", value=f'Prize Redemption for {interaction.user.mention}', inline=False)
        embed.add_field(name="Whoomper's Ring Box", value= '\u200b', inline=False)
        embed.add_field(name="Ring Name Placeholder", value= 'Ring Level Placeholder', inline=False)
        embed.set_footer(text=f'Remaining box pieces: {0}')
        await interaction.response.send_message(embed=embed)


class Games(commands.Cog):
    def __init__(self, bot):
        print(f'games.cog init')
        self.bot = bot
        self.usersRunning = {}

        self.runsRemaining = {}
        if os.path.isfile('runs.obj') and os.access('runs.obj', os.R_OK):
            with open('runs.obj', 'rb') as file_object:
                self.runsRemaining = pickle.load(file_object)
                print('Loaded # of Runs from File: ')
        print(self.runsRemaining)

        self.boxes = {} 
        if os.path.isfile('boxes.obj') and os.access('boxes.obj', os.R_OK):
            with open('boxes.obj', 'rb') as file_object:
                self.boxes = pickle.load(file_object)
                print('Loaded # of Boxes from File: ')
        print(self.boxes)

        self.ozRunTime = 50

        #DB Connection
        self.miscConnection = main.miscConnection
        self.miscCursor = main.miscConnection.cursor()
        self.checkRingTable()

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
        self.saveRunsRemainingToJson()
        print(f'User {self.bot.get_user(memberId)} completed an Oz run. Runs Remaining: {self.runsRemaining[memberId]}.')
        
    # Oz Run Starter
    def startOzRun(self, memberId):
        username = self.bot.get_user(memberId)
        print(f'User {username} is starting an Oz run...')
        if memberId not in self.runsRemaining:
            self.usersRunning[memberId] = (Timer(self.ozRunTime*60, self.ozRun, [memberId]), time.time())
            self.usersRunning[memberId][0].start()
            print(f'User {self.bot.get_user(memberId)} started an Oz run.')
        elif self.runsRemaining[memberId] > 0:
            self.usersRunning[memberId] = (Timer(self.ozRunTime*60, self.ozRun, [memberId]), time.time())
            self.usersRunning[memberId][0].start()
            print(f'User {self.bot.get_user(memberId)} started an Oz run.')
        else:
            print(f'User {username} has no more runs left.')

    def quitOzRun(self, memberId):
        if memberId not in self.usersRunning:
            print('User exited but is not currently running.')
            return
        self.usersRunning[memberId][0].cancel()
        del self.usersRunning[memberId]
        print(f'User {self.bot.get_user(memberId)} abandoned an Oz run.')

    # Box Incrementer
    def incrementBoxes(self, memberId):
        if memberId not in self.boxes:
            self.boxes[memberId] = 1
        else:
            self.boxes[memberId] += 1
        self.saveNumBoxesToJson()
        print(f'User {self.bot.get_user(memberId)} has received an oz box. Total boxes: {self.boxes[memberId]}.')

    def decrementBoxes(self, memberId):
        if memberId not in self.boxes:
            print('BUG: Member id should exist in boxes')
        else:
            self.boxes[memberId] -= 1
            if self.boxes[memberId] < 0:
                print('BUG: Member should not be allowed to decrement box below 0')
                self.boxes[memberId] = 0
        self.saveNumBoxesToJson()
    
    def checkBoxPieces(self, userId) -> int:
        self.miscCursor.execute(f'SELECT * FROM \'ringTable\' WHERE userid = \'{userId}\' AND itemname = \'Broken Box Piece x5\' AND itemattribute != \'0\'')
        resultTable = self.miscCursor.fetchall()
        boxPieces = 0
        for row in resultTable:
            boxPieces += int(row[2])
        return boxPieces

    def checkWhoompTickets(self, userId) -> int:
        self.miscCursor.execute(f'SELECT * FROM \'ringTable\' WHERE userid = \'{userId}\' AND (itemname = \'Whoomp Ticket\' or \'Whoomp Ticket x1\') AND itemattribute != \'0\'')
        resultTable = self.miscCursor.fetchall()
        whoompTickets = 0
        for row in resultTable:
            whoompTickets += int(row[2])
        return whoompTickets

    def tryDeductingBoxPieces(self, userId, cost) -> bool:
        self.miscCursor.execute(f'SELECT * FROM \'ringTable\' WHERE userid = \'{userId}\' AND itemname = \'Broken Box Piece x5\' AND itemattribute != \'0\'')
        resultTable = self.miscCursor.fetchall()
        boxPieces = 0
        for row in resultTable:
            boxPieces += int(row[2])
        myCost = cost

        if boxPieces < myCost:
            return False
        else:
            updateCursor = self.miscConnection.cursor()
            for row in resultTable:
                currentPieces = int(row[2])
                myCost = myCost-currentPieces
                if myCost > 0:
                    # update row with 0
                    updateCursor.execute(f'UPDATE \'ringTable\' SET itemattribute = \'0\' WHERE userid = \'{userId}\' AND itemname = \'Broken Box Piece x5\' AND timestamp = \'{row[3]}\'')
                else:
                    # update row with abs value of remaining cost and exit
                    updateCursor.execute(f'UPDATE \'ringTable\' SET itemattribute = \'{abs(myCost)}\' WHERE userid = \'{userId}\' AND itemname = \'Broken Box Piece x5\' AND timestamp = \'{row[3]}\'')
                    break
            self.miscConnection.commit()
            return True

    def tryDeductingWhoompTickets(self, userId, cost) -> bool:
        self.miscCursor.execute(f'SELECT * FROM \'ringTable\' WHERE userid = \'{userId}\' AND (itemname = \'Whoomp Ticket\' or \'Whoomp Ticket x1\') AND itemattribute != \'0\'')
        resultTable = self.miscCursor.fetchall()
        whoompTickets = 0
        for row in resultTable:
            whoompTickets += int(row[2])
        myCost = cost

        if whoompTickets < myCost:
            return False
        else:
            updateCursor = self.miscConnection.cursor()
            for row in resultTable:
                currentPieces = int(row[2])
                myCost = myCost-currentPieces
                if myCost > 0:
                    # update row with 0
                    updateCursor.execute(f'UPDATE \'ringTable\' SET itemattribute = \'0\' WHERE userid = \'{userId}\' AND (itemname = \'Whoomp Ticket\' or \'Whoomp Ticket x1\') AND timestamp = \'{row[3]}\'')
                else:
                    # update row with abs value of remaining cost and exit
                    updateCursor.execute(f'UPDATE \'ringTable\' SET itemattribute = \'{abs(myCost)}\' WHERE userid = \'{userId}\' AND (itemname = \'Whoomp Ticket\' or \'Whoomp Ticket x1\') AND timestamp = \'{row[3]}\'')
                    break
            self.miscConnection.commit()
            return True

    def saveNumBoxesToJson(self):
        with open('boxes.obj', 'wb') as file_object:
            pickle.dump(self.boxes, file_object)
        print('Storing # of Boxes to File: ')
        print(self.boxes)

    def saveRunsRemainingToJson(self):
        with open('runs.obj', 'wb') as file_object:
            pickle.dump(self.runsRemaining, file_object)
        print('Storing # of Runs to File: ')
        print(self.runsRemaining)

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

    def resetOzRuns(self):
        print("RESETTING OZ RUNS:")
        for user in self.runsRemaining:
            if user in self.usersRunning:
                self.runsRemaining[user] = 6
            else:
                self.runsRemaining[user] = 5
        
        self.initUsersRunning()
        self.saveRunsRemainingToJson()
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
                        if currentMember not in self.usersRunning:
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
        schedule.every().day.at("23:59").do(self.resetOzRuns)
        self.stop_run_continuously = self.run_continuously()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        currentId = member.id
        if after.channel == None:
            if before.afk != True:
                self.quitOzRun(currentId)
        elif before.channel == None and after.channel != None:
            if after.afk != True:
                self.startOzRun(currentId)
        else:
            if before.afk == True and after.afk == False:
                self.startOzRun(currentId)
            elif before.afk == False and after.afk == True:
                self.quitOzRun(currentId)
            else:
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
        else:
            embed.add_field(name="Current Status", value=timeString, inline=False)
            embed.add_field(name="Runs Left", value=self.runsRemaining[user.id], inline=True)

        if user.id not in self.boxes:
            embed.add_field(name="Boxes", value='0', inline=True)
        else:
            embed.add_field(name="Boxes", value=self.boxes[user.id], inline=True)
        
        embed.add_field(name="Box Pieces", value=boxPieces, inline=True)
        embed.add_field(name='Whoomp Tickets', value=self.checkWhoompTickets(user.id), inline=True)
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
            if currentUser.id not in self.runsRemaining:
                embed.add_field(name="Runs Left", value="5", inline=False)
            else:
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
                elif reward == 'Whoomp Ticket':
                    attribute = '2'
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

        embed.add_field(name=f'{user.mention} has {self.checkBoxPieces(user.id)} pieces, {self.checkWhoompTickets(user.id)} tickets', value=f'\u200b', inline=False)

        embed.add_field(name=f'**1.** Whoomper\'s Ring Box', value='10x Box Pieces', inline=False)
        embed.add_field(name=f'**2.** Whoomper\'s Shiny Ring Box', value='100x Box Pieces', inline=False)
        embed.add_field(name=f'**3.** Quagsire RPS', value = '1x Whoomp Ticket', inline=False)
        embed.add_field(name=f'**4.** Quagsire Mind Reading', value = '1x Whoomp Ticket', inline=False)
        embed.add_field(name=f'**5.** Feet Pics', value = 'Placeholder', inline=False)

        await interaction.response.send_message(embed=embed, view=ShopButtons(self))

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
            self.saveNumBoxesToJson()
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

            boxPieces = self.checkBoxPieces(user.id)
            
            embed=discord.Embed(title="Box Piece Dispenser", description=f'{user.mention} you now have {boxPieces} pieces.', color=0xf1d3ed)
            embed.set_thumbnail(url=imgURL)
        else:
            embed=discord.Embed(title="Box Piece Dispenser", description=f'{interaction.user} is not authorized to give pieces.', color=0xf1d3ed)
            embed.set_thumbnail(url=imgURL)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='givetickets', description='TESTING ONLY')
    async def givetickets(self, interaction: discord.Interaction, user: discord.User = None, num: int = 5):
        if user is None:
            user = interaction.user

        imgURL = "https://static.wikia.nocookie.net/maplestory/images/f/f3/Use_2x_EXP_Coupon.png/revision/latest?cb=20220712230445"
        if interaction.user.id == 125114599249936384:
            self.miscCursor.execute(f'INSERT INTO \'ringTable\' (userid, itemname, itemattribute, timestamp) VALUES (\'{user.id}\',\'Whoomp Ticket\',\'{num}\', datetime(\'now\'))')
            self.miscConnection.commit()

            self.miscCursor.execute(f'SELECT * FROM \'ringTable\' WHERE userid = \'{user.id}\' AND itemname = \'Whoomp Ticket\'')
            resultTable = self.miscCursor.fetchall()
            whoompTickets = 0
            for row in resultTable:
                whoompTickets += int(row[2])

            
            embed=discord.Embed(title="Whoomp Ticket Dispenser", description=f'{user.mention} you now have {whoompTickets} tickets.', color=0xf1d3ed)
            embed.set_thumbnail(url=imgURL)
        else:
            embed=discord.Embed(title="Whoomp Ticket Dispenser", description=f'{interaction.user} is not authorized to give tickets.', color=0xf1d3ed)
            embed.set_thumbnail(url=imgURL)

        await interaction.response.send_message(embed=embed)

    async def ozleaderboard_autocomplete(self, interaction: discord.Interaction, current: str,) -> List[app_commands.Choice[str]]:
        choices = data.leaderboardRings
        return [
            app_commands.Choice(name=choice, value=choice)
            for choice in choices if current.lower() in choice.lower()
        ]

    async def ozleaderboardlevel_autocomplete(self, interaction: discord.Interaction, current: str,) -> List[app_commands.Choice[str]]:
        localcopy = data.ringLevels
        choices = localcopy[::-1]
        return [
            app_commands.Choice(name=choice, value=choice)
            for choice in choices if current.lower() in choice.lower()
        ]

    @app_commands.command(name='ozrings', description='Display usable rings')
    @app_commands.autocomplete(ringname=ozleaderboard_autocomplete, ringlevel=ozleaderboardlevel_autocomplete)
    async def ozrings(self, interaction: discord.Interaction, ringname: str = 'Ring of Restraint', ringlevel: str = 'Level 4'):
        if ringname == 'Weapon Jump Rings (All)':
            imgURL = data.rewardLinks['Weapon Jump S Ring']
            self.miscCursor.execute(f'SELECT * FROM \'ringTable\' WHERE (itemname = \'Weapon Jump I Ring\' OR itemname = \'Weapon Jump L Ring\' OR itemname = \'Weapon Jump S Ring\' OR itemname = \'Weapon Jump D Ring\') AND itemattribute = \'{ringlevel}\'')
        else:
            if ringname not in data.rewardLinks or ringlevel not in data.ringLevels:
                embed = discord.Embed(title="Tower of Oz Leaderboard", description=f'Invalid Ring Name or Level')
                embed.set_thumbnail(url="https://i.imgur.com/dxPvMN8.gif")
                await interaction.response.send_message(embed=embed)
                return
            imgURL = data.rewardLinks[ringname]
            self.miscCursor.execute(f'SELECT * FROM \'ringTable\' WHERE itemname = \'{ringname}\' AND itemattribute = \'{ringlevel}\'')

        resultTable = self.miscCursor.fetchall()
        leaderboardDict = {}
        for row in resultTable:
            currentUser = row[0]
            if currentUser in leaderboardDict:
                leaderboardDict[currentUser] += 1
            else:
                leaderboardDict[currentUser] = 1

        embed = discord.Embed(title="Tower of Oz Leaderboard", description=f'{ringname} {ringlevel}')
        embed.set_thumbnail(url=imgURL)

        count = 0
        for key, value in sorted(leaderboardDict.items(), key=lambda item: item[1], reverse=True):
            embed.add_field(name=f'{count+1}) {self.bot.get_user(int(key)).name} has {value} ring(s)', value=f'\u200b', inline=False)
            count += 1
            if count >= 5:
                break

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Games(bot), guilds=config.guildList)