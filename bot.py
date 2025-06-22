import os
import asyncio
import discord
import datetime
from config import config
from dotenv import load_dotenv
from discord.ext import commands

from utils import log_utils

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

    log_utils.log(ctx, "info")

    embed = discord.Embed(
        title="What Even Is This ?",
        description=".....",
        color=0x2F3136,
    )

    if bot.user.avatar:
        embed.set_thumbnail(url=bot.user.avatar.url)

    await ctx.send(embed=embed)


@bot.command(name="checkembed")
async def checkembed(ctx):
    if ctx.author.id not in config.admin_uids:
        await ctx.send(
            "❌ You Don't Have Permission To Use This Command.", ephemeral=True
        )
        return
    
    log_utils.log(ctx, "checkembed")

    ref = ctx.message.reference
    if ref and ref.resolved and isinstance(ref.resolved, discord.Message):
        referenced_msg = ref.resolved

        if referenced_msg.embeds:
            for i, embed in enumerate(referenced_msg.embeds, start=1):
                await ctx.send(f"**Embed {i} :**")
                if embed.title:
                    await ctx.send(f"**Title :** {embed.title}")
                if embed.description:
                    await ctx.send(f"**Description :** {embed.description}")
                if embed.fields:
                    for field in embed.fields:
                        await ctx.send(f"**{field.name} :** {field.value}")
        else:
            await ctx.send("Referenced Message Has No Embeds")
    else:
        await ctx.send("No Valid Reference Found")


@bot.command(name="checkmessage")
async def checkmessage(ctx):
    if ctx.author.id not in config.admin_uids:
        await ctx.send(
            "❌ You Don't Have Permission To Use This Command.", ephemeral=True
        )
        return

    log_utils.log(ctx, "checkmessage")

    ref = ctx.message.reference
    if ref and ref.resolved and isinstance(ref.resolved, discord.Message):
        referenced_msg = ref.resolved

        content = referenced_msg.content.strip()
        if content:
            await ctx.send(f"📨 Message Content :\n```\n{content}\n```")

        else:
            await ctx.send("Referenced Message Has No Content")
    else:
        await ctx.send("No Valid Reference Found")


bot.load_extension("cogs.admin")
bot.load_extension("cogs.pokemon")
bot.load_extension("cogs.gambling")
bot.load_extension("cogs.events")
bot.load_extension("cogs.help")

bot.run(os.getenv("BOT_TOKEN"))
