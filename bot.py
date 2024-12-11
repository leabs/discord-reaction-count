import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from datetime import datetime
import asyncio

# Load environment variables from .env file
load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')

# Set up Discord Intents
intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.messages = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot is online as {bot.user} (ID: {bot.user.id})')
    print('Ready to receive commands!')

def chunk_message(message, chunk_size=2000):
    """Splits a message into chunks fitter under a certain character size."""
    return [message[i:i+chunk_size] for i in range(0, len(message), chunk_size)]

@bot.command(name='topreactions')
async def top_reactions(ctx):
    this_year_start = datetime(datetime.now().year, 1, 1)
    messages_with_reactions = []

    # Specifying a reasonable limit to avoid excessive data retrieval per call
    message_fetch_limit = 100

    # Define emojis to filter reactions (including emoji codes for both Unicode and custom emojis)
    desired_emojis = [":joy:", ":cryinglaughing:", ":HOF:"]

    for channel in ctx.guild.text_channels:
        # Only process channels where the bot can read message history
        permissions = channel.permissions_for(ctx.me)
        if permissions.read_message_history:
            try:
                print(f"Processing channel '{channel.name}'")
                async for message in channel.history(limit=message_fetch_limit, after=this_year_start):
                    # Check if any desired emoji is in the reactions
                    matching_reactions = []
                    for reaction in message.reactions:
                        emoji_name = ""
                        if isinstance(reaction.emoji, discord.PartialEmoji) or isinstance(reaction.emoji, discord.Emoji):
                            emoji_name = f":{reaction.emoji.name}:"
                        elif isinstance(reaction.emoji, str):
                            emoji_name = reaction.emoji

                        if emoji_name in desired_emojis:
                            matching_reactions.append(reaction.count)

                    total_reactions = sum(matching_reactions)
                    if total_reactions > 0:
                        messages_with_reactions.append((message, total_reactions))

                # Add a slight delay to adhere to rate limits
                await asyncio.sleep(0.5)

            except discord.errors.Forbidden:
                print(f"Permission denied for channel '{channel.name}', despite checks. Skipping channel.")
                continue
        else:
            print(f"Skipping channel '{channel.name}' as Read Message History permission is False.")

    # Sort messages by the total number of reactions in descending order
    messages_with_reactions.sort(key=lambda msg: msg[1], reverse=True)

    # Prepare the output for the top 25 messages
    top_25 = messages_with_reactions[:25]
    if not top_25:
        await ctx.send("No messages with reactions found this year.")
        return

    response_lines = ["Top 25 Messages with Reactions from this Year Across Accessible Channels:"]
    for message, count in top_25:
        response_lines.append(f"Reactions: {count} - Message: {message.content[:50]}... [Link](https://discordapp.com/channels/{ctx.guild.id}/{message.channel.id}/{message.id})")

    response = '\n'.join(response_lines)

    # Send the response in chunks
    for chunk in chunk_message(response):
        await ctx.send(chunk)

bot.run(TOKEN)
