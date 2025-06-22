import discord
import requests
from config import config
from database import database
from discord.ext import commands
from utils import pokemon_utils, embed_utils


def get_pokemon_data(dex_number):
    url = f"https://pokeapi.co/api/v2/pokemon/{dex_number}"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Failed To Fetch Pokémon #{dex_number}")
        return None

    data = response.json()

    species_url = data["species"]["url"]
    species_response = requests.get(species_url)
    species_data = (
        species_response.json() if species_response.status_code == 200 else {}
    )

    region_map = {
        1: "Kanto",
        2: "Johto",
        3: "Hoenn",
        4: "Sinnoh",
        5: "Unova",
        6: "Kalos",
        7: "Alola",
        8: "Galar",
        9: "Paldea",
    }

    generation_id = (
        species_data.get("generation", {}).get("url", "").split("/")[-2]
        if species_data.get("generation")
        else "1"
    )
    try:
        gen_num = int(generation_id)
        region = region_map.get(gen_num, "Kanto")
    except (ValueError, TypeError):
        region = "Kanto"

    name = data["name"].capitalize()

    types = [ptype["type"]["name"].capitalize() for ptype in data["types"]]

    stats = {}
    for stat in data["stats"]:
        stat_name = stat["stat"]["name"]
        if stat_name == "hp":
            stats["HP"] = stat["base_stat"]
        elif stat_name == "attack":
            stats["Attack"] = stat["base_stat"]
        elif stat_name == "defense":
            stats["Defense"] = stat["base_stat"]
        elif stat_name == "special-attack":
            stats["Sp. Atk"] = stat["base_stat"]
        elif stat_name == "special-defense":
            stats["Sp. Def"] = stat["base_stat"]
        elif stat_name == "speed":
            stats["Speed"] = stat["base_stat"]

    pokemon_entry = {
        "title": f"#{data['id']} — {name}",
        "color": 16685769,
        "fields": [
            {"name": "Types", "value": "\n".join(types), "inline": False},
            {"name": "Region", "value": region, "inline": False},
            {"name": "Catchable", "value": "Yes", "inline": False},
            {
                "name": "Base Stats",
                "value": "\n".join(
                    [
                        f"**{stat_name}:** {stat_value}"
                        for stat_name, stat_value in stats.items()
                    ]
                ),
                "inline": False,
            },
            {"name": "Names", "value": f"🇬🇧 {name}", "inline": False},
            {
                "name": "Appearance",
                "value": f"Height: {data['height'] / 10:.1f} m\nWeight: {data['weight'] / 10:.1f} kg",
                "inline": False,
            },
        ],
        "thumbnail": {"url": None},
        "image": {"url": f"https://cdn.poketwo.net/images/{data['id']}.png"},
    }

    print(f"Fetched Pokémon #{data['id']} - {name}")

    return pokemon_entry


