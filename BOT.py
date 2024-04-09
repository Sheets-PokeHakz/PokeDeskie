import json
import random
import discord
import datetime
from discord.ext import commands

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='+', intents=intents)

bot.remove_command('help')

@bot.event
async def on_ready():
    print(f'======================= ')
    print(f'STATUS : ONLINE')
    print(f'======================= ')
    print(f'BOT : {bot.user}')

    # await bot.change_presence(status=discord.Status.idle,activity=discord.Game(name="Maintainance"))
    await bot.change_presence(activity=discord.Game(name="PokeDex | +help"))

    start_time = datetime.datetime.now()
    bot.start_time = start_time

@bot.command()
async def ping(ctx):

    latency = bot.latency * 1000
    uptime = datetime.datetime.now() - bot.start_time

    uptime_seconds = uptime.total_seconds()
    uptime_str = str(datetime.timedelta(seconds=uptime_seconds)).split(".")[0]

    num_servers = len(bot.guilds)

    embed = discord.Embed(
        title="_*Pong !*_",
        color=0x2f3136
    )

    embed.add_field(name="Uptime", value=uptime_str, inline=False)
    embed.add_field(name="Latency", value=f"{latency:.2f}ms", inline=False)
    embed.add_field(name="Servers", value=num_servers, inline=False)

    await ctx.send(embed=embed)


@bot.event
async def on_message(message):
    if message.author.id == 235148962103951360:
        if message.channel.id == 1223874528044908595 or message.channel.id == 1223811923477401733:
            with open('PokeDex.json', 'r') as file:
                embed_data = json.load(file)

            if message.embeds:
                for embed in message.embeds:
                    if 'rolls' in embed.title:
                        title_parts = embed.title.split(" ")
                        rolls_index = title_parts.index("rolls")
                        number = title_parts[rolls_index + 1].strip('**')
                        number = number.strip("()")
                        number = int(number)

                        if 1 <= number <= 1010:
                            stats = []
                            for field in embed_data[number]["fields"]:
                                if field["name"] == "Base Stats":
                                    hp = int(field["value"].split(
                                        "**HP:** ")[1].split("\n")[0])
                                    attack = int(field["value"].split(
                                        "**Attack:** ")[1].split("\n")[0])
                                    defense = int(field["value"].split(
                                        "**Defense:** ")[1].split("\n")[0])
                                    sp_atk = int(field["value"].split(
                                        "**Sp. Atk:** ")[1].split("\n")[0])
                                    sp_def = int(field["value"].split(
                                        "**Sp. Def:** ")[1].split("\n")[0])
                                    speed = int(
                                        field["value"].split("**Speed:** ")[1])
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

                            new_embed = discord.Embed(title=embed_data[number]["title"], color=0x2f3136)
                            new_embed.set_thumbnail(url=embed_data[number]["image"]["url"])
                            new_embed.add_field(name="Type", value=embed_data[number]["fields"][1]["value"], inline=False)
                            new_embed.add_field(name="Region", value=embed_data[number]["fields"][2]["value"], inline=False)
                            new_embed.add_field(name="Stats", value="\n".join(stats), inline=False)

                            await message.channel.send(embed=new_embed)

        else:

            embed = discord.Embed(
                title="PokeDex Unavailable",
                description='Sorry Autodex Works Only In <#1223874528044908595> And <#1223811923477401733>'
            )

            await message.channel.send(embed=embed, delete_after=10)

    if message.author.id == 716390085896962058 and len(message.embeds) > 0 and "Completed trade between" in message.embeds[0].title:
        post_channel = bot.get_channel(1109853131841470484)
        logging_channel = bot.get_channel(1109853131841470484)

        if post_channel is not None:
            message_link = f"https://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id}"
            trade_message = message.embeds[0].title.split('\n')[0]
            
            trade_parts = trade_message.split(' between ')
            if len(trade_parts) == 2:
                data3 = message.embeds[0].to_dict()
                participant1 = data3['fields'][0]['name'][2:]
                participant2 = data3['fields'][1]['name'][2:]
                embed_copy = message.embeds[0].to_dict()
                embed_copy['fields'].append(
                    {'name': 'Message Link', 'value': message_link})
                embed_copy = discord.Embed.from_dict(embed_copy)

                trade_data = {
                    "participant1": participant1,
                    "participant2": participant2,
                    "message_link": message_link
                }

                try:
                    with open('Trades.json', 'r') as file:
                        trades = json.load(file)
                except json.decoder.JSONDecodeError:
                    trades = {"trades": []}

                trades["trades"].append(trade_data)
                with open('Trades.json', 'w') as file:
                    json.dump(trades, file, indent=4)

                participants_message = f"Gamblers : {participant1}, {participant2}"
                await post_channel.send(participants_message, embed=embed_copy)

                logging_embed = discord.Embed(
                    title=f"Poketwo Trade Update")
                logging_embed.add_field(name='', value=f'**Trade Data**\n'
                                                       f'Participant 1: {participant1}\n'
                                                       f'Participant 2: {participant2}\n'
                                                       f'Message Link: {message_link}')

                await logging_channel.send(embed=logging_embed)

    await bot.process_commands(message)

