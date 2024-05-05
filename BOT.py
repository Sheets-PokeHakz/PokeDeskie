from flask import Flask, render_template
from threading import Thread

app = Flask(__name__)


@app.route("/")
def index():
    return """<body style="margin: 0; padding: 0;">
    <iframe width="100%" height="100%" src="https://astrumbot.vercel.app/" frameborder="0" allowfullscreen></iframe>
  </body>"""


def run():
    app.run(host="0.0.0.0", port=8080)


def keep_alive():
    t = Thread(target=run)
    t.start()


keep_alive()

import re
import sys
import json
import random
import asyncio
import sqlite3
import discord
import datetime
import traceback
from discord.ext import commands

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="+", intents=intents)

bot.remove_command("help")

conn = sqlite3.connect("Profile.db")
c = conn.cursor()

c.execute(
    """
    CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY,
        net_total INTEGER DEFAULT 0,
        max_gambled INTEGER DEFAULT 0,
        gamble_wins INTEGER DEFAULT 0,
        gamble_losses INTEGER DEFAULT 0,
        gamble_wins_streak INTEGER DEFAULT 0,
        gamble_losses_streak INTEGER DEFAULT 0
    )
"""
)

conn.commit()
c.close()

# Register User


def register_user(user_id):
    conn = sqlite3.connect("Profile.db")
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user_data = c.fetchone()

    if user_data is None:
        c.execute(
            "INSERT OR IGNORE INTO users (user_id, net_total, max_gambled, gamble_wins, gamble_losses) VALUES (?, ?, ?, ?, ?)",
            (user_id, 0, 0, 0, 0),
        )

        conn.commit()
        c.close()

    conn.commit()
    c.close()


# Get User Details


def get_user_details(user_id):
    conn = sqlite3.connect("Profile.db")
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user_data = c.fetchone()

    if user_data is None:
        conn.commit()
        c.close()

        return None

    else:
        conn.commit()
        c.close()

        return user_data


@bot.event
async def on_ready():
    print(f"======================= ")
    print(f"STATUS : ONLINE")
    print(f"======================= ")
    print(f"BOT : {bot.user}")

    # await bot.change_presence(status=discord.Status.idle,activity=discord.Game(name="Maintainance"))
    await bot.change_presence(activity=discord.Game(name="PokeDex | +help"))

    start_time = datetime.datetime.now()
    bot.start_time = start_time


@bot.command()
async def register(ctx):

    if get_user_details(ctx.author.id) is None:
        register_user(ctx.author.id)

        embed = discord.Embed(
            title="*Registration Successful*",
            description="### You Have Been Successfully Registered",
            color=0x2F3136,
        )

        await ctx.send(embed=embed)

    else:
        embed = discord.Embed(
            title="*Registration Failed*",
            description="### You Are Already Registered",
            color=0x2F3136,
        )

        await ctx.send(embed=embed)


@bot.command(aliases=["profile", "p"])
async def profile(ctx):

    user_data = get_user_details(ctx.author.id)

    if user_data is None:
        embed = discord.Embed(
            title="*Profile Not Found*",
            description="### Please Register First",
            color=0x2F3136,
        )

        await ctx.send(embed=embed)

    else:

        net_total = user_data[1]
        max_gambled = user_data[2]
        gamble_wins = user_data[3]
        gamble_losses = user_data[4]
        gamble_wins_streak = user_data[5]
        gamble_losses_streak = user_data[6]

        if gamble_wins + gamble_losses != 0:
            win_rate = round((gamble_wins / (gamble_wins + gamble_losses)) * 100, 2)

        else:
            win_rate = 0

        gamble_done = gamble_wins + gamble_losses

        embed = discord.Embed(
            title=f"{ctx.author.display_name}'s **Profile**",
            description="\u200b",
            color=0x2F3136,
        )
        embed.add_field(name="Net Total", value=f"{net_total} Coins", inline=True)

        if ctx.author.avatar is None:
            embed.set_thumbnail(url="https://cdn.discordapp.com/embed/avatars/0.png")

        else:
            embed.set_thumbnail(url=ctx.author.avatar.url)

        embed.add_field(name="Max Gambled", value=f"{max_gambled} Coins", inline=True)
        embed.add_field(
            name="---------------------------------------", value="\u200b", inline=False
        )
        embed.add_field(name="Gambles", value=gamble_done, inline=True)
        embed.add_field(name="Wins", value=gamble_wins, inline=True)
        embed.add_field(name="Losses", value=gamble_losses, inline=True)
        embed.add_field(
            name="---------------------------------------", value="\u200b", inline=False
        )
        embed.add_field(name="Win Rate", value=f"{win_rate} %", inline=True)
        embed.add_field(name="Wins Streak", value=gamble_wins_streak, inline=True)
        embed.add_field(name="Losses Streak", value=gamble_losses_streak, inline=True)

        await ctx.send(embed=embed)


