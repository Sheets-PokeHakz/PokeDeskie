import re
import json
import datetime
import traceback
import sys
import discord
from config import config
from database import database
from discord.ext import commands, tasks
from utils import pokemon_utils, trade_utils


class EventsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = None

        self.YAMPB_ID = 204255221017214977
        self.POKETWO_ID = 716390085896962058
        self.CARL_BOT_ID = 235148962103951360
        self.PK2_ASSISTANT_ID = 854233015475109888

    @commands.Cog.listener()
    async def on_ready(self):
        print("=" * 50)
        print("STATUS: ONLINE")
        print("=" * 50)
        print(f"BOT: {self.bot.user}")
        print(f"Logged in as {self.bot.user.name} ({self.bot.user.id})")
        print("=" * 50)

        await self.bot.change_presence(activity=discord.Game(name="PokeDex | +help"))

        self.start_time = datetime.datetime.now()
        self.bot.start_time = self.start_time

        self.daily_backup.start()

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return

        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Missing Requirement Argument : {error.param.name}")
            return

        if isinstance(error, commands.BadArgument):
            await ctx.send("❌ Invalid argument provided.")
            return

        # Log other errors
        print(f"Command error in {ctx.command}: {error}")
        await ctx.send("❌ An error occurred while processing the command.")

    @commands.Cog.listener()
    async def on_message(self, message):
        """Handle incoming messages for Pokemon bot integration."""
        # Ignore bot's own messages
        if message.author == self.bot.user:
            return

        # Handle Carl Bot Pokemon rolls
        if message.author.id == self.CARL_BOT_ID:
            await self._handle_carl_bot_pokemon(message)

        # Handle PK2 Assistant Pokemon rolls
        elif message.author.id == self.PK2_ASSISTANT_ID:
            await self._handle_pk2_pokemon(message)

        # Handle YAMPB Pokemon rolls
        elif message.author.id == self.YAMPB_ID:
            await self._handle_yampb_pokemon(message)

        # Handle Poketwo trade updates
        elif message.author.id == self.POKETWO_ID:
            await self._handle_poketwo_trade(message)

        # Process commands
        await self.bot.process_commands(message)

    async def _handle_carl_bot_pokemon(self, message):
        """Handle Carl Bot Pokemon roll messages."""
        if message.channel.id not in config.rand_channels:
            return

        if not message.embeds:
            return

        for embed in message.embeds:
            if "rolls" in embed.title:
                try:
                    # Extract Pokemon number from title
                    title_parts = embed.title.split(" ")
                    rolls_index = title_parts.index("rolls")
                    number_str = title_parts[rolls_index + 1].strip("**()")
                    number = int(number_str)

                    if 1 <= number <= 1017:
                        pokemon_data = pokemon_utils.get_pokemon_by_number(number)
                        if pokemon_data:
                            pokemon_embed = pokemon_utils.create_pokemon_embed(
                                pokemon_data
                            )
                            await message.channel.send(embed=pokemon_embed)
                except (ValueError, IndexError):
                    continue

    async def _handle_pk2_pokemon(self, message):
        """Handle PK2 Assistant Pokemon roll messages."""
        if message.channel.id not in config.rand_channels:
            return

        if not message.embeds:
            return

        for embed in message.embeds:
            if "Random Roll" in embed.title:
                try:
                    # Extract Pokemon number from description
                    description = embed.description
                    number = int(description.split("**")[-2])

                    if 1 <= number <= 1017:
                        pokemon_data = pokemon_utils.get_pokemon_by_number(number)
                        if pokemon_data:
                            pokemon_embed = pokemon_utils.create_pokemon_embed(
                                pokemon_data
                            )
                            await message.channel.send(embed=pokemon_embed)
                except (ValueError, IndexError):
                    continue

    async def _handle_yampb_pokemon(self, message):
        """Handle YAMPB Pokemon roll messages."""
        if message.channel.id not in config.rand_channels:
            return

        if ":game_die:" in message.content:
            try:
                number = int(message.content.split(" ")[1])

                if 1 <= number <= 1017:
                    pokemon_data = pokemon_utils.get_pokemon_by_number(number)
                    if pokemon_data:
                        pokemon_embed = pokemon_utils.create_pokemon_embed(pokemon_data)
                        await message.channel.send(embed=pokemon_embed)
            except (ValueError, IndexError):
                return

    async def _handle_poketwo_trade(self, message):
        """Handle Poketwo trade completion messages."""
        if message.channel.id not in config.trade_channels:
            return

        if not message.embeds:
            return

        embed = message.embeds[0]
        if "Completed trade between" not in embed.title:
            return

        try:
            # Process trade data
            await self._process_trade_data(message, embed)
        except Exception as e:
            print(f"Error processing trade: {e}")
            traceback.print_exc()

    async def _process_trade_data(self, message, embed):
        """Process and log trade data."""
        # Get trade log channel
        trade_log_channel = self.bot.get_channel(config.trade_log)
        if not trade_log_channel:
            return

        # Create message link
        message_link = f"https://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id}"

        # Extract participant data
        embed_dict = embed.to_dict()
        if "fields" not in embed_dict or len(embed_dict["fields"]) < 2:
            return

        participant1 = embed_dict["fields"][0]["name"][2:]  # Remove "• " prefix
        participant2 = embed_dict["fields"][1]["name"][2:]  # Remove "• " prefix

        # Save trade data
        trade_utils.save_trade_data(participant1, participant2, message_link)

        # Create enhanced embed with message link
        enhanced_embed = embed.copy()
        enhanced_embed.add_field(name="Message Link", value=message_link, inline=False)

        # Send to trade log channel
        participants_msg = f"Gamblers: {participant1}, {participant2}"
        await trade_log_channel.send(participants_msg, embed=enhanced_embed)

        # Update gambling statistics
        await self._update_gambling_stats(
            message.guild, participant1, participant2, embed_dict
        )

    async def _update_gambling_stats(
        self, guild, participant1, participant2, embed_dict
    ):
        """Update gambling statistics for trade participants."""
        # Find member objects by display name
        member1 = None
        member2 = None

        for member in guild.members:
            if member.display_name == participant1 or (
                member.nick and member.nick == participant1
            ):
                member1 = member
            if member.display_name == participant2 or (
                member.nick and member.nick == participant2
            ):
                member2 = member

        if not member1 or not member2:
            return

        # Register users if needed
        if database.get_user_details(member1.id) is None:
            database.register_user(member1.id)
        if database.get_user_details(member2.id) is None:
            database.register_user(member2.id)

        # Extract coin amounts from trade
        value1 = embed_dict["fields"][0]["value"]
        value2 = embed_dict["fields"][1]["value"]

        user1_coins = self._extract_coin_amount(value1)
        user2_coins = self._extract_coin_amount(value2)

        if user1_coins > 0 or user2_coins > 0:
            # Update net totals and gambling stats
            if user1_coins > 0:
                database.update_user_net_total(member1.id, -user1_coins)  # Lost coins
                database.update_user_net_total(member2.id, user1_coins)  # Gained coins

            if user2_coins > 0:
                database.update_user_net_total(member2.id, -user2_coins)  # Lost coins
                database.update_user_net_total(member1.id, user2_coins)  # Gained coins

            # Determine winner and update gambling stats
            if user1_coins > user2_coins:
                # Member2 won
                database.update_gamble_stats(
                    member2.id, True, max(user1_coins, user2_coins)
                )
                database.update_gamble_stats(
                    member1.id, False, max(user1_coins, user2_coins)
                )
            elif user2_coins > user1_coins:
                # Member1 won
                database.update_gamble_stats(
                    member1.id, True, max(user1_coins, user2_coins)
                )
                database.update_gamble_stats(
                    member2.id, False, max(user1_coins, user2_coins)
                )

    def _extract_coin_amount(self, text):
        """Extract coin amount from trade text."""
        match = re.search(r"(\d+(?:,\d+)*)\s+Pok", text)
        if match:
            return int(match.group(1).replace(",", ""))
        return 0

    @tasks.loop(hours=24)
    async def daily_backup(self):
        """Perform daily database backup."""
        if datetime.datetime.now().time().strftime("%H:%M") == "00:00":
            await self._backup_database()

    async def _backup_database(self):
        """Backup the database to webhook."""
        if not config.webhook_url:
            return

        try:
            # This would require the discord-webhook library
            # For now, just print that backup would happen
            print(f"Database backup scheduled for {datetime.datetime.now()}")
        except Exception as e:
            print(f"Backup failed: {e}")

    @commands.command()
    async def ping(self, ctx):
        """Display bot latency and uptime."""
        latency = self.bot.latency * 1000

        if self.start_time:
            uptime = datetime.datetime.now() - self.start_time
            uptime_str = str(uptime).split(".")[0]  # Remove microseconds
        else:
            uptime_str = "Unknown"

        num_servers = len(self.bot.guilds)

        embed = discord.Embed(title="🏓 Pong", color=0x2F3136)
        embed.add_field(name="Uptime", value=uptime_str, inline=False)
        embed.add_field(name="Latency", value=f"{latency:.2f}ms", inline=False)
        embed.add_field(name="Servers", value=num_servers, inline=False)

        await ctx.send(embed=embed)


async def setup(bot):
    """Setup function for the cog."""
    await bot.add_cog(EventsCog(bot))
