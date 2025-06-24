import io
import discord
import aiohttp
from config import config
from database import database
from discord.ext import commands
from datetime import datetime, timezone
from PIL import Image, ImageDraw, ImageFont
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

        ctx.typing()

        member = member or ctx.author

        user_data = database.get_user_details(member.id)
        if not user_data:
            embed = embed_utils.create_error_embed(
                "Profile Not Found",
                "This user is not registered. They need to use `+register` first.",
            )
            return await ctx.send(embed=embed)

        (
            user_id,
            net_total,
            max_gambled,
            gamble_wins,
            gamble_losses,
            wins_streak,
            losses_streak,
            register_date,
        ) = user_data

        total_gambles = gamble_wins + gamble_losses
        win_rate = (
            round((gamble_wins / total_gambles) * 100, 1) if total_gambles > 0 else 0
        )

        background = Image.open("images/2.png").convert("RGBA")
        draw = ImageDraw.Draw(background)

        avatar_url = member.display_avatar.url

        if not avatar_url:
            avatar_url = "https://cdn.discordapp.com/embed/avatars/0.png"

        async with aiohttp.ClientSession() as session:
            async with session.get(avatar_url) as resp:
                if resp.status != 200:
                    return await ctx.send("Could Not Load Avatar.")

                avatar_bytes = await resp.read()

        avatar = Image.open(io.BytesIO(avatar_bytes)).convert("RGBA")

        high_res_size = (200, 200)
        avatar = avatar.resize(high_res_size, Image.LANCZOS)

        mask = Image.new("L", high_res_size, 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse((0, 0, high_res_size[0], high_res_size[1]), fill=255)

        avatar.putalpha(mask)

        final_size = (100, 100)
        avatar = avatar.resize(final_size, Image.LANCZOS)

        avatar_position = (60, 75)
        background.paste(avatar, avatar_position, avatar)

        font = ImageFont.truetype("fonts/Michroma-Regular.ttf", 24)

        username_fill = (255, 255, 255, 255)  # White
        outline_color = (0, 0, 0, 255)  # Black

        username_position = (175, 100)

        for offset in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            draw.text(
                (username_position[0] + offset[0], username_position[1] + offset[1]),
                f"{member.name}",
                font=font,
                fill=outline_color,
            )

        draw.text(username_position, f"{member.name}", font=font, fill=username_fill)

        if isinstance(register_date, str):
            register_date = datetime.fromisoformat(register_date)

        reg_date = register_date.strftime("%d • %m • %Y")

        reg_font = ImageFont.truetype("fonts/Michroma-Regular.ttf", 14)

        date_fill = (255, 255, 255, 255)
        outline_color = (0, 0, 0, 255)

        reg_position = (197, 193)

        for offset in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            draw.text(
                (reg_position[0] + offset[0], reg_position[1] + offset[1]),
                f"{reg_date}",
                font=reg_font,
                fill=outline_color,
            )

        draw.text(reg_position, f"{reg_date}", font=reg_font, fill=date_fill)

        formatted_total = f"{net_total:,}"

        net_font = ImageFont.truetype("fonts/Arial.ttf", 20)

        net_fill = (255, 255, 255, 255)  # White
        outline_color = (0, 0, 0, 255)  # Black

        net_position = (525, 88)

        for offset in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            draw.text(
                (net_position[0] + offset[0], net_position[1] + offset[1]),
                formatted_total,
                font=net_font,
                fill=outline_color,
            )

        draw.text(net_position, formatted_total, font=net_font, fill=net_fill)

        formatted_highest = f"{max_gambled:,}"

        net_font = ImageFont.truetype("fonts/Arial.ttf", 20)

        net_fill = (255, 255, 255, 255)  # White
        outline_color = (0, 0, 0, 255)  # Black

        net_position = (574, 140)

        for offset in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            draw.text(
                (net_position[0] + offset[0], net_position[1] + offset[1]),
                formatted_highest,
                font=net_font,
                fill=outline_color,
            )

        draw.text(net_position, formatted_highest, font=net_font, fill=net_fill)

        total_gambles = gamble_wins + gamble_losses
        formatted_done = f"{total_gambles:,}"

        net_font = ImageFont.truetype("fonts/Arial.ttf", 20)

        net_fill = (255, 255, 255, 255)  # White
        outline_color = (0, 0, 0, 255)  # Black

        net_position = (530, 182)

        for offset in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            draw.text(
                (net_position[0] + offset[0], net_position[1] + offset[1]),
                formatted_done,
                font=net_font,
                fill=outline_color,
            )

        draw.text(net_position, formatted_done, font=net_font, fill=net_fill)

        formatted_win = f"{gamble_wins:,}"

        net_font = ImageFont.truetype("fonts/Arial.ttf", 18)

        net_fill = (255, 255, 255, 255)  # White
        outline_color = (0, 0, 0, 255)  # Black

        net_position = (506, 234)

        for offset in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            draw.text(
                (net_position[0] + offset[0], net_position[1] + offset[1]),
                formatted_win,
                font=net_font,
                fill=outline_color,
            )

        draw.text(net_position, formatted_win, font=net_font, fill=net_fill)

        formatted_winrate = f"{win_rate}%"

        net_font = ImageFont.truetype("fonts/Arial.ttf", 18)

        net_fill = (255, 255, 255, 255)  # White
        outline_color = (0, 0, 0, 255)  # Black

        net_position = (682, 233)

        for offset in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            draw.text(
                (net_position[0] + offset[0], net_position[1] + offset[1]),
                formatted_winrate,
                font=net_font,
                fill=outline_color,
            )

        draw.text(net_position, formatted_winrate, font=net_font, fill=net_fill)

        formatted_winstreak = f"{wins_streak:,}"

        net_font = ImageFont.truetype("fonts/Arial.ttf", 18)

        net_fill = (255, 255, 255, 255)
        outline_color = (0, 0, 0, 255)

        net_position = (698, 306)

        for offset in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            draw.text(
                (net_position[0] + offset[0], net_position[1] + offset[1]),
                formatted_winstreak,
                font=net_font,
                fill=outline_color,
            )

        draw.text(net_position, formatted_winstreak, font=net_font, fill=net_fill)

        formatted_loss = f"{gamble_losses:,}"

        net_font = ImageFont.truetype("fonts/Arial.ttf", 18)

        net_fill = (255, 255, 255, 255)  # White
        outline_color = (0, 0, 0, 255)  # Black

        net_position = (506, 307)

        for offset in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            draw.text(
                (net_position[0] + offset[0], net_position[1] + offset[1]),
                formatted_loss,
                font=net_font,
                fill=outline_color,
            )

        draw.text(net_position, formatted_loss, font=net_font, fill=net_fill)

        buffer = io.BytesIO()
        background.save(buffer, format="PNG")
        buffer.seek(0)

        file = discord.File(fp=buffer, filename="profile.png")
        await ctx.send(file=file)

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
            discord.SelectOption(
                label="Gamble Win Leaderboard",
                description="See the top performers by gamble wins",
                value="wins",
                emoji="🏆",
            ),
            discord.SelectOption(
                label="Gamble Loss Leaderboard",
                description="See the top performers by gamble losses",
                value="losses",
                emoji="❌",
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
            value_field_name = "🎲 Total Gambles"
            user_position_key = "gambles"

        elif leaderboard_type == "wins":
            leaderboard_data = database.get_leaderboard_by_wins(5)
            title = "🏆 Gambling Win Leaderboard"
            value_field_name = "🏆 Total Wins"
            user_position_key = "wins"

        elif leaderboard_type == "losses":
            leaderboard_data = database.get_leaderboard_by_losses(5)
            title = "🏆 Gambling Loss Leaderboard"
            value_field_name = "❌ Total Losses"
            user_position_key = "losses"

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
            elif leaderboard_type == "wins":
                value = "{:,}".format(user_data[3])
            elif leaderboard_type == "losses":
                value = "{:,}".format(user_data[4])

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