@bot.command(aliases=["lb"])
async def leaderboard(ctx):
    conn = sqlite3.connect("Profile.db")
    c = conn.cursor()

    c.execute("SELECT * FROM users ORDER BY net_total DESC")
    user_data = c.fetchall()

    embed = discord.Embed(title="Gambling Leaderboard", description="Gamblers With The Highest Earnings.", color=0x2F3136)

    positions = [":1st: 1st Place", ":2nd: 2nd Place", ":3rd: 3rd Place", ":4th: 4th Place", ":5th: 5th Place"]
    emoji_ids = ["1236697996377325709", "1236697993973989427", "1236697991428177940", "1236697999095234600", "1236698001205100717"]

    for index, user in enumerate(user_data[:5]):
        user_id = user[0]
        net_total = user[1]

        member = ctx.guild.get_member(int(user_id))

        if member is not None:
            name = member.display_name
        else:
            name = user_id

        position = positions[index]
        emoji_id = emoji_ids[index]

        embed.add_field(
            name=f"{position} {emoji_id}",
            value=f"<@{user_id}> {net_total} Pokécoins",
            inline=False
        )

    user_net_total = get_user_details(ctx.author.id)[1]
    user_position = sum(1 for user in user_data if user[1] > user_net_total) + 1


    embed.set_footer(text=f"You Are At {user_position} On Leaderboard", icon_url=ctx.author.avatar.url)

    await ctx.send(embed=embed)


@bot.command()
async def ping(ctx):

    latency = bot.latency * 1000
    uptime = datetime.datetime.now() - bot.start_time

    uptime_seconds = uptime.total_seconds()
    uptime_str = str(datetime.timedelta(seconds=uptime_seconds)).split(".")[0]

    num_servers = len(bot.guilds)

    embed = discord.Embed(title="🏓 Pong", color=0x2F3136)

    embed.add_field(name="Uptime", value=uptime_str, inline=False)
    embed.add_field(name="Latency", value=f"{latency:.2f}ms", inline=False)
    embed.add_field(name="Servers", value=num_servers, inline=False)

    await ctx.send(embed=embed)