@bot.command()
async def roll(ctx):
    with open('PokeDex.json', 'r') as file:
        dex_data = json.load(file)

    number = random.randint(1, 1010)

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

    embed = discord.Embed(title=dex_data[number]["title"], color=0x2f3136)
    embed.set_thumbnail(url=dex_data[number]["image"]["url"])
    embed.add_field(name="Type", value=dex_data[number]["fields"][1]["value"], inline=False)
    embed.add_field(name="Region", value=dex_data[number]["fields"][2]["value"], inline=False)
    embed.add_field(name="Stats", value="\n".join(stats), inline=False)

    rollemebd = discord.Embed(title=f"Roll Value Is {number}",description=f'Rolled By : {ctx.author.mention}\nRolled Between 1 And 1010 \n', color=0x2f3136)

    await ctx.send(embed=rollemebd)

    if ctx.channel.id == 1223874528044908595 or ctx.channel.id == 1223811923477401733:
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            title="PokeDex Unavailable",
            description='Autodex Works Only In : \nRand 1 : <#1223874528044908595> \nRand 2 : <#1223811923477401733>'
            )
        await ctx.send(embed=embed, delete_after=10)

@bot.command()
async def search(ctx, pokemon_query):
    with open('PokeDex.json', 'r') as file:
        dex_data = json.load(file)

    pokemon_found = False
    for pokemon in dex_data:
        if pokemon_query.isdigit():  
            if pokemon.get("title", "").split(" ")[0] == f"#{pokemon_query}":
                pokemon_found = True

                embed = discord.Embed(title=pokemon["title"], description=pokemon["description"], color=pokemon["color"])
                for field in pokemon["fields"]:
                    embed.add_field(name=field["name"], value=field["value"], inline=False)
                embed.set_thumbnail(url=pokemon["thumbnail"]["url"])
                embed.set_image(url=pokemon["image"]["url"])
                await ctx.send(embed=embed)
                break
            
        elif pokemon_query.lower() in pokemon.get("title", "").lower():  
            pokemon_found = True

            embed = discord.Embed(title=pokemon["title"], description=pokemon["description"], color=pokemon["color"])
            for field in pokemon["fields"]:
                embed.add_field(name=field["name"], value=field["value"], inline=False)
            embed.set_thumbnail(url=pokemon["thumbnail"]["url"])
            embed.set_image(url=pokemon["image"]["url"])
            await ctx.send(embed=embed)
            break

    if not pokemon_found:
        await ctx.send(f"Pokemon '{pokemon_query}' Not Found")

@bot.event
async def on_member_join(member):
    channel = bot.get_channel(1223811655029227582)
    embed = discord.Embed(
        title=f"Welcome To Forever",
        description="Hope You Have A Great Time Here",
        color=0x2f3136
    )
    embed.set_thumbnail(url=member.avatar.url)
    await channel.send(f'{member.mention}', embed=embed)


