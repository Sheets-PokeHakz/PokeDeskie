import os
import json
import discord
import datetime
import requests
from dotenv import load_dotenv
from typing import Dict, Any, List, Optional


class PokemonUtils:
    def __init__(self, pokedex_file: str = "PokeDex.json"):
        self.pokedex_file = pokedex_file
        self._pokedex_data = {}
        self.load_pokedex()

    def load_pokedex(self) -> None:
        try:
            with open(self.pokedex_file, "r") as file:
                self._pokedex_data = json.load(file)
        except FileNotFoundError:
            print(f"PokeDex File {self.pokedex_file} Not Found")
            self._pokedex_data = {}
        except json.JSONDecodeError:
            print(f"Invalid JSON In {self.pokedex_file}.")
            self._pokedex_data = {}

    def get_pokemon_by_number(self, number: int) -> Optional[Dict[str, Any]]:
        if isinstance(self._pokedex_data, list):
            if 0 <= number < len(self._pokedex_data):
                pokemon_data = self._pokedex_data[number]
                if pokemon_data and len(pokemon_data) > 0:
                    return pokemon_data
                return None
            return None
        else:
            return self._pokedex_data.get(number)

    def search_pokemon_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        name_lower = name.lower()

        if isinstance(self._pokedex_data, list):
            for pokemon_data in self._pokedex_data:
                if pokemon_data and pokemon_data.get("title", ""):
                    if name_lower in pokemon_data.get("title", "").lower():
                        return pokemon_data
        else:
            for pokemon_data in self._pokedex_data.values():
                if name_lower in pokemon_data.get("title", "").lower():
                    return pokemon_data

        return None

    def get_pokemon_stats(self, pokemon_data: Dict[str, Any]) -> List[str]:
        stats = []
        for field in pokemon_data.get("fields", []):
            if field["name"] == "Base Stats":
                value = field["value"]

                hp = self._extract_stat(value, "HP")
                attack = self._extract_stat(value, "Attack")
                defense = self._extract_stat(value, "Defense")
                sp_atk = self._extract_stat(value, "Sp. Atk")
                sp_def = self._extract_stat(value, "Sp. Def")
                speed = self._extract_stat(value, "Speed")

                total = hp + attack + defense + sp_atk + sp_def + speed

                stats.extend(
                    [
                        f"**HP:** {hp}",
                        f"**Attack:** {attack}",
                        f"**Defense:** {defense}",
                        f"--------------",
                        f"**Sp. Atk:** {sp_atk}",
                        f"**Sp. Def:** {sp_def}",
                        f"--------------",
                        f"**Speed:** {speed}",
                        f"**Total:** {total}",
                    ]
                )
                break

        return stats

    def _extract_stat(self, text: str, stat_name: str) -> int:
        try:
            start = text.find(f"**{stat_name}:** ") + len(f"**{stat_name}:** ")
            if start == len(f"**{stat_name}:** ") - 1:
                return 0

            end = text.find("\n", start)
            if end == -1:
                end = len(text)

            return int(text[start:end].strip())
        except (ValueError, AttributeError):
            return 0

    def create_pokemon_embed(
        self, pokemon_data: Dict[str, Any], include_stats: bool = True
    ) -> discord.Embed:

        embed = discord.Embed(
            title=pokemon_data.get("title", "Unknown Pokemon"),
            color=pokemon_data.get("color", 0x2F3136),
        )

        image_url = pokemon_data.get("image", {}).get("url")
        if image_url:
            embed.set_thumbnail(url=image_url)

        if include_stats:
            stats = self.get_pokemon_stats(pokemon_data)
            if stats:
                embed.add_field(name="Stats", value="\n".join(stats), inline=False)

        return embed

    def save_pokemon_to_dex(self, pokemon_entry: Dict[str, Any]) -> bool:
        try:
            title = pokemon_entry.get("title", "")
            if not title or "—" not in title:
                print("Invalid Pokemon Entry: Missing Title Format")
                return False

            number_part = title.split("—")[0].strip().replace("#", "")
            try:
                pokemon_number = int(number_part)
            except ValueError:
                print(f"Invalid Pokemon Number: {number_part}")
                return False

            try:
                with open(self.pokedex_file, "r") as file:
                    pokedex_data = json.load(file)
            except FileNotFoundError:
                pokedex_data = []
            except json.JSONDecodeError:
                print(f"Invalid JSON In {self.pokedex_file}")
                return False

            while len(pokedex_data) <= pokemon_number:
                pokedex_data.append({})

            pokedex_data[pokemon_number] = pokemon_entry

            with open(self.pokedex_file, "w") as file:
                json.dump(pokedex_data, file, indent=2)

            self._pokedex_data = pokedex_data

            print(f"Successfully Saved Pokemon #{pokemon_number} To PokeDex")
            return True

        except Exception as e:
            print(f"Error saving Pokemon To PokeDex: {e}")
            return False


