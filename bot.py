import config
import discord

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

def main():
    client.run(config.botToken)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return 

    if message.author.id == 125114599249936384:
        await message.channel.send("says the furniture stealer")

if __name__ == '__main__':
    main()