@bot.event
async def on_member_remove(member):
    channel = bot.get_channel(1223811655029227582)
    embed = discord.Embed(
        title=f"Goodbye",
        description="Hope You Had A Great Time Here",
        color=0xff0000 
    )
    embed.set_thumbnail(url=member.avatar.url)
    await channel.send(f'{member.mention}', embed=embed)

log_channel = bot.get_channel(1224006089880895499)

@bot.command()
async def ban(ctx, member: discord.Member, *, reason=None):
    if ctx.user.guild_permissions.ban_members:
        await member.ban(reason=reason)
        
        embed = discord.Embed(
            title=f"{member} Has Been Banned",
            description=f"Reason : {reason}",
            color=0x2f3136
        )

        await ctx.send(embed=embed)

        if ctx.guild.id == 1223811654588960860 :
            await log_channel.send(embed=embed)

    else:
        embed = discord.Embed(
            title="Unable To Ban",
            description="You Don't Have The Required Permissions",
            color=0xff0000
        )

        await ctx.send(embed=embed)

@bot.command()
async def kick(ctx, member: discord.Member, *, reason=None):
    if ctx.user.guild_permissions.kick_members:
        await member.kick(reason=reason)
        
        embed = discord.Embed(
            title=f"{member} Has Been Kicked",
            description=f"Reason : {reason}",
            color=0x2f3136
        )

        await ctx.send(embed=embed)

        if ctx.guild.id == 1223811654588960860 :
            await log_channel.send(embed=embed)

    else:
        embed = discord.Embed(
            title="Unable To Kick",
            description="You Don't Have The Required Permissions",
            color=0xff0000
        )

        await ctx.send(embed=embed)

@bot.command()
async def clear(ctx, amount=5):
    if ctx.author.guild_permissions.manage_messages:

        amount = amount + 1

        await ctx.channel.purge(limit=amount)
    else:
        embed = discord.Embed(
            title="Unable To Clear Messages",
            description="You Don't Have The Required Permissions",
            color=0xff0000
        )

        await ctx.send(embed=embed)


@bot.command()
async def unban(ctx, *, member):
    banned_users = await ctx.guild.bans()
    member_name, member_discriminator = member.split('#')

    for ban_entry in banned_users:
        user = ban_entry.user

        if (user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)
            embed = discord.Embed(
                title=f"{user} Has Been Unbanned",
                color=0x2f3136
            )

            await ctx.send(embed=embed)

            if ctx.guild.id == 1223811654588960860 :
                await log_channel.send(embed=embed)

            return
        
    embed = discord.Embed(
        title="Unable To Unban",
        description="User Not Found",
        color=0xff0000
    )

    await ctx.send(embed=embed)

@bot.command()
async def mute(ctx, member: discord.Member, *, reason=None):
    if ctx.user.guild_permissions.manage_roles:
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")

        if not muted_role:
            muted_role = await ctx.guild.create_role(name="Muted")

            for channel in ctx.guild.channels:
                await channel.set_permissions(muted_role, send_messages=False)

        await member.add_roles(muted_role, reason=reason)
        embed = discord.Embed(
            title=f"{member} Has Been Muted",
            description=f"Reason : {reason}",
            color=0x2f3136
        )

        await ctx.send(embed=embed)

        if ctx.guild.id == 1223811654588960860 :
            await log_channel.send(embed=embed)

    else:
        embed = discord.Embed(
            title="Unable To Mute",
            description="You Don't Have The Required Permissions",
            color=0xff0000
        )

        await ctx.send(embed=embed)

@bot.command()
async def unmute(ctx, member: discord.Member):
    if ctx.user.guild_permissions.manage_roles:
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")

        if muted_role in member.roles:
            await member.remove_roles(muted_role)
            embed = discord.Embed(
                title=f"{member} Has Been Unmuted",
                color=0x2f3136
            )

            await ctx.send(embed=embed)

            if ctx.guild.id == 1223811654588960860 :
                await log_channel.send(embed=embed)

        else:
            embed = discord.Embed(
                title="Unable To Unmute",
                description="User Is Not Muted",
                color=0xff0000
            )

            await ctx.send(embed=embed)

    else:
        embed = discord.Embed(
            title="Unable To Unmute",
            description="You Don't Have The Required Permissions",
            color=0xff0000
        )

        await ctx.send(embed=embed)