class EmbedUtils:
    @staticmethod
    def create_success_embed(title: str, description: str) -> discord.Embed:
        return discord.Embed(
            title=f"✅ {title}", description=description, color=0x00FF00
        )

    @staticmethod
    def create_error_embed(title: str, description: str) -> discord.Embed:
        return discord.Embed(
            title=f"❌ {title}", description=description, color=0xFF0000
        )

    @staticmethod
    def create_info_embed(
        title: str, description: str, color: int = 0x2F3136
    ) -> discord.Embed:
        return discord.Embed(title=title, description=description, color=color)

    @staticmethod
    def create_profile_embed(user, user_data: tuple) -> discord.Embed:
        net_total = "{:,}".format(user_data[1])
        max_gambled = "{:,}".format(user_data[2])
        gamble_wins = user_data[3]
        gamble_losses = user_data[4]
        gamble_wins_streak = user_data[5]

        total_gambles = gamble_wins + gamble_losses
        win_rate = (
            round((gamble_wins / total_gambles) * 100, 2) if total_gambles > 0 else 0
        )

        embed = discord.Embed(
            title=f"{user.display_name}'s Profile",
            description=(
                f"**Net Total**: {net_total}\n"
                f"**Highest Gamble**: {max_gambled}\n\n"
                f"**Gambles Done**: {total_gambles}\n"
                f"**Wins**: {gamble_wins}\n"
                f"**Losses**: {gamble_losses}\n\n"
                f"**Win Rate**: {win_rate}%\n"
                f"**Win Streak**: {gamble_wins_streak}"
            ),
            color=0xF98D2F,
        )

        embed.timestamp = datetime.datetime.now()

        if user.avatar:
            embed.set_thumbnail(url=user.avatar.url)
        else:
            embed.set_thumbnail(url="https://cdn.discordapp.com/embed/avatars/0.png")

        return embed


class TradeUtils:
    @staticmethod
    def save_trade_data(
        participant1: str, participant2: str, message_link: str
    ) -> None:
        trade_data = {
            "participant1": participant1,
            "participant2": participant2,
            "message_link": message_link,
            "timestamp": datetime.datetime.now().isoformat(),
        }

        try:
            with open("Trades.json", "r") as file:
                trades = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            trades = {"trades": []}

        trades["trades"].append(trade_data)

        with open("Trades.json", "w") as file:
            json.dump(trades, file, indent=4)


def format_number(number: int) -> str:
    return "{:,}".format(number)


def get_ordinal_suffix(position: int) -> str:
    if 10 <= position % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(position % 10, "th")

    return f"{position}{suffix}"


class Logutils:
    @staticmethod
    def log(ctx, command) -> None:
        print(f"Info : {ctx.author} : {command} : {ctx.guild.id}")

        webhook_url = os.getenv("WEBHOOK_URL")

        if webhook_url:

            timestamp = int(datetime.datetime.now().timestamp())
            embed_data = {
                "title": "🔍 Command Execution Log",
                "description": f"**Timestamp :** <t:{timestamp}:t>\n### Command : `{command}`\n\n\n**User :** {ctx.author.mention}\n**Guild :** {ctx.guild.name} [ {ctx.guild.id}]",
                "color": 0x5865F2,
                "thumbnail": {
                    "url": (
                        ctx.author.avatar.url
                        if ctx.author.avatar
                        else "https://cdn.discordapp.com/embed/avatars/0.png"
                    )
                },
            }

            payload = {"embeds": [embed_data]}

            try:
                requests.post(webhook_url, json=payload)

            except requests.RequestException as e:
                print(f"Failed To Send Webhook Log : {e}")


pokemon_utils = PokemonUtils()
embed_utils = EmbedUtils()
trade_utils = TradeUtils()
log_utils = Logutils()
