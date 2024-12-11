import discord
from discord.ext import commands
from collections import Counter
import datetime
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Bot setup
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.reactions = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

async def get_top_reacted_messages(guild: discord.Guild, year: int):
    message_reactions = []
    current_year = datetime.datetime.now().year

    if year > current_year:
        raise ValueError("Year cannot be in the future.")

    for channel in guild.text_channels:
        try:
            async for message in channel.history(limit=None, after=datetime.datetime(year, 1, 1), before=datetime.datetime(year + 1, 1, 1)):
                total_reactions = sum(reaction.count for reaction in message.reactions)
                message_reactions.append((message, total_reactions))
        except (discord.Forbidden, discord.HTTPException):
            continue

    # Sort messages by total reactions
    sorted_messages = sorted(message_reactions, key=lambda x: x[1], reverse=True)
    return sorted_messages[:25]

@bot.command()
async def top_messages(ctx, year: int = datetime.datetime.now().year):
    """Ranks the top 25 most reacted messages in the server for the given year."""
    try:
        top_messages = await get_top_reacted_messages(ctx.guild, year)
        if not top_messages:
            await ctx.send(f"No messages found with reactions for {year}.")
            return

        embed = discord.Embed(title=f"Top 25 Most Reacted Messages in {year}", color=discord.Color.blue())

        for rank, (message, reactions) in enumerate(top_messages, start=1):
            content_preview = message.content[:50] + ('...' if len(message.content) > 50 else '')
            embed.add_field(
                name=f"#{rank} - {reactions} Reactions",
                value=f"[Jump to Message]({message.jump_url})\nContent: {content_preview}",
                inline=False
            )

        await ctx.send(embed=embed)
    except ValueError as e:
        await ctx.send(str(e))
    except discord.Forbidden:
        await ctx.send("I don't have permission to access some channels in this server.")

bot.run(BOT_TOKEN)