@bot.command()
async def lock(ctx, channel: discord.TextChannel):
    if ctx.user.guild_permissions.manage_channels:
        await channel.set_permissions(ctx.guild.default_role, send_messages=False)
        embed = discord.Embed(
            title=f"{channel} Has Been Locked",
            color=0x2f3136
        )

        await ctx.send(embed=embed)

        if ctx.guild.id == 1223811654588960860 :
            await log_channel.send(embed=embed)

    else:
        embed = discord.Embed(
            title="Unable To Lockdown",
            description="You Don't Have The Required Permissions",
            color=0xff0000
        )

        await ctx.send(embed=embed)

@bot.command()
async def unlock(ctx, channel: discord.TextChannel):
    if ctx.user.guild_permissions.manage_channels:
        await channel.set_permissions(ctx.guild.default_role, send_messages=True)
        embed = discord.Embed(
            title=f"{channel} Has Been Unlocked",
            color=0x2f3136
        )

        await ctx.send(embed=embed)

        if ctx.guild.id == 1223811654588960860 :
            await log_channel.send(embed=embed)

    else:
        embed = discord.Embed(
            title="Unable To Unlock",
            description="You Don't Have The Required Permissions",
            color=0xff0000
        )

        await ctx.send(embed=embed)

# Verification System
@bot.command()
async def verify(ctx):

    if ctx.channel.id == 1224293065091448862:

        embed = discord.Embed(
            title="Verification",
            description="**Please Click The Button Below To Verify** \nBy Clicking The Button You Agree To The Server Rules",
            color=0x2f3136
        )

        await ctx.send(embed=embed, view=verify())

class verify(discord.ui.View):
    @discord.ui.button(label='Verify', style=discord.ButtonStyle.green)
    async def verify(self, button: discord.ui.Button, interaction: discord.Interaction):


        role = interaction.guild.get_role(1223839868598222879)

        await interaction.response.send_message('You Have Been Verified', ephemeral=True)
        await interaction.user.add_roles(role)

        await interaction.channel.purge(limit=2)

        vembed = discord.Embed(
            title="Verification Log",
            description=f"{interaction.user.mention} Has Been Verified",
            color=0x2f3136
        )

        userpfp = interaction.user.avatar.url
        vembed.set_thumbnail(url=userpfp)

        await interaction.guild.get_channel(1224006089880895499).send(embed = vembed)

    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.red)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):

        await interaction.response.send_message('Verification Cancelled', ephemeral=True)

        await interaction.message.delete()

@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="_*Help Command*_",
        color=0x2f3136
    )

    embed.add_field(name="+ping", value="Shows Bot's Latency, Uptime And Server Info", inline=False)
    embed.add_field(name="+roll", value="Rolls A Random Pokemon From The Pokedex", inline=False)
    embed.add_field(name="+search <pokemon_name/pokemon_number>", value="Searches For A Pokemon In The Pokedex", inline=False)

    await ctx.send(embed=embed)

    if ctx.user.guild_permissions.ban_members:
        embed = discord.Embed(
            title="_*Moderation Commands*_",
            color=0x2f3136
        )

        embed.add_field(name="+ban <member> <reason>", value="Bans A Member", inline=False)
        embed.add_field(name="+kick <member> <reason>", value="Kicks A Member", inline=False)
        embed.add_field(name="+unban <member>", value="Unbans A Member", inline=False)
        embed.add_field(name="+mute <member> <reason>", value="Mutes A Member", inline=False)
        embed.add_field(name="+unmute <member>", value="Unmutes A Member", inline=False)
        embed.add_field(name="+lock <channel>", value="Locks A Channel", inline=False)
        embed.add_field(name="+unlock <channel>", value="Unlocks A Channel", inline=False)
        embed.add_field(name="+clear <amount>", value="Clears Messages", inline=False)

        await ctx.send(embed=embed)

bot.run('MTIwMzIxMDA4Njg4NTg4ODAxMA.GAW7ZW.q7DEfbHzTLnY3ow45ugJg9XhGsUjlN9UFlVCnM')
