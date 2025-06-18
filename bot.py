import os
import asyncio
import discord
import datetime
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="+", intents=intents)

bot.remove_command("help")

@bot.event
async def on_ready():
    print("--------------------------------")
    print("----- + LOADED POKEDX BOT + ----")
    print("--------------------------------")

    await bot.change_presence(activity=discord.Game(name="Gablimg | +help"))

    start_time = datetime.datetime.now()
    bot.start_time = start_time

    print("----- + LOADING COMMANDS + -----")
    print("--------------------------------")

    commands = 0

    print("+ Registered Commands +")
    for cmd in bot.commands:
        print(f"- {cmd.name}")
        commands += 1

    print("--------------------------------")
    print(f"--- + Loaded : {commands} Commands + ---")
    print("--------------------------------")

    print("------- + LOADING COGS + -------")
    print(f"----- + Loaded : {len(bot.cogs)} Cogs + ------")
    print("--------------------------------")



@bot.command(name="info")
async def info(ctx):
    print(f"Info : {ctx.author} : {ctx.guild.name} : {ctx.guild.id}")

    embed = discord.Embed(
        title=":information_source: What Even Is This ?",
        description=".....",
        color=0x2F3136,
    )

    if bot.user.avatar:
        embed.set_thumbnail(url=bot.user.avatar.url)

    await ctx.send(embed=embed)


bot.load_extension("cogs.admin")
bot.load_extension("cogs.pokemon")
bot.load_extension("cogs.gambling")
bot.load_extension("cogs.events")
bot.load_extension("cogs.help")

bot.run(os.getenv("BOT_TOKEN"))
