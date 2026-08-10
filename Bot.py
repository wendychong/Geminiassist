import os
import discord
from discord.ext import commands
from google import genai

# Pull secrets safely from environment variables
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Initialize Gemini Client
gemini_client = genai.Client(api_key=GEMINI_API_KEY)

# Initialize Discord Bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.event
async def on_message(message):
    # Prevent bot from responding to itself
    if message.author == bot.user:
        return

    # Trigger when the bot is mentioned or via a direct message
    if bot.user.mentioned_in(message) or isinstance(message.channel, discord.DMChannel):
        # Remove the bot mention from the prompt text
        prompt = message.content.replace(f'<@{bot.user.id}>', '').strip()
        
        if not prompt:
            await message.channel.send("Hello! How can I help you today?")
            return

        async with message.channel.typing():
            try:
                # Call Gemini API (Using Gemini 2.5 Flash for fast response times)
                response = gemini_client.models.generate_content(
                    model='gemini-3.6-flash',
                    contents=prompt,
                )
                
                # Handle Discord's 2000 character limit by splitting if needed
                reply_text = response.text
                if len(reply_text) <= 2000:
                    await message.reply(reply_text)
                else:
                    for i in range(0, len(reply_text), 1900):
                        await message.channel.send(reply_text[i:i+1900])
            except Exception as e:
                await message.reply(f"An error occurred: {str(e)}")

    await bot.process_commands(message)

bot.run(DISCORD_TOKEN)
