import discord
from config import config
from database import database
from discord.ext import commands
from utils import embed_utils, get_ordinal_suffix


class GamblingCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def register(self, ctx):
        if database.register_user(ctx.author.id):
            embed = embed_utils.create_success_embed(
                "Registration Successful",
                "You Have Been Successfully Registered In The Gambling System!",
            )
        else:
            embed = embed_utils.create_error_embed(
                "Registration Failed",
                "You Are Already Registered In The Gambling System!",
            )

        await ctx.send(embed=embed)

    @commands.command(aliases=["p"])
    async def profile(self, ctx, member: discord.Member = None):
        target_user = member or ctx.author
        user_data = database.get_user_details(target_user.id)

        if user_data is None:
            embed = embed_utils.create_error_embed(
                "Profile Not Found", "Please Register It First Using `+register`"
            )
        else:
            embed = embed_utils.create_profile_embed(target_user, user_data)

        await ctx.send(embed=embed)

    @commands.command(aliases=["lb"])
    async def leaderboard(self, ctx):
        leaderboard_data = database.get_leaderboard_by_net_total(5)

        embed = discord.Embed(
            title="💰 **GAMBLING LEADERBOARD** 💰",
            description="```Top Gamblers by Net Total Pokécoins```",
            color=0xFFD700,
        )
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/emojis/1236697996377325709.png"
        )

        # Emoji Positions
        positions = [
            "<:1st:1236697996377325709> **1st Place**",
            "<:2nd:1236697993973989427> **2nd Place**",
            "<:3rd:1236697991428177940> **3rd Place**",
            "<:4th:1236697999095234600> **4th Place**",
            "<:5th:1236698001205100717> **5th Place**",
        ]

        for index, user_data in enumerate(leaderboard_data):
            if index >= len(positions):
                break

            user_id = user_data[0]
            net_total = "{:,}".format(user_data[1])

            member = ctx.guild.get_member(int(user_id))
            display_name = member.display_name if member else f"User {user_id}"

            embed.add_field(
                name="━━━━━━━━━━━━━━━━━━━━━━━━",
                value=f"{positions[index]}\n💎 **<@{user_id}>**\n💰 `{net_total}` Pokécoins",
                inline=False,
            )

        user_data = database.get_user_details(ctx.author.id)
        if user_data:
            user_position = database.get_user_position_in_leaderboard(
                ctx.author.id, "net_total"
            )
            position_text = get_ordinal_suffix(user_position)

            avatar_url = (
                ctx.author.avatar.url
                if ctx.author.avatar
                else "https://cdn.discordapp.com/embed/avatars/0.png"
            )
            embed.set_footer(
                text=f"🏆 You are ranked {position_text} on the leaderboard!",
                icon_url=avatar_url,
            )

        embed.add_field(
            name="━━━━━━━━━━━━━━━━━━━━━━━━",
            value="🎯 *Keep gambling to climb the ranks!*",
            inline=False,
        )

        await ctx.send(embed=embed)

    @commands.command(aliases=["lbg"])
    async def leaderboardgambles(self, ctx):
        leaderboard_data = database.get_leaderboard_by_gambles(5)

        embed = discord.Embed(
            title="🎲 **GAMBLE ACTIVITY LEADERBOARD** 🎲",
            description="```Most Active Gamblers by Total Gambles```",
            color=0xFF6B35,
        )
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/emojis/1236697996377325709.png"
        )

        # Emoji Positions
        positions = [
            "<:1st:1236697996377325709> **1st Place**",
            "<:2nd:1236697993973989427> **2nd Place**",
            "<:3rd:1236697991428177940> **3rd Place**",
            "<:4th:1236697999095234600> **4th Place**",
            "<:5th:1236698001205100717> **5th Place**",
        ]

        for index, user_data in enumerate(leaderboard_data):
            if index >= len(positions):
                break

            user_id = user_data[0]
            total_gambles = user_data[-1]

            member = ctx.guild.get_member(int(user_id))
            display_name = member.display_name if member else f"User {user_id}"

            embed.add_field(
                name="━━━━━━━━━━━━━━━━━━━━━━━━",
                value=f"{positions[index]}\n🎰 **<@{user_id}>**\n🎲 `{total_gambles}` Total Gambles",
                inline=False,
            )

        user_data = database.get_user_details(ctx.author.id)
        if user_data:
            user_position = database.get_user_position_in_leaderboard(
                ctx.author.id, "gambles"
            )
            position_text = get_ordinal_suffix(user_position)

            avatar_url = (
                ctx.author.avatar.url
                if ctx.author.avatar
                else "https://cdn.discordapp.com/embed/avatars/0.png"
            )
            embed.set_footer(
                text=f"🏆 You are ranked {position_text} on the activity leaderboard!",
                icon_url=avatar_url,
            )

        embed.add_field(
            name="━━━━━━━━━━━━━━━━━━━━━━━━",
            value="🔥 *Keep gambling to become the most active player!*",
            inline=False,
        )

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(GamblingCog(bot))
