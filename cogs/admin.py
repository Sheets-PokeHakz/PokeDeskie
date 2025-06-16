import discord
from config import config
from database import database
from utils import embed_utils
from discord.ext import commands


class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def is_admin_or_owner(self, user):
        return user.guild_permissions.administrator or user.id == config.admin_user_id

    @commands.command(aliases=["ap"])
    async def adminprofile(self, ctx, member: discord.Member = None):
        if not self.is_admin_or_owner(ctx.author):
            await ctx.respond(
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
            await ctx.respond(embed=embed)
        else:
            embed = embed_utils.create_profile_embed(member, user_data)
            await ctx.respond(embed=embed)

    @commands.command(aliases=["anet"])
    async def addnet(self, ctx, member: discord.Member = None, amount: int = 0):
        if not self.is_admin_or_owner(ctx.author):
            await ctx.respond("❌ You Don't Have Permission To Use This Command.")
            return

        if member is None:
            await ctx.respond("❌ Please Specify Member To Add Coins To.")
            return

        if amount <= 0:
            await ctx.respond("❌ Amount Must Be Positive.")
            return

        if database.get_user_details(member.id) is None:
            database.register_user(member.id)

        database.update_user_net_total(member.id, amount)

        embed = embed_utils.create_success_embed(
            "Coins Added", f"Added {amount:,} Pokécoins To {member.mention}"
        )
        await ctx.respond(embed=embed)

    @commands.command(aliases=["rnet"])
    async def removenet(self, ctx, member: discord.Member = None, amount: int = 0):
        if not self.is_admin_or_owner(ctx.author):
            await ctx.respond("❌ You Don't Have Permission To Use This Command.")
            return

        if member is None:
            await ctx.respond("❌ Please Specify Member To Remove Coins From.")
            return

        if amount <= 0:
            await ctx.respond("❌ Amount Must Be Positive.")
            return

        if database.get_user_details(member.id) is None:
            await ctx.respond("❌ User Is Not Registered.")
            return

        database.update_user_net_total(member.id, -amount)

        embed = embed_utils.create_success_embed(
            "Coins Removed", f"Removed {amount:,} Pokécoins From {member.mention}"
        )
        await ctx.respond(embed=embed)


async def setup(bot):
    await bot.add_cog(AdminCog(bot))