@bot.event
async def on_message(ctx):

    # Carl Bot Support

    if ctx.author.id == 235148962103951360:

        if (
            ctx.channel.id == 1167681875540713562
            or ctx.channel.id == 1168924782876692525
        ):
            with open("PokeDex.json", "r") as file:
                embed_data = json.load(file)

            if ctx.embeds:
                for embed in ctx.embeds:
                    if "rolls" in embed.title:
                        title_parts = embed.title.split(" ")
                        rolls_index = title_parts.index("rolls")
                        number = title_parts[rolls_index + 1].strip("**")
                        number = number.strip("()")
                        number = int(number)

                        if 1 <= number <= 1017:
                            stats = []
                            for field in embed_data[number]["fields"]:
                                if field["name"] == "Base Stats":
                                    hp = int(
                                        field["value"]
                                        .split("**HP:** ")[1]
                                        .split("\n")[0]
                                    )
                                    attack = int(
                                        field["value"]
                                        .split("**Attack:** ")[1]
                                        .split("\n")[0]
                                    )
                                    defense = int(
                                        field["value"]
                                        .split("**Defense:** ")[1]
                                        .split("\n")[0]
                                    )
                                    sp_atk = int(
                                        field["value"]
                                        .split("**Sp. Atk:** ")[1]
                                        .split("\n")[0]
                                    )
                                    sp_def = int(
                                        field["value"]
                                        .split("**Sp. Def:** ")[1]
                                        .split("\n")[0]
                                    )
                                    speed = int(field["value"].split("**Speed:** ")[1])
                                    total = (
                                        hp + attack + defense + sp_atk + sp_def + speed
                                    )
                                    stats.append(f"**HP:** {hp}")
                                    stats.append(f"**Attack:** {attack}")
                                    stats.append(f"**Defense:** {defense}")
                                    stats.append(f"--------------")
                                    stats.append(f"**Sp. Atk:** {sp_atk}")
                                    stats.append(f"**Sp. Def:** {sp_def}")
                                    stats.append(f"--------------")
                                    stats.append(f"**Speed:** {speed}")
                                    stats.append(f"**Total:** {total}")

                            new_embed = discord.Embed(
                                title=embed_data[number]["title"], color=0x2F3136
                            )
                            new_embed.set_thumbnail(
                                url=embed_data[number]["image"]["url"]
                            )
                            new_embed.add_field(
                                name="Type",
                                value=embed_data[number]["fields"][1]["value"],
                                inline=False,
                            )
                            new_embed.add_field(
                                name="Region",
                                value=embed_data[number]["fields"][2]["value"],
                                inline=False,
                            )
                            new_embed.add_field(
                                name="Stats", value="\n".join(stats), inline=False
                            )

                            await ctx.channel.send(embed=new_embed)

    # PK2 Assistant Support

    if ctx.author.id == 854233015475109888:
        if (
            ctx.channel.id == 1167681875540713562
            or ctx.channel.id == 1168924782876692525
        ):
            with open("PokeDex.json", "r") as file:
                embed_data = json.load(file)

            if ctx.embeds:
                for embed in ctx.embeds:
                    if "Random Roll" in embed.title:
                        description = embed.description

                        number = int(description.split("**")[-2])

                        if 1 <= number <= 1017:
                            stats = []
                            for field in embed_data[number]["fields"]:
                                if field["name"] == "Base Stats":
                                    hp = int(
                                        field["value"]
                                        .split("**HP:** ")[1]
                                        .split("\n")[0]
                                    )
                                    attack = int(
                                        field["value"]
                                        .split("**Attack:** ")[1]
                                        .split("\n")[0]
                                    )
                                    defense = int(
                                        field["value"]
                                        .split("**Defense:** ")[1]
                                        .split("\n")[0]
                                    )
                                    sp_atk = int(
                                        field["value"]
                                        .split("**Sp. Atk:** ")[1]
                                        .split("\n")[0]
                                    )
                                    sp_def = int(
                                        field["value"]
                                        .split("**Sp. Def:** ")[1]
                                        .split("\n")[0]
                                    )
                                    speed = int(field["value"].split("**Speed:** ")[1])
                                    total = (
                                        hp + attack + defense + sp_atk + sp_def + speed
                                    )
                                    stats.append(f"**HP:** {hp}")
                                    stats.append(f"**Attack:** {attack}")
                                    stats.append(f"**Defense:** {defense}")
                                    stats.append(f"--------------")
                                    stats.append(f"**Sp. Atk:** {sp_atk}")
                                    stats.append(f"**Sp. Def:** {sp_def}")
                                    stats.append(f"--------------")
                                    stats.append(f"**Speed:** {speed}")
                                    stats.append(f"**Total:** {total}")

                            new_embed = discord.Embed(
                                title=embed_data[number]["title"], color=0x2F3136
                            )
                            new_embed.set_thumbnail(
                                url=embed_data[number]["image"]["url"]
                            )
                            new_embed.add_field(
                                name="Type",
                                value=embed_data[number]["fields"][1]["value"],
                                inline=False,
                            )
                            new_embed.add_field(
                                name="Region",
                                value=embed_data[number]["fields"][2]["value"],
                                inline=False,
                            )
                            new_embed.add_field(
                                name="Stats", value="\n".join(stats), inline=False
                            )

                            await ctx.channel.send(embed=new_embed)

    # YAMPB Support

    if ctx.author.id == 204255221017214977:
        if (
            ctx.channel.id == 1167681875540713562
            or ctx.channel.id == 1168924782876692525
        ):
            with open("PokeDex.json", "r") as file:
                embed_data = json.load(file)

            if ":game_die:" in ctx.content:
                number = int(ctx.content.split(" ")[1])

                if 1 <= number <= 1017:
                    stats = []
                    for field in embed_data[number]["fields"]:
                        if field["name"] == "Base Stats":
                            hp = int(field["value"].split("**HP:** ")[1].split("\n")[0])
                            attack = int(
                                field["value"].split("**Attack:** ")[1].split("\n")[0]
                            )
                            defense = int(
                                field["value"].split("**Defense:** ")[1].split("\n")[0]
                            )
                            sp_atk = int(
                                field["value"].split("**Sp. Atk:** ")[1].split("\n")[0]
                            )
                            sp_def = int(
                                field["value"].split("**Sp. Def:** ")[1].split("\n")[0]
                            )
                            speed = int(
                                field["value"].split("**Speed:** ")[1].split("\n")[0]
                            )
                            total = hp + attack + defense + sp_atk + sp_def + speed
                            stats.append(f"**HP:** {hp}")
                            stats.append(f"**Attack:** {attack}")
                            stats.append(f"**Defense:** {defense}")
                            stats.append(f"--------------")
                            stats.append(f"**Sp. Atk:** {sp_atk}")
                            stats.append(f"**Sp. Def:** {sp_def}")
                            stats.append(f"--------------")
                            stats.append(f"**Speed:** {speed}")
                            stats.append(f"**Total:** {total}")

                    new_embed = discord.Embed(
                        title=embed_data[number]["title"], color=0x2F3136
                    )
                    new_embed.set_thumbnail(url=embed_data[number]["image"]["url"])
                    new_embed.add_field(
                        name="Type",
                        value=embed_data[number]["fields"][1]["value"],
                        inline=False,
                    )
                    new_embed.add_field(
                        name="Region",
                        value=embed_data[number]["fields"][2]["value"],
                        inline=False,
                    )
                    new_embed.add_field(
                        name="Stats", value="\n".join(stats), inline=False
                    )

                    await ctx.channel.send(embed=new_embed)

    trade_channels = [
        1139282085979377664,
        1168285910530531458,
        1234713072975876157,
        1139282123581305014,
        1139282152400355418,
        1180520761606283314,
        1167681875540713562,
        1168924782876692525,
        1194483081919336469,
    ]

    # Trade Update

    if (
        ctx.author.id == 716390085896962058
        and len(ctx.embeds) > 0
        and "Completed trade between" in ctx.embeds[0].title
        and ctx.channel.id in trade_channels
    ):
        post_channel = bot.get_channel(1178187732279898113)

        if post_channel is not None:
            message_link = (
                f"https://discord.com/channels/{ctx.guild.id}/{ctx.channel.id}/{ctx.id}"
            )
            trade_message = ctx.embeds[0].title.split("\n")[0]

            trade_parts = trade_message.split(" between ")

            if len(trade_parts) == 2:

                data3 = ctx.embeds[0].to_dict()

                if data3 is not None and "fields" in data3 and len(data3["fields"]) > 1:
                    participant1 = data3["fields"][0]["name"][2:]
                    participant2 = data3["fields"][1]["name"][2:]

                embed_copy = ctx.embeds[0].to_dict()
                embed_copy["fields"].append(
                    {"name": "Message Link", "value": message_link}
                )
                embed_copy = discord.Embed.from_dict(embed_copy)

                trade_data = {
                    "participant1": participant1,
                    "participant2": participant2,
                    "message_link": message_link,
                }

                try:
                    with open("Trades.json", "r") as file:
                        trades = json.load(file)
                except json.decoder.JSONDecodeError:
                    trades = {"trades": []}

                trades["trades"].append(trade_data)
                with open("Trades.json", "w") as file:
                    json.dump(trades, file, indent=4)

                participants_message = f"Gamblers : {participant1}, {participant2}"
                await post_channel.send(participants_message, embed=embed_copy)

                logging_embed = discord.Embed(title=f"Poketwo Trade Update")
                logging_embed.add_field(
                    name="",
                    value=f"**Trade Data**\n"
                    f"Participant 1: {participant1}\n"
                    f"Participant 2: {participant2}\n"
                    f"Message Link: {message_link}",
                )

                await post_channel.send(embed=logging_embed)

                # Gamble Data Update

                for member in ctx.guild.members:
                    if (
                        member.display_name == participant1
                        or member.nick == participant1
                    ):

                        participant1 = member.id
                        break

                for member in ctx.guild.members:
                    if (
                        member.display_name == participant2
                        or member.nick == participant2
                    ):

                        participant2 = member.id
                        break

                user_details_1 = get_user_details(participant1)

                if user_details_1 is None:
                    register_user(participant1)

                user_details_2 = get_user_details(participant2)

                if user_details_2 is None:
                    register_user(participant2)

                user1_lost_amt = 0
                user2_lost_amt = 0

                value1 = data3["fields"][0]["value"]
                value2 = data3["fields"][1]["value"]

                if re.search(r"(\d+(?:,\d+)*)\s+Pok", value1) or re.search(
                    r"(\d+(?:,\d+)*)\s+Pok", value2
                ):

                    try:

                        conn = sqlite3.connect("Profile.db")
                        c = conn.cursor()

                        if re.search(r"(\d+(?:,\d+)*)\s+Pok", value1):
                            user1_lost_amt = int(
                                re.search(r"(\d+(?:,\d+)*)\s+Pok", value1)
                                .group(1)
                                .replace(",", "")
                            )

                        if re.search(r"(\d+(?:,\d+)*)\s+Pok", value2):
                            user2_lost_amt = int(
                                re.search(r"(\d+(?:,\d+)*)\s+Pok", value2)
                                .group(1)
                                .replace(",", "")
                            )

                        # Update Net Total

                        if user2_lost_amt != 0:
                            c.execute(
                                "UPDATE users SET net_total = net_total + ? WHERE user_id = ?",
                                (user2_lost_amt, participant1),
                            )

                        if user1_lost_amt != 0:
                            c.execute(
                                "UPDATE users SET net_total = net_total + ? WHERE user_id = ?",
                                (user1_lost_amt, participant2),
                            )

                        if user1_lost_amt != 0:
                            c.execute(
                                "UPDATE users SET net_total = net_total - ? WHERE user_id = ?",
                                (user1_lost_amt, participant1),
                            )

                        if user2_lost_amt != 0:
                            c.execute(
                                "UPDATE users SET net_total = net_total - ? WHERE user_id = ?",
                                (user2_lost_amt, participant2),
                            )

                        # Update Wins And Loss Steaks

                        if participant1 is not None:
                            c.execute(
                                "SELECT gamble_wins_streak FROM users WHERE user_id = ?",
                                (participant1,),
                            )
                            user1_wins_streak = c.fetchone()[0]

                        else:
                            user1_wins_streak = 0

                        if participant1 is not None:
                            c.execute(
                                "SELECT gamble_losses_streak FROM users WHERE user_id = ?",
                                (participant1,),
                            )
                            user1_losses_streak = c.fetchone()[0]

                        else:
                            user1_losses_streak = 0

                        gamble_win_streak_user_1 = user1_wins_streak
                        gamble_loss_streak_user_1 = user1_losses_streak

                        if participant2 is not None:
                            c.execute(
                                "SELECT gamble_wins_streak FROM users WHERE user_id = ?",
                                (participant2,),
                            )
                            user2_wins_streak = c.fetchone()[0]

                        else:
                            user2_wins_streak = 0

                        if participant2 is not None:
                            c.execute(
                                "SELECT gamble_losses_streak FROM users WHERE user_id = ?",
                                (participant2,),
                            )
                            user2_losses_streak = c.fetchone()[0]

                        else:

                            user2_losses_streak = 0

                        gamble_win_streak_user_2 = user2_wins_streak
                        gamble_loss_streak_user_2 = user2_losses_streak

                        if user1_lost_amt > user2_lost_amt:
                            c.execute(
                                "UPDATE users SET gamble_losses = gamble_losses + ? WHERE user_id = ?",
                                (1, participant1),
                            )

                            gamble_win_streak_user_1 = 0
                            gamble_loss_streak_user_1 += 1

                            c.execute(
                                "UPDATE users SET gamble_wins = gamble_wins + ? WHERE user_id = ?",
                                (1, participant2),
                            )

                            gamble_loss_streak_user_2 = 0
                            gamble_win_streak_user_2 += 1

                        # Update Wins And Loss Amount

                        elif user1_lost_amt < user2_lost_amt:
                            c.execute(
                                "UPDATE users SET gamble_losses = gamble_losses + ? WHERE user_id = ?",
                                (1, participant2),
                            )

                            gamble_win_streak_user_2 = 0
                            gamble_loss_streak_user_2 += 1

                            c.execute(
                                "UPDATE users SET gamble_wins = gamble_wins + ? WHERE user_id = ?",
                                (1, participant1),
                            )

                            gamble_win_streak_user_1 += 1
                            gamble_loss_streak_user_1 = 0

                        try:
                            c.execute(
                                "UPDATE users SET gamble_wins_streak = ? WHERE user_id = ?",
                                (gamble_win_streak_user_1, participant1),
                            )

                        except Exception as e:
                            print(
                                f"{traceback.extract_tb(sys.exc_info()[2])[-1][1]} : {e}"
                            )

                        try:
                            c.execute(
                                "UPDATE users SET gamble_losses_streak = ? WHERE user_id = ?",
                                (gamble_loss_streak_user_1, participant1),
                            )

                        except Exception as e:
                            print(
                                f"{traceback.extract_tb(sys.exc_info()[2])[-1][1]} : {e}"
                            )

                        try:
                            c.execute(
                                "UPDATE users SET gamble_wins_streak = ? WHERE user_id = ?",
                                (gamble_win_streak_user_2, participant2),
                            )

                        except Exception as e:
                            print(
                                f"{traceback.extract_tb(sys.exc_info()[2])[-1][1]} : {e}"
                            )

                        try:
                            c.execute(
                                "UPDATE users SET gamble_losses_streak = ? WHERE user_id = ?",
                                (gamble_loss_streak_user_2, participant2),
                            )

                        except Exception as e:
                            print(
                                f"{traceback.extract_tb(sys.exc_info()[2])[-1][1]} : {e}"
                            )

                        c.execute(
                            "SELECT max_gambled FROM users WHERE user_id = ?",
                            (participant1,),
                        )

                        row = c.fetchone()

                        if row is not None:
                            participant1_max_amount = int(row[0])
                        else:
                            participant1_max_amount = 0

                        c.execute(
                            "SELECT max_gambled FROM users WHERE user_id = ?",
                            (participant2,),
                        )

                        row = c.fetchone()

                        if row is not None:
                            participant2_max_amount = int(row[0])
                        else:
                            participant2_max_amount = 0

                        if int(user1_lost_amt) > int(user2_lost_amt):
                            highest_amount = int(user1_lost_amt)
                        elif int(user2_lost_amt) > int(user1_lost_amt):
                            highest_amount = int(user2_lost_amt)
                        elif int(user1_lost_amt) == int(user2_lost_amt):
                            highest_amount = int(user1_lost_amt)
                        else:
                            highest_amount = None

                        if highest_amount is not None:
                            if highest_amount > participant1_max_amount:
                                c.execute(
                                    "UPDATE users SET max_gambled = ? WHERE user_id = ?",
                                    (highest_amount, participant1),
                                )

                            if highest_amount > participant2_max_amount:
                                c.execute(
                                    "UPDATE users SET max_gambled = ? WHERE user_id = ?",
                                    (highest_amount, participant2),
                                )

                        conn.commit()

                    except sqlite3.Error as e:
                        print(f"Database Error: {e}")

                    except Exception as e:
                        print(f"{traceback.extract_tb(sys.exc_info()[2])[-1][1]} : {e}")

                    finally:
                        if conn:
                            conn.close()

    await bot.process_commands(ctx)


