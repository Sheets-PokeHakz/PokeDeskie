import random
import discord
from config import config
from discord.ext import commands
from utils import pokemon_utils, embed_utils


class PokemonCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["r"])
    async def roll(self, ctx):
        number = random.randint(1, 1017)

        roll_embed = embed_utils.create_info_embed(
            f"Roll Value Is {number}",
            f"Rolled by: {ctx.author.mention}\nRolled Between 1 And 1017",
            color=0x2F3136,
        )
        await ctx.send(embed=roll_embed)

        if ctx.channel.id in config.rand_channels:
            pokemon_data = pokemon_utils.get_pokemon_by_number(number)
            if pokemon_data:
                pokemon_embed = pokemon_utils.create_pokemon_embed(pokemon_data)
                await ctx.send(embed=pokemon_embed)
        else:
            error_embed = embed_utils.create_error_embed(
                "PokeDex Unavailable", "Autodex Only Available In Random Channels"
            )
            await ctx.send(embed=error_embed, delete_after=10)

    @commands.command(aliases=["poke"])
    async def search(self, ctx, *, pokemon_query: str):
        if not pokemon_query:
            await ctx.send("❌ Please Provide A Pokemon Name Or Number To Search For.")
            return

        pokemon_data = None

        if pokemon_query.isdigit():
            number = int(pokemon_query)
            if 1 <= number <= 1017:
                pokemon_data = pokemon_utils.get_pokemon_by_number(number)
        else:

            pokemon_data = pokemon_utils.search_pokemon_by_name(pokemon_query)

        if pokemon_data:
            embed = pokemon_utils.create_pokemon_embed(pokemon_data)
            await ctx.send(embed=embed)
        else:
            error_embed = embed_utils.create_error_embed(
                "Pokemon Not Found",
                f"Could Not Find Pokemon '{pokemon_query}'. Please Check The Spelling Or Try A Different Name.",
            )
            await ctx.send(embed=error_embed)


def setup(bot):
    bot.add_cog(PokemonCog(bot))
