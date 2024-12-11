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
    """Splits a message into chunks fitted under a certain character size."""
    return [message[i:i + chunk_size] for i in range(0, len(message), chunk_size)]


@bot.command(name='topreactions')
async def top_reactions(ctx):
    this_year_start = datetime(datetime.now().year, 1, 1)
    messages_with_reactions = []

    # Define emojis using Unicode representation for standard emojis and name for custom emojis
    target_emojis = {"😂", ":cryinglaughing:", ":HOF:"}

    # Process the first two categories in the server
    categories_to_check = ctx.guild.categories[:2]  # Limits to the first two categories

    for category in categories_to_check:
        for channel in category.text_channels:
            permissions = channel.permissions_for(ctx.me)
            if permissions.read_message_history:
                try:
                    print(f"Processing channel '{channel.name}' in category '{category.name}'")
                    async for message in channel.history(limit=None, after=this_year_start):
                        emoji_counts = {emoji: 0 for emoji in target_emojis}
                        total_reactions = 0

                        for reaction in message.reactions:
                            emoji_key = str(reaction.emoji)
                            if isinstance(reaction.emoji, (discord.PartialEmoji, discord.Emoji)):
                                emoji_key = f":{reaction.emoji.name}:"
                            
                            if emoji_key in target_emojis:
                                emoji_counts[emoji_key] += reaction.count
                                total_reactions += reaction.count

                        if total_reactions > 0:
                            messages_with_reactions.append((message, total_reactions, emoji_counts))

                    # Add a slight delay to adhere to rate limits
                    await asyncio.sleep(0.5)

                except discord.errors.Forbidden:
                    print(f"Permission denied for channel '{channel.name}', despite checks. Skipping channel.")
                    continue
            else:
                print(f"Skipping channel '{channel.name}' as Read Message History permission is False.")

    messages_with_reactions.sort(key=lambda msg: msg[1], reverse=True)

    top_25 = messages_with_reactions[:25]
    if not top_25:
        await ctx.send("No messages with reactions found this year in the first two sections.")
        return

    response_lines = ["Top 25 Messages with Reactions from this Year Across First Two Categories:"]
    for index, (message, count, emoji_counts) in enumerate(top_25, start=1):
        author = message.author
        emoji_details = ', '.join([f"{emoji}: {cnt}" for emoji, cnt in emoji_counts.items() if cnt > 0])
        response_lines.append(
            f"#{index} - User: {author.display_name}\n"
            f"Message: \"{message.content[:50]}...\"\n"
            f"Reactions: {emoji_details} [Link](https://discordapp.com/channels/{ctx.guild.id}/{message.channel.id}/{message.id})\n"
        )

    response = '\n\n'.join(response_lines)

    for chunk in chunk_message(response):
        await ctx.send(chunk)


bot.run(TOKEN)