@bot.command(aliases=["roll", "r"])
async def roll(ctx):
    with open("PokeDex.json", "r") as file:
        dex_data = json.load(file)

    number = random.randint(1, 1017)

    stats = []
    for field in dex_data[number]["fields"]:
        if field["name"] == "Base Stats":
            hp = int(field["value"].split("**HP:** ")[1].split("\n")[0])
            attack = int(field["value"].split("**Attack:** ")[1].split("\n")[0])
            defense = int(field["value"].split("**Defense:** ")[1].split("\n")[0])
            sp_atk = int(field["value"].split("**Sp. Atk:** ")[1].split("\n")[0])
            sp_def = int(field["value"].split("**Sp. Def:** ")[1].split("\n")[0])
            speed = int(field["value"].split("**Speed:** ")[1])
            total = hp + attack + defense + sp_atk + sp_def + speed
            stats.append(f"**HP:** {hp}")
            stats.append(f"**Attack:** {attack}")
            stats.append(f"**Defense:** {defense}")
            stats.append(f"--------------")
            stats.append(f"**Sp. Atk:** {sp_atk}")
            stats.append(f"**Sp. Def:** {sp_def}")
            stats.append(f"--------------")
            stats.append(f"**Speed:** {speed}")
            stats.append(f"**Total:** {total}")

    embed = discord.Embed(title=dex_data[number]["title"], color=0x2F3136)
    embed.set_thumbnail(url=dex_data[number]["image"]["url"])
    embed.add_field(
        name="Type", value=dex_data[number]["fields"][1]["value"], inline=False
    )
    embed.add_field(
        name="Region", value=dex_data[number]["fields"][2]["value"], inline=False
    )
    embed.add_field(name="Stats", value="\n".join(stats), inline=False)

    rollemebd = discord.Embed(
        title=f"Roll Value Is {number}",
        description=f"Rolled By : {ctx.author.mention}\nRolled Between 1 And 1017 \n",
        color=0x2F3136,
    )

    await ctx.send(embed=rollemebd)

    if ctx.channel.id == 1167681875540713562 or ctx.channel.id == 1168924782876692525:
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            title="PokeDex Unavailable",
            description="Autodex Works Only In : \nRand 1 : <#1167681875540713562> \nRand 2 : <#1168924782876692525>",
        )
        await ctx.send(embed=embed, delete_after=10)


