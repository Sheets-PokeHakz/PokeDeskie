"""
Pokemon-related commands for the PokeDex Discord bot.
"""
import random
import discord
from discord.ext import commands
from utils import pokemon_utils, embed_utils
from config import config


class PokemonCog(commands.Cog):
    """Pokemon-related commands."""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(aliases=["r"])
    async def roll(self, ctx):
        """Roll a random Pokemon."""
        # Generate random Pokemon number
        number = random.randint(1, 1017)
        
        # Create roll announcement embed
        roll_embed = embed_utils.create_info_embed(
            f"Roll Value Is {number}",
            f"Rolled by: {ctx.author.mention}\nRolled between 1 and 1017",
            color=0x2F3136
        )
        await ctx.send(embed=roll_embed)
        
        # Check if we should show the Pokemon details
        if ctx.channel.id in config.rand_channels:
            pokemon_data = pokemon_utils.get_pokemon_by_number(number)
            if pokemon_data:
                pokemon_embed = pokemon_utils.create_pokemon_embed(pokemon_data)
                await ctx.send(embed=pokemon_embed)
        else:
            error_embed = embed_utils.create_error_embed(
                "PokeDex Unavailable",
                "Auto-dex works only in designated random channels."
            )
            await ctx.send(embed=error_embed, delete_after=10)
    
    @commands.command(aliases=["poke"])
    async def search(self, ctx, *, pokemon_query: str):
        """Search for a Pokemon by name or number."""
        if not pokemon_query:
            await ctx.send("❌ Please provide a Pokemon name or number to search for.")
            return
        
        pokemon_data = None
        
        # Check if query is a number
        if pokemon_query.isdigit():
            number = int(pokemon_query)
            if 1 <= number <= 1017:
                pokemon_data = pokemon_utils.get_pokemon_by_number(number)
        else:
            # Search by name
            pokemon_data = pokemon_utils.search_pokemon_by_name(pokemon_query)
        
        if pokemon_data:
            embed = pokemon_utils.create_pokemon_embed(pokemon_data)
            await ctx.send(embed=embed)
        else:
            error_embed = embed_utils.create_error_embed(
                "Pokemon Not Found",
                f"Could not find Pokemon '{pokemon_query}'. Please check the spelling or try a different search term."
            )
            await ctx.send(embed=error_embed)


async def setup(bot):
    """Setup function for the cog."""
    await bot.add_cog(PokemonCog(bot))
