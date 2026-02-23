import os
import asyncio
import discord
from discord.ext import commands
from flask import Flask
from threading import Thread
from dotenv import load_dotenv

load_dotenv()

# Flask server for keep-alive
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# Discord Bot Setup
intents = discord.Intents.default()
intents.message_content = True

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Load cogs here if any exist in the cogs/ directory
        if os.path.exists('./cogs'):
            for filename in os.listdir('./cogs'):
                if filename.endswith('.py'):
                    await self.load_extension(f'cogs.{filename[:-3]}')

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

bot = MyBot()

@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')

def main():
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("Error: DISCORD_TOKEN not found in environment variables.")
        return

    # Start Flask in a separate thread
    t = Thread(target=run_flask)
    t.start()

    # Run Discord Bot
    bot.run(token)

if __name__ == "__main__":
    main()