@bot.command(aliases=["search", "poke"])
async def search(ctx, pokemon_query):
    with open("PokeDex.json", "r") as file:
        dex_data = json.load(file)

    pokemon_found = False
    for pokemon in dex_data:
        if pokemon_query.isdigit():
            if pokemon.get("title", "").split(" ")[0] == f"#{pokemon_query}":
                pokemon_found = True

                embed = discord.Embed(
                    title=pokemon["title"],
                    color=pokemon["color"],
                )

                for field in pokemon["fields"]:
                    embed.add_field(
                        name=field["name"], value=field["value"], inline=False
                    )

                embed.set_thumbnail(url=pokemon["image"]["url"])
                await ctx.send(embed=embed)
                break

        elif pokemon_query.lower() in pokemon.get("title", "").lower():
            pokemon_found = True

            embed = discord.Embed(
                title=pokemon["title"],
                color=pokemon["color"],
            )

            for field in pokemon["fields"]:
                embed.add_field(name=field["name"], value=field["value"], inline=False)

            embed.set_thumbnail(url=pokemon["image"]["url"])
            await ctx.send(embed=embed)
            break

    if not pokemon_found:
        await ctx.send(f"Pokemon '{pokemon_query}' Not Found")


@bot.command()
async def help(ctx):
    embed = discord.Embed(title="*Help Command*", color=0x2F3136)

    embed.add_field(
        name="**+register**",
        value="Registers The User In The Database",
        inline=False,
    )

    embed.add_field(
        name="**+profile** / **p**",
        value="Displays The Profile Of The User",
        inline=False,
    )

    embed.add_field(
        name="**+leaderboard** / **lb**",
        value="Displays The Leaderboard Of The Server",
        inline=False,
    )

    embed.add_field(
        name="**+ping**",
        value="Displays The Bot's Uptime And Latency",
        inline=False,
    )

    embed.add_field(
        name="**+roll** / **r**",
        value="Rolls A Random Pokemon",
        inline=False,
    )

    embed.add_field(
        name="**+search** / **poke** <Pokemon Name/Number>",
        value="Searches For A Pokemon By Name Or Number",
        inline=False,
    )

    await ctx.send(embed=embed)


bot.run("")
