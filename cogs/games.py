# Dependencies
import random
from threading import Timer

# File Imports
import config

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
        self.usersRunning[memberId] = Timer(5, self.ozRun, [memberId])
        self.usersRunning[memberId].start()
        print(f'User {self.bot.get_user(memberId)} started an Oz run.')

    # Box Incrementer
    def incrementBoxes(self, memberId):
        if memberId not in self.boxes:
            self.boxes[memberId] = 1
        else:
            self.boxes[memberId] += 1

    
    # Initialize currently connected users
    def updateUsersRunning(self):
        updateTime = time.time()
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
        self.updateUsersRunning()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if after.channel == None:
            if before.afk != True:
                # print(f'User {self.connectedUsers} disconnected.')
        elif before.channel == None and after.channel != None:
            if after.afk != True:
                # print(f'User {self.connectedUsers} connected.')
        else:
            if before.afk == True and after.afk == False:
                # print(f'User {self.connectedUsers} returned from afk.')
            elif before.afk == False and after.afk == True:
                # print(f'User {self.connectedUsers} went afk.')
            else:
                # print(f'User {self.connectedUsers} made a non-connection related voice status update.')
        return

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

    @app_commands.command(name='ozbox', description='Open a Tower of Oz ring box')
    async def ozbox(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message("This command is under construction")

async def setup(bot):
    await bot.add_cog(Games(bot), guilds=config.guildList)