class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def is_admin_or_owner(self, user):
        return user.id in config.admin_uids or user.id == self.bot.owner_id

    @commands.command(aliases=["ap"])
    async def adminprofile(self, ctx, member: discord.Member = None):
        print(f"Info : {ctx.author} : {ctx.guild.name} : {ctx.guild.id}")

        if not self.is_admin_or_owner(ctx.author):
            await ctx.send(
                "❌ You Don't Have Permission To Use This Command.", ephemeral=True
            )
            return

        if member is None:
            member = ctx.author

        user_data = database.get_user_details(member.id)

        if user_data is None:
            embed = embed_utils.create_error_embed(
                "Profile Not Found",
                "This user is not registered. They need to use `+register` first.",
            )
            await ctx.send(embed=embed)
        else:
            embed = embed_utils.create_profile_embed(member, user_data)
            await ctx.send(embed=embed)

    @commands.command(aliases=["anet"])
    async def addnet(self, ctx, member: discord.Member = None, amount: int = 0):
        if not self.is_admin_or_owner(ctx.author):
            await ctx.send("❌ You Don't Have Permission To Use This Command.")
            return

        if member is None:
            await ctx.send("❌ Please Specify Member To Add Coins To.")
            return

        if amount <= 0:
            await ctx.send("❌ Amount Must Be Positive.")
            return

        if database.get_user_details(member.id) is None:
            database.register_user(member.id)

        database.update_user_net_total(member.id, amount)

        embed = embed_utils.create_success_embed(
            "Coins Added", f"Added {amount:,} Pokécoins To {member.mention}"
        )
        await ctx.send(embed=embed)

    @commands.command(aliases=["rnet"])
    async def removenet(self, ctx, member: discord.Member = None, amount: int = 0):
        if not self.is_admin_or_owner(ctx.author):
            await ctx.send("❌ You Don't Have Permission To Use This Command.")
            return

        if member is None:
            await ctx.send("❌ Please Specify Member To Remove Coins From.")
            return

        if amount <= 0:
            await ctx.send("❌ Amount Must Be Positive.")
            return

        if database.get_user_details(member.id) is None:
            await ctx.send("❌ User Is Not Registered.")
            return

        database.update_user_net_total(member.id, -amount)

        embed = embed_utils.create_success_embed(
            "Coins Removed", f"Removed {amount:,} Pokécoins From {member.mention}"
        )
        await ctx.send(embed=embed)

    @commands.command(aliases=["pupdate"])
    async def pokeupdate(self, ctx, start_number: int = None, end_number: int = None):
        if not self.is_admin_or_owner(ctx.author):
            await ctx.send("❌ You Don't Have Permission To Use This Command.")
            return

        if start_number is None or end_number is None:
            await ctx.send(
                "❌ Please Provide Start And End Pokémon Numbers (e.g., `+pupdate 1 151`)"
            )
            return

        if start_number < 1 or end_number < 1:
            await ctx.send("❌ Pokémon Numbers Must Be Positive.")
            return

        if start_number > end_number:
            await ctx.send("❌ Start Number Must Be Less Than Or Equal To End Number.")
            return

        status_embed = embed_utils.create_success_embed(
            "PokeDex Update Started",
            f"Updating PokeDex Entries From #{start_number} To #{end_number}...",
        )
        status_message = await ctx.send(embed=status_embed)

        successful_updates = 0
        skipped_updates = 0
        failed_updates = 0

        for pokemon_number in range(start_number, end_number + 1):
            try:
                pokemon_entry = get_pokemon_data(pokemon_number)

                if pokemon_entry is None:
                    failed_updates += 1

                    print(f"Failed To Fetch Pokemon Data For #{pokemon_number}")
                    continue

                success = pokemon_utils.save_pokemon_to_dex(pokemon_entry)

                if success:
                    successful_updates += 1
                    print(f"Successfully Updated Pokemon #{pokemon_number}")
                else:
                    failed_updates += 1
                    print(f"Failed To Save Pokemon #{pokemon_number}")

                if pokemon_number % 10 == 0:
                    progress_embed = embed_utils.create_success_embed(
                        "PokeDex Update In Progress",
                        f"Progress : {pokemon_number}/{end_number}\n"
                        f"> Updated : {successful_updates}\n"
                        f"> Skipped : {skipped_updates}\n"
                        f"> Failed : {failed_updates}",
                    )
                    await status_message.edit(embed=progress_embed)

            except Exception as e:
                failed_updates += 1
                print(f"Error Updating Pokemon Data #{pokemon_number}: {e}")
                continue

        if successful_updates > 0:
            final_embed = embed_utils.create_success_embed(
                "PokeDex Update Complete",
                f"> Successfully Updated : {successful_updates} Pokémon\n"
                f"> Failed : {failed_updates} Pokémon",
            )
        else:
            final_embed = embed_utils.create_error_embed(
                "PokeDex Update Failed",
                f"> Skipped: {skipped_updates}\n" f"> Failed: {failed_updates}",
            )

        await status_message.edit(embed=final_embed)

    @commands.command(aliases=["padd"])
    async def pokeadd(self, ctx, message: discord.Message = None):
        if not self.is_admin_or_owner(ctx.author):
            await ctx.send("❌ You Don't Have Permission To Use This Command.")
            return

        if message is None:
            await ctx.send("❌ Please Provide A Message To Add Pokemon Data From.")
            return

        if not message.embeds:
            await ctx.send("❌ The Provided Message Does Not Contain Any Embeds.")
            return

        embed = message.embeds[0]

        title = embed.title
        if title and "—" in title:
            parts = title.split("—")
            pokemon_number = parts[0].strip().replace("#", "")
            pokemon_name = parts[1].strip()
        else:
            await ctx.send("❌ Unable To Pokemon Data")
            return

        description = embed.description or ""
        image_url = embed.image.url if embed.image else ""

        pokemon_data = {
            "number": pokemon_number,
            "name": pokemon_name,
            "description": description,
            "image_url": image_url,
        }

        for field in embed.fields:
            field_name = field.name.lower()
            field_value = field.value

            if field_name == "types":
                types = []
                for line in field_value.split("\n"):
                    if line.strip():
                        type_name = line.split()[-1]
                        types.append(type_name)
                pokemon_data["types"] = types

            elif field_name == "region":
                pokemon_data["region"] = field_value

            elif field_name == "base stats":
                stats = {}
                for line in field_value.split("\n"):
                    if ":" in line:
                        stat_name, stat_value = line.split(":", 1)
                        stat_name = stat_name.strip("*").strip()
                        stat_value = stat_value.strip()
                        if stat_name != "Total":
                            stats[stat_name.lower().replace(" ", "_")] = stat_value
                pokemon_data["base_stats"] = stats

            elif field_name == "appearance":
                for line in field_value.split("\n"):
                    if line.startswith("Height:"):
                        pokemon_data["height"] = line.split(":", 1)[1].strip()
                    elif line.startswith("Weight:"):
                        pokemon_data["weight"] = line.split(":", 1)[1].strip()

        number = int(pokemon_data["number"])

        pokemon_data_from_dex = pokemon_utils.get_pokemon_by_number(number=number)
        if pokemon_data_from_dex:
            await ctx.send("❌ Pokemon Already Exists In The PokeDex.")
            return

        # Converting To The Required Json Format
        pokedex_entry = {
            "title": f"#{pokemon_data['number']} — {pokemon_data['name']}",
            "color": 16685769,
            "fields": [],
            "thumbnail": {"url": None},
            "image": {"url": pokemon_data.get("image_url", "")},
        }

        # Add Types Field
        if "types" in pokemon_data:
            types_value = "\n".join(pokemon_data["types"])
            pokedex_entry["fields"].append(
                {"name": "Types", "value": types_value, "inline": False}
            )

        # Add Region Field
        if "region" in pokemon_data:
            pokedex_entry["fields"].append(
                {"name": "Region", "value": pokemon_data["region"], "inline": False}
            )

        # Add Catchable Field
        pokedex_entry["fields"].append(
            {"name": "Catchable", "value": "Yes", "inline": False}
        )

        # Add Base Stats Field
        if "base_stats" in pokemon_data:
            stats_lines = []
            stat_names = {
                "hp": "HP",
                "attack": "Attack",
                "defense": "Defense",
                "sp_atk": "Sp. Atk",
                "sp_def": "Sp. Def",
                "speed": "Speed",
            }
            for stat_key, stat_display in stat_names.items():
                if stat_key in pokemon_data["base_stats"]:
                    stats_lines.append(
                        f"**{stat_display}:** {pokemon_data['base_stats'][stat_key]}"
                    )

                if stats_lines:
                    pokedex_entry["fields"].append(
                        {
                            "name": "Base Stats",
                            "value": "\n".join(stats_lines),
                            "inline": False,
                        }
                    )

        # Add Names Field
        pokedex_entry["fields"].append(
            {"name": "Names", "value": f"🇬🇧 {pokemon_data['name']}", "inline": False}
        )

        # Add Appearance Field
        if "height" in pokemon_data or "weight" in pokemon_data:
            appearance_lines = []
            if "height" in pokemon_data:
                appearance_lines.append(f"Height: {pokemon_data['height']}")
            if "weight" in pokemon_data:
                appearance_lines.append(f"Weight: {pokemon_data['weight']}")

            if appearance_lines:
                pokedex_entry["fields"].append(
                    {
                        "name": "Appearance",
                        "value": "\n".join(appearance_lines),
                        "inline": False,
                    }
                )

        success = pokemon_utils.save_pokemon_to_dex(pokedex_entry)

        if success:
            embed = embed_utils.create_success_embed(
                "Pokémon Added",
                f"Successfully added **{pokemon_data['name']}** (#{pokemon_data['number']}) to the PokéDex!",
            )
            await ctx.send(embed=embed)
        else:
            embed = embed_utils.create_error_embed(
                "Failed to Add Pokémon",
                f"There was an error adding **{pokemon_data['name']}** to the PokéDex. Please check the logs.",
            )
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(AdminCog(bot))
