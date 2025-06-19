import discord
from config import config
from discord.ext import commands


class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def help(self, ctx):
        embed = discord.Embed(
            title="🔸 PokeDex Bot Help",
            description="Here Are All The Commands To Be Used!",
            color=0x2F3136
        )
        
        embed.add_field(
            name="**+register**",
            value="Register Yourself To The Gambling System",
            inline=False
        )
        
        embed.add_field(
            name="**+profile** / **+p** [user]",
            value="Display Your Or Another User's Profile",
            inline=False
        )
        
        embed.add_field(
            name="**+leaderboard** / **+lb**",
            value="Display The Earnings Leaderboard",
            inline=False
        )
        
        embed.add_field(
            name="**+leaderboardgambles** / **+lbg**",
            value="Display The Most Active Gamblers Leaderboard",
            inline=False
        )
        
        embed.add_field(
            name="**+ping**",
            value="Display Bot Latency And Uptime",
            inline=False
        )
        
        embed.add_field(
            name="**+roll** / **+r**",
            value="Roll Command ( Not Official )",
            inline=False
        )
        
        embed.add_field(
            name="**+search** / **+poke** <name/number>",
            value="Search For A Pokemon By Name Or Number",
            inline=False
        )
        
        embed.set_footer(text="Use +help To View This Message Again")
        
        await ctx.send(embed=embed)
        
        if (ctx.author.guild_permissions.administrator or 
            ctx.author.id == config.admin_user_id):
            
            admin_embed = discord.Embed(
                title="⚡ Admin Commands",
                description="Additional Admin Commands",
                color=0xFF6B6B
            )
            
            admin_embed.add_field(
                name="**+adminprofile** / **+ap** <user>",
                value="View A User's Profile With Admin Privileges",
                inline=False
            )
            
            admin_embed.add_field(
                name="**+addnet** / **+anet** <user> <amount>",
                value="Add Pokécoins To A User's Net Total",
                inline=False
            )
            
            admin_embed.add_field(
                name="**+removenet** / **+rnet** <user> <amount>",
                value="Remove Pokécoins From A User's Net Total",
                inline=False
            )
            
            await ctx.send(embed=admin_embed)


def setup(bot):
    bot.add_cog(HelpCog(bot))
