"""
Help command for the PokeDex Discord bot.
"""
import discord
from discord.ext import commands
from config import config


class HelpCog(commands.Cog):
    """Help command for the bot."""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def help(self, ctx):
        """Display help information."""
        # Create main help embed
        embed = discord.Embed(
            title="🔸 PokeDex Bot Help",
            description="Here are all the available commands:",
            color=0x2F3136
        )
        
        # User commands
        embed.add_field(
            name="**+register**",
            value="Register yourself in the gambling system",
            inline=False
        )
        
        embed.add_field(
            name="**+profile** / **+p** [user]",
            value="Display your or another user's gambling profile",
            inline=False
        )
        
        embed.add_field(
            name="**+leaderboard** / **+lb**",
            value="Display the earnings leaderboard",
            inline=False
        )
        
        embed.add_field(
            name="**+leaderboardgambles** / **+lbg**",
            value="Display the most active gamblers leaderboard",
            inline=False
        )
        
        embed.add_field(
            name="**+ping**",
            value="Display bot latency and uptime information",
            inline=False
        )
        
        embed.add_field(
            name="**+roll** / **+r**",
            value="Roll a random Pokemon (works in designated channels)",
            inline=False
        )
        
        embed.add_field(
            name="**+search** / **+poke** <name/number>",
            value="Search for a Pokemon by name or Pokedex number",
            inline=False
        )
        
        embed.set_footer(text="Use +help to see this message again")
        
        await ctx.send(embed=embed)
        
        # Send admin commands if user is admin
        if (ctx.author.guild_permissions.administrator or 
            ctx.author.id == config.admin_user_id):
            
            admin_embed = discord.Embed(
                title="⚡ Admin Commands",
                description="Additional commands for administrators:",
                color=0xFF6B6B
            )
            
            admin_embed.add_field(
                name="**+adminprofile** / **+ap** <user>",
                value="View any user's profile",
                inline=False
            )
            
            admin_embed.add_field(
                name="**+addnet** / **+anet** <user> <amount>",
                value="Add Pokécoins to a user's net total",
                inline=False
            )
            
            admin_embed.add_field(
                name="**+removenet** / **+rnet** <user> <amount>",
                value="Remove Pokécoins from a user's net total",
                inline=False
            )
            
            await ctx.send(embed=admin_embed)


async def setup(bot):
    """Setup function for the cog."""
    await bot.add_cog(HelpCog(bot))
