import os
import sys
import asyncio
import discord
from config import config
from discord.ext import commands


intents = discord.Intents.all()
bot = commands.Bot(command_prefix="+", intents=intents)


bot.remove_command("help")


async def load_cogs():
    cogs_to_load = [
        "cogs.admin",
        "cogs.pokemon",
        "cogs.gambling",
        "cogs.events",
        "cogs.help",
    ]

    for cog in cogs_to_load:
        try:
            await bot.load_extension(cog)
            print(f"✅ Loaded {cog}")
        except Exception as e:
            print(f"❌ Failed To Load {cog}: {e}")


async def main():
    await load_cogs()

    token = os.environ.get("BOT_TOKEN") or config.get("bot_token")

    if not token:
        print("❌ Bot Token Not Found!")
        sys.exit(1)

    try:
        await bot.start(token)
    except discord.LoginFailure:
        print("❌ Invalid Bot Token!")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error Stating Bot : {e}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Bot Shutting Down ...")
    except Exception as e:
        print(f"❌ Fatal Error : {e}")
        sys.exit(1)
