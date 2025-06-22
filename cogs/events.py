import re
import discord
import datetime
import traceback
from config import config
from database import database
from discord.ext import commands, tasks
from utils import pokemon_utils, trade_utils

from utils import log_utils


class EventCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = None

        self.YAMPB_ID = 204255221017214977
        self.POKETWO_ID = 716390085896962058
        self.CARL_BOT_ID = 235148962103951360
        self.PK2_ASSISTANT_ID = 854233015475109888

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        # Handle Carl Bot Pokemon Rolls
        if message.author.id == self.CARL_BOT_ID:
            print(f"Info : {message.author} : Received Carl Roll Message")

            await self._handle_carl_bot_pokemon(message)

        # Handle PK2 Assistant Pokemon Rolls
        elif message.author.id == self.PK2_ASSISTANT_ID:
            print(f"Info : {message.author} : Received PK2 Assistant Roll Message")

            await self._handle_pk2_pokemon(message)

        # Handle YAMPB Pokemon Rolls
        elif message.author.id == self.YAMPB_ID:
            print(f"Info : {message.author} : Received YAMP Roll Message")

            await self._handle_yampb_pokemon(message)

        # Handle Poketwo Trade Updates
        elif message.author.id == self.POKETWO_ID:
            print(f"Info : {message.author} : Received Poketwo Message")

            await self._handle_poketwo_trade(message)

    async def _handle_carl_bot_pokemon(self, message):
        print(f"Info : {message.author} : Processing Carl Roll")

        if message.channel.id not in config.rand_channels:
            return

        if not message.embeds:
            return

        for embed in message.embeds:
            if "rolls" in embed.title:
                try:
                    title_parts = embed.title.split(" ")
                    rolls_index = title_parts.index("rolls")
                    number_str = title_parts[rolls_index + 1].strip("**()")
                    number = int(number_str)

                    print(f"Extracted Number: {number}")

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
        print(f"Info : {message.author} : Processing PK2 Assistant Roll")

        if message.channel.id not in config.rand_channels:
            return

        if not message.embeds:
            return

        for embed in message.embeds:
            if "Random Roll" in embed.title:
                try:
                    description = embed.description
                    number = int(description.split("**")[-2])

                    print(f"Extracted Number: {number}")

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
        print(f"Info : {message.author} : Processing YAMPB Roll")

        if message.channel.id not in config.rand_channels:
            return

        content = (
            message.content.strip()
            or (message.embeds[0].description if message.embeds else "")
            or (message.embeds[0].title if message.embeds else "")
        )

        if not content and message.embeds:
            content = message.embeds[0].description or message.embeds[0].title or ""

        if ":game_die:" in content:
            try:
                match = re.search(r":game_die:\s*(\d+)\s*\(", content)
                if not match:
                    print("No number matched.")
                    return

                number = int(match.group(1))
                print(f"🎲 Extracted Number: {number}")

                if 1 <= number <= 1017:
                    pokemon_data = pokemon_utils.get_pokemon_by_number(number)
                    if pokemon_data:
                        pokemon_embed = pokemon_utils.create_pokemon_embed(pokemon_data)
                        await message.channel.send(embed=pokemon_embed)

            except (ValueError, IndexError) as e:
                print(f"Error: {e}")

    async def _handle_poketwo_trade(self, message):
        print(f"Info : {message.author} : Processing Poketwo Trade Roll")

        if message.channel.id not in config.rand_channels:
            return

        if not message.embeds:
            return

        try:
            embed = message.embeds[0]
            title = embed.title or "No Title"

            if "Completed Trade " in title:
                await self._process_trade_data(message, embed)

        except Exception as e:
            print(f"Error Processing Trade : {e}")
            traceback.print_exc()

    async def _process_trade_data(self, message, embed):
        for channel_id in config.trade_log:
            trade_log_channel = self.bot.get_channel(channel_id)

        if not trade_log_channel:
            return

        message_link = f"https://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id}"

        embed_dict = embed.to_dict()
        fields = embed_dict.get("fields", [])
        if len(fields) < 2:
            return

        participant1 = fields[0]["name"].strip("🟢 ").strip()
        participant2 = fields[1]["name"].strip("🟢 ").strip()

        trade_utils.save_trade_data(participant1, participant2, message_link)

        enhanced_embed = embed.copy()
        enhanced_embed.add_field(
            name="🔗 Message Link", value=message_link, inline=False
        )

        participants_msg = f"Gamblers: **{participant1}**, **{participant2}**"
        await trade_log_channel.send(participants_msg, embed=enhanced_embed)

        await self._update_gambling_stats(
            message.guild, participant1, participant2, embed_dict
        )

    async def _update_gambling_stats(
        self, guild, participant1, participant2, embed_dict
    ):
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

        # Register Users If Not Registered
        if database.get_user_details(member1.id) is None:
            database.register_user(member1.id)

        if database.get_user_details(member2.id) is None:
            database.register_user(member2.id)

        # Extract Coin Amounts
        value1 = embed_dict["fields"][0]["value"]
        value2 = embed_dict["fields"][1]["value"]

        user1_coins = self._extract_coin_amount(value1)
        user2_coins = self._extract_coin_amount(value2)

        if user1_coins > 0 or user2_coins > 0:
            # Update Net Totals
            if user1_coins > 0:
                database.update_user_net_total(member1.id, -user1_coins)  # Lost Coins
                database.update_user_net_total(member2.id, user1_coins)  # Gained Coins

            if user2_coins > 0:
                database.update_user_net_total(member2.id, -user2_coins)  # Lost Coins
                database.update_user_net_total(member1.id, user2_coins)  # Gained Coins

            # Determine Winner And Update Database
            if user1_coins > user2_coins:
                # Member 2 Won
                database.update_gamble_stats(
                    member2.id, True, max(user1_coins, user2_coins)
                )
                database.update_gamble_stats(
                    member1.id, False, max(user1_coins, user2_coins)
                )
            elif user2_coins > user1_coins:
                # Member 1 Won
                database.update_gamble_stats(
                    member1.id, True, max(user1_coins, user2_coins)
                )
                database.update_gamble_stats(
                    member2.id, False, max(user1_coins, user2_coins)
                )

    def _extract_coin_amount(self, text):
        match = re.search(r"(\d+(?:,\d+)*)\s+Pok", text)
        if match:
            return int(match.group(1).replace(",", ""))
        return 0


def setup(bot):
    bot.add_cog(EventCog(bot))
