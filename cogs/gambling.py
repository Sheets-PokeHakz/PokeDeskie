import discord
from config import config
from database import database
from discord.ext import commands
from datetime import datetime, timezone
from utils import embed_utils, get_ordinal_suffix

from utils import log_utils


class GamblingCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def register(self, ctx):
        log_utils.log(ctx, "register")

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
        log_utils.log(ctx, "profile")

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
        log_utils.log(ctx, "leaderboard")

        default_embed = discord.Embed(
            title="🏆 Gambling Leaderboard",
            description="Choose A Leaderboard Type Below!",
            color=0xF1C40F,
            timestamp=datetime.now(timezone.utc),
        )
        default_embed.set_footer(
            text=f"Requested By {ctx.author.display_name}",
            icon_url=(
                ctx.author.avatar.url
                if ctx.author.avatar
                else "https://cdn.discordapp.com/embed/avatars/0.png"
            ),
        )

        await ctx.send(embed=default_embed, view=LeaderboardView(ctx.author))


class LeaderboardView(discord.ui.View):
    def __init__(self, author):
        super().__init__(timeout=None)
        self.author = author

    async def on_timeout(self):
        self.disable_all_items()
        await self.message.edit(view=self)

    @discord.ui.select(
        placeholder="Choose a Leaderboard Type!",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(
                label="Net Total Leaderboard",
                description="See the top performers by net total earnings",
                value="net_total",
                emoji="💰",
            ),
            discord.SelectOption(
                label="Gamble Leaderboard",
                description="See the top performers by gambles",
                value="gambles",
                emoji="🎲",
            ),
        ],
    )
    async def select_callback(self, select, interaction):
        if interaction.user != self.author:
            await interaction.response.send_message(
                "You Are Not Authorized To Use This Dropdown!", ephemeral=True
            )
            return

        leaderboard_type = select.values[0]

        if leaderboard_type == "net_total":
            leaderboard_data = database.get_leaderboard_by_net_total(5)
            title = "🏆 Gambling Net Leaderboard"
            value_field_name = "💰 Pokécoins"
            user_position_key = "net_total"

        elif leaderboard_type == "gambles":
            leaderboard_data = database.get_leaderboard_by_gambles(5)
            title = "🏆 Gambling Gamble Leaderboard"
            value_field_name = "🎲 Gamble Wins"
            user_position_key = "gambles"

        else:
            await interaction.response.send_message(
                "Invalid Leaderboard Type!", ephemeral=True
            )
            return

        embed = discord.Embed(
            title=title,
            color=0xF1C40F,
            timestamp=datetime.now(timezone.utc),
        )

        positions = [
            "<:1st:1386587979971297380>",
            "<:2nd:1386588309639270450>",
            "<:3rd:1386587974812303512>",
            "<:4th:1386587984949936299>",
            "<:5th:1386588306061394004>",
        ]

        leaderboard_text = ""

        for index, user_data in enumerate(leaderboard_data):
            if index >= len(positions):
                break

            user_id = user_data[0]
            if leaderboard_type == "net_total":
                value = "{:,}".format(user_data[1])
            elif leaderboard_type == "gambles":
                value = "{:,}".format(user_data[3] + user_data[4])

            leaderboard_text += f"{positions[index]} <@{user_id}>\n"
            leaderboard_text += f"{value_field_name.replace('`', '')} `{value}`\n\n"

        embed.add_field(
            name="━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            value=leaderboard_text.strip(),
            inline=False,
        )

        user_data = database.get_user_details(interaction.user.id)
        if user_data:
            user_position = database.get_user_position_in_leaderboard(
                interaction.user.id, user_position_key
            )
            position_text = get_ordinal_suffix(user_position)

            embed.add_field(
                name="━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                value="\u200b",
                inline=True,
            )

        avatar_url = (
            interaction.user.avatar.url
            if interaction.user.avatar
            else "https://cdn.discordapp.com/embed/avatars/0.png"
        )

        embed.set_footer(
            text=f"{interaction.user.display_name} | Your Rank : {position_text}",
            icon_url=avatar_url,
        )

        await interaction.response.edit_message(embed=embed, view=self)


def setup(bot):
    bot.add_cog(GamblingCog(bot))
