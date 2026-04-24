# -- Imports --

# - Discord

import discord
from discord.ext import commands, tasks
from discord import app_commands # slash-command
from discord import ui #discord-ui

from typing import Literal, Union
import typing #autocomplete

# - Basic
import traceback
import os
import random
import asyncio
import json
import requests

# - FN client
import rebootpy
from rebootpy.ext import commands as fn_commands

import functools
from functools import partial

# - FN API
import FortniteAPIAsync
set = FortniteAPIAsync.APIClient()
BenBotAsync = set.cosmetics




# -- Config -- 


# - Discord
bot_token = ""
prefix = "-"

id_startbotlog_channel = 00000
id_error_channel = 00000
footer_text = "LBM"
bot_name = "LBM"

discord_link = "https://discord.gg/00000"

startbot_slash_id = "</startbot:00000>"

# - FN Client
online_fn_client = {}

bot_time = 120 # Bot time duration in minutes

cid = 'Character_Titanium'
bid = 'BID_753_TomatoKnight'
eid = 'EID_SandwichBop'
pickaxe_id = 'Pickaxe_LockJaw'
banner = "InfluencerBanner17"
level = 200
status = '🌐 Lobby Bot Maker 🌐'
joinMessage = 'Hello 👋'

login_url = "auth_code_link"


# -- Code --

# - DS Client


class PersistentViewBot(commands.Bot): 
    def __init__(self):
        intents = discord.Intents.all()

        super().__init__(command_prefix=prefix, intents=intents, case_insensitive=True)
    async def setup_hook(self) -> None:
        print(f"[DEBUG] rebootpy version {rebootpy.__version__}")
        slash_sync = await self.tree.sync() # - slash 
        print(f"[DISCORD] | Synced app command (tree) {len(slash_sync)}.") # - slash 


discord_bot = PersistentViewBot()

discord_bot.remove_command('help')

@tasks.loop(seconds=10)
async def ch_pr():
  statuses = [f"{len(discord_bot.guilds)} server",f"{len(online_fn_client)} bot online!"]
  status = random.choice(statuses)
  await discord_bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name=status))

@discord_bot.event
async def on_ready():
    if not ch_pr.is_running():
        ch_pr.start()
    print('[DISCORD] Discord Bot Online')

# - Client FN Basic

async def newbot(code_auth: str, user_id: int, interaction:discord.Interaction):
        try:
            #client definition    
            client_fn = fn_commands.Bot(
                command_prefix='!',
                auth=rebootpy.AuthorizationCodeAuth(code=code_auth),
                status=status
                )
            # user = discord user that created the bot
            user = discord_bot.get_user(user_id)


            @client_fn.event
            async def event_ready() -> None:
                # - Log
                print(f"[FORTNITE] {interaction.user.display_name} | Client ready as {client_fn.user.display_name}.")
                # ---
                channel = discord_bot.get_channel(id_startbotlog_channel)
                embed=discord.Embed(title=f"[FORTNITE] {interaction.user.display_name} | Client ready as {client_fn.user.display_name}.", color=discord.Color.green())
                await channel.send(embed=embed)
                # - Code
                member = client_fn.party.me
                try:
                    await member.edit_and_keep(
                        partial(member.set_outfit, asset=cid),
                        partial(member.set_backpack, asset=bid),
                        partial(member.set_banner, icon=banner, season_level=level),
                        partial(member.set_emote, asset=eid,run_for=15)
                        )
                    await client_fn.party.set_privacy(rebootpy.PartyPrivacy.PRIVATE)
                    
                    for request in client_fn.incoming_pending_friends:
                        await request.accept()
                    print(f"[FORTNITE] {client_fn.user.display_name} | Pending Friend Request Accepted")
                except Exception as e:
                    print(f"[FORTNITE] {client_fn.user.display_name} | Error in the start setup")
                    print(e)
            
            @client_fn.event
            async def event_party_member_join(member):
                #if client_fn.party.leader == client_fn.party.me:
                    #if len(client_fn.party.members) == 2:
                        #await member.promote()
                try:
                    print(f"[FORTNITE] {client_fn.user.display_name} | {member} joined the party")
                    await client_fn.party.me.clear_emote()
                    #await client_fn.party.send(joinMessage)
                except Exception as e:
                    if "Client is in a party alone." in str(e):
                        pass
                    else:
                        print(f"[FORTNITE] {client_fn.user.display_name} | event_party_member_join Error")
                        print(e)
                    
    
            @client_fn.event
            async def event_party_invite(invite):
                print(f"[FORTNITE] {client_fn.user.display_name} | Invite from {invite.sender.display_name}")
                try:
                    embed = discord.Embed(title=f"You have received an invitation request from `{invite.sender.display_name}`, press `✅` to accept it or `❌` to decline it", color=discord.Color.blue())
                    embed.set_footer(text="You have 30 seconds before the invitation request will be accepted.")
                    msg = await user.send(embed=embed, view=RequestButtonsView(invite))
                    await asyncio.sleep(30)
                    try:
                        await msg.delete()
                        await invite.accept()
                    except:
                        return
                except Exception as e:
                    await invite.accept()
                    print("[DISCORD] / [FORTNITE] | error in event_party_invite")
                    print(e)


            @client_fn.event
            async def event_party_join_request(invite):
                print(f"[FORTNITE] {client_fn.user.display_name} | Join request from {invite.friend.display_name}")
                try:
                    embed = discord.Embed(title=f"You have received an join request from `{invite.friend.display_name}`, press `✅` to accept it or `❌` to decline it", color=discord.Color.blue())
                    embed.set_footer(text="You have 30 seconds before the join request will be accepted.")
                    msg = await user.send(embed=embed, view=RequestButtonsView(invite))
                    await asyncio.sleep(30)
                    try:
                        await msg.delete()
                        await invite.accept()
                    except:
                        return
                except Exception as e:
                    await invite.accept()
                    print("[DISCORD] / [FORTNITE] | error in event_party_join_request")
                    print(e)

            @client_fn.event
            async def event_friend_request(invite):
                if invite.outgoing:
                    return
                print(f"[FORTNITE] {client_fn.user.display_name} | Friend request from {invite.display_name}")
                try:
                    embed = discord.Embed(title=f"You have received a friend request from `{invite.display_name}`, press `✅` to accept it or `❌` to decline it", color=discord.Color.blue())
                    embed.set_footer(text="You have 30 seconds before the friend request will be accepted.")
                    msg = await user.send(embed=embed, view=RequestButtonsView(invite))
                    await asyncio.sleep(30)
                    try:
                        await msg.delete()
                        await invite.accept()
                    except:
                        return
                except Exception as e:
                    await invite.accept()
                    print("[DISCORD] / [FORTNITE] | error in event_party_invite")
                    print(e)


            return client_fn
        except Exception as e:
            if "self.name = data['name']" in str(e):
                embed_error_name = discord.Embed(title="Invalid account, to use this account set a first and last name in the Epic Games account",color=discord.Color.red())
                await interaction.edit_original_response(embed=embed_error_name) 
            else:
                embed_error = discord.Embed(title="Unknown error",color=discord.Color.red())
                await interaction.edit_original_response(embed=embed_error)
                raise e


# ---- UI FN

# - Friend Request UI

class RequestButtonsView(discord.ui.View):
    def __init__(self, invite):
        self.invite = invite
        super().__init__(timeout=None)

    @discord.ui.button(label=None,emoji="✖️", style=discord.ButtonStyle.red)
    async def RequestDeclineButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title="I declined the request ❌",color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        invite = self.invite
        await invite.decline()
        await interaction.message.delete()
        
    @discord.ui.button(label=None,emoji="✔️", style=discord.ButtonStyle.green)
    async def RequestAcceptButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title="I accepted the request ✅",color=discord.Color.green())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        invite = self.invite
        await invite.accept()
        await interaction.message.delete()



# ---- StartBot command


class FN_AuthButtonView(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(label="Send the code",emoji="🤖", style=discord.ButtonStyle.blurple)
    async def AuthButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(FN_AuthModal())
        await interaction.delete_original_response()



class FN_AuthModal(discord.ui.Modal, title='Create a Lobby bot'):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(ui.TextInput(label='Auth Code',required=True,placeholder='Code=...', max_length=32))
    async def on_submit(self, interaction: discord.Interaction):
        code = str(self.children[0].value)
        embed_loading = discord.Embed(description="# **Loading** <a:loading:1302708369521643560>", color=discord.Color.blue())
        await interaction.response.send_message(embed=embed_loading,ephemeral=True) 
        if int(len(code)) == 32:
            fn_client = await newbot(code, user_id = interaction.user.id, interaction=interaction)
            
            async def start_bot():
                await fn_client.start()
            global task

            task = [discord_bot.loop.create_task(start_bot()), discord_bot.loop.create_task(fn_client.wait_until_ready())]		
            #task che fa / prova a far partire il bot
            done, pending = await asyncio.wait(task, return_when=asyncio.FIRST_COMPLETED)
            if str(task[1]) not in str(done):
                    embed_error_auth = discord.Embed(title="Invalid code, try sending the code faster!",color=discord.Color.red())
                    await interaction.edit_original_response(embed=embed_error_auth) 
            else:
                # - After Bot started
                online_fn_client[str(interaction.user.id)] = fn_client
                embed_account = discord.Embed(title=f"👤 `{fn_client.user.display_name}` 👤",color=discord.Color.blue())
                embed_account.set_thumbnail(url=f"https://fortnite-api.com/images/cosmetics/br/{cid}/smallicon.png")
                embed_account.add_field(name=f"<:logo_fortnite:1302708314525798490> Lobby Battle Royale - `{fn_client.party.member_count} / 16` <:logo_fortnite:1302708314525798490>", value="\u200b", inline=False)
                embed_account.add_field(name="📄 Commands List 🆘", value="</help:1305109828846354454>",inline=False)
                embed_account.add_field(name="<:discord:1302708403424198726> Discord server <:discord:1302708403424198726>", value=f"**[Click here]({discord_link})**",inline=False)
                embed_account.set_footer(text="The bot will shut down in 2 hours")
                await interaction.edit_original_response(embed=embed_account)
                await stopbot(fn_client, interaction.user.id, task)
        else:
            embed_error_auth = embed_account = discord.Embed(title="Invalid code, the code must be 32 digits!",color=discord.Color.red())
            await interaction.edit_original_response(embed=embed_error_auth) 

async def stopbot(client_fn, user_id, task):
    await asyncio.sleep(bot_time*60)
    await client_fn.close()
    del online_fn_client[str(user_id)]
    for task_fn in task:
        task_fn.cancel()
    try:
        user = await discord_bot.fetch_user(user_id)
        dm = await user.create_dm()
        embed = discord.Embed(title="Bot offline, session has been closed due to hosting time limit reached.\nUse </startbot:1302710342983483524> to start it again", color=discord.Color.red())
        await dm.send(embed=embed)
    except:
        pass

@discord_bot.tree.command(name="startbot", description = "Start a lobby bot")
@app_commands.allowed_installs(guilds=True, users=True)
async def startbot(interaction: discord.Integration):
    try:
        # - Bot already On check
        if str(interaction.user.id) in online_fn_client: 
            embed_already_on = discord.Embed(title="❌ You already have a Bot online ❌", color=discord.Color.red())
            await interaction.response.send_message(embed=embed_already_on,ephemeral=True)
        else:
            # - Auth Code get
            embed=discord.Embed(title=f"🤖 {bot_name} 🤖", color=discord.Color.blue())
            embed.add_field(name="**Create your own Bot**", value=f"-Log in on [epicgames.com](<{login_url}>) with the bot account (do not use your personal account)", inline=False)
            embed.add_field(name="Send your Authorization code by pressing the button", value="-Enter the code after: **`code=`**", inline=False)
            embed.set_image(url="https://cdn.discordapp.com/attachments/836517393266245632/837230076118302730/image0.png")
            await interaction.response.send_message(embed=embed, view=FN_AuthButtonView(), ephemeral=True)
    except Exception as e:
        channel = discord_bot.get_channel(id_error_channel)
        embed=discord.Embed(title="Si è verificato un errore nel completare un azione (comando: Start)", description=f"Si è verificato un errore, ma il tempo del bot è terminato!")
        await channel.send(embed=embed)
        raise e




@discord_bot.tree.command(name="stop", description = "Stop the lobby bot")
@app_commands.allowed_installs(guilds=True, users=True)
async def stop(interaction: discord.Integration):
    try:
        # - Bot already On check
        if not str(interaction.user.id) in online_fn_client: 
            embed_already_on = discord.Embed(title="❌ You don't have a Bot online ❌", color=discord.Color.red())
            await interaction.response.send_message(embed=embed_already_on,ephemeral=True)
        else:
            client_fn = online_fn_client[str(interaction.user.id)]
            embed_loading = discord.Embed(description="# **Loading** <a:loading:1302708369521643560>", color=discord.Color.blue())
            await interaction.response.send_message(embed=embed_loading,ephemeral=True)
            await client_fn.close()
            del online_fn_client[str(interaction.user.id)]
            global task
            for task_fn in task:
                task_fn.cancel()
            print(f"[FORTNITE] {interaction.user.display_name} | User {client_fn.user.display_name} killed the client.")
            embed = discord.Embed(title="The lobby bot has been successfully stopped", color=discord.Color.red())
            await interaction.edit_original_response(embed=embed)
    except Exception as e:
        channel = discord_bot.get_channel(id_error_channel)
        embed=discord.Embed(title="Si è verificato un errore nel completare un azione (comando: Stop)", description=f"Si è verificato un errore, ma il tempo del bot è terminato!")
        await channel.send(embed=embed)
        raise e


# -- Skin Command


async def skin_search_autocomplete(interaction: discord.Interaction, current:str) -> typing.List[app_commands.Choice[str]]:
    list_r = []
    count = 0

    r = requests.get("https://fortnite-api.com/v2/cosmetics/br")
    rj = r.json()
    keymatch = str(current)
    name: str = None
    value: str = None
    for value in rj["data"]:
        if "name" in value and "id" in value:
            if "CID_" in value["id"]:
                if keymatch.lower() in str(value["name"]).lower():
                    name = value["name"]
                    id = value["id"]
                    if count > 23:
                        break
                    if current.lower() in name.lower():
                        if name in str(list_r):
                            n_obj = 1
                            for object in list_r:
                                if name in str(object):
                                    n_obj = n_obj + 1
                            name = f"{name} {str(n_obj)}"
                        list_r.append(app_commands.Choice(name=name, value=id))
                        count += 1
    return list_r


@discord_bot.tree.command(name="skin", description = "Set a skin to the bot")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.autocomplete(value=skin_search_autocomplete)
@app_commands.describe(value="Id or Name of the skin")
async def skin(interaction: discord.Interaction, value: str):
    if str(interaction.user.id) in online_fn_client:
        fn_client = online_fn_client[str(interaction.user.id)]
        client = fn_client
        
        if value.upper().startswith("CID_"):
                await client.party.me.set_outfit(asset=value.upper())
                embed = discord.Embed(title=f"{client.user.display_name}", color=discord.Color.blue())
                embed.add_field(name=f"**Skin id (CID):** `{value}`", value="\u200b", inline=False)
                embed.set_thumbnail(url=f"https://fortnite-api.com/images/cosmetics/br/{value.lower()}/smallicon.png")
                await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            try:
                cosmetic = await BenBotAsync.get_cosmetic(
                    lang="en",
                    searchLang="en",
                    name=value,
                    matchMethod="contains",
                    backendType="AthenaCharacter"
                )
                await client.party.me.set_outfit(asset=cosmetic.id)
                embed = discord.Embed(title=f'{client.user.display_name}', color=discord.Color.blue())
                embed.add_field(name=f"**Skin Name:** `{cosmetic.name}`\n**Skin Id:** `{cosmetic.id}`", value="\u200b", inline=False)
                embed.set_thumbnail(url=f"https://fortnite-api.com/images/cosmetics/br/{cosmetic.id}/smallicon.png")
                await interaction.response.send_message(embed=embed, ephemeral=True)
            except: 
                embed = discord.Embed(title=f'Nothing found', color=discord.Color.red())
                await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        embed = discord.Embed(title=f"To use the following command create a bot using {startbot_slash_id}", color=discord.Color.red())
        await interaction.response.send_message(embed=embed,ephemeral=True)

# -- Emote Command

async def emote_search_autocomplete(interaction: discord.Interaction, current:str) -> typing.List[app_commands.Choice[str]]:
    list_r = []
    count = 0

    r = requests.get("https://fortnite-api.com/v2/cosmetics/br")
    rj = r.json()
    keymatch = str(current)
    name: str = None
    value: str = None
    for value in rj["data"]:
        if "name" in value and "id" in value:
            if "EID_" in value["id"]:
                if keymatch.lower() in str(value["name"]).lower():
                    name = value["name"]
                    id = value["id"]
                    if count > 23:
                        break
                    if current.lower() in name.lower():
                        if name in str(list_r):
                            n_obj = 1
                            for object in list_r:
                                if name in str(object):
                                    n_obj = n_obj + 1
                            name = f"{name} {str(n_obj)}"
                        list_r.append(app_commands.Choice(name=name, value=id))
                        count += 1
    return list_r

@discord_bot.tree.command(name="emote", description = "Set an emote to the bot")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.autocomplete(value=emote_search_autocomplete)
@app_commands.describe(value="Id or Name of the emote")
async def emote(interaction: discord.Interaction, value: str):
    if str(interaction.user.id) in online_fn_client:
        fn_client = online_fn_client[str(interaction.user.id)]
        client = fn_client
        if value.lower == "none":
            await fn_client.party.me.clear_emote()
            embed = discord.Embed(title="I removed the emote that was playing", color=discord.Color.blue())
            await interaction.response.send_message(embed=embed, ephemeral=True)
        if value.upper().startswith("EID_"):
                await client.party.me.set_emote(asset=value.upper())
                embed = discord.Embed(title=f"{client.user.display_name}", color=discord.Color.blue())
                embed.add_field(name=f"**Emote id (EID):** `{value}`", value="\u200b", inline=False)
                embed.set_thumbnail(url=f"https://fortnite-api.com/images/cosmetics/br/{value.lower()}/smallicon.png")
                await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            try:
                cosmetic = await BenBotAsync.get_cosmetic(
                    lang="en",
                    searchLang="en",
                    name=value,
                    matchMethod="contains",
                    backendType="AthenaDance"
                )
                await fn_client.party.me.clear_emote()
                await fn_client.party.me.set_emote(asset=cosmetic.id)
                embed = discord.Embed(title=f'{client.user.display_name}', color=discord.Color.blue())
                embed.add_field(name=f"**Emote Name:** `{cosmetic.name}`\n**Emote Id:** `{cosmetic.id}`", value="\u200b", inline=False)
                embed.set_thumbnail(url=f"https://fortnite-api.com/images/cosmetics/br/{cosmetic.id}/smallicon.png")
                await interaction.response.send_message(embed=embed, ephemeral=True)
            except: 
                embed = discord.Embed(title=f'Nothing found', color=discord.Color.red())
                await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        embed = discord.Embed(title=f"To use the following command create a bot using {startbot_slash_id}", color=discord.Color.red())
        await interaction.response.send_message(embed=embed,ephemeral=True)

# -- Skin Command

async def pickaxe_search_autocomplete(interaction: discord.Interaction, current:str) -> typing.List[app_commands.Choice[str]]:
    list_r = []
    count = 0

    r = requests.get("https://fortnite-api.com/v2/cosmetics/br")
    rj = r.json()
    keymatch = str(current)
    name: str = None
    value: str = None
    for value in rj["data"]:
        if "name" in value and "id" in value:
            if "Pickaxe_" in value["id"]:
                if keymatch.lower() in str(value["name"]).lower():
                    name = value["name"]
                    id = value["id"]
                    if count > 23:
                        break
                    if current.lower() in name.lower():
                        if name in str(list_r):
                            n_obj = 1
                            for object in list_r:
                                if name in str(object):
                                    n_obj = n_obj + 1
                            name = f"{name} {str(n_obj)}"
                        list_r.append(app_commands.Choice(name=name, value=id))
                        count += 1
    return list_r

@discord_bot.tree.command(name="pickaxe", description = "Set a pickaxe to the bot")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.autocomplete(value=pickaxe_search_autocomplete)
@app_commands.describe(value="Id or Name of the pickaxe")
async def pickaxe(interaction: discord.Interaction, value: str):
    if str(interaction.user.id) in online_fn_client:
        fn_client = online_fn_client[str(interaction.user.id)]
        client = fn_client
        if value.upper().startswith("Pickaxe_"): # Fix needed
                await fn_client.party.me.clear_emote()
                await fn_client.party.me.set_pickaxe(asset=value.upper())
                await client.party.me.set_emote(asset="EID_IceKing")
                embed = discord.Embed(title=f"{client.user.display_name}", color=discord.Color.blue())
                embed.add_field(name=f"**Pickaxe id:** `{value}`", value="\u200b", inline=False)
                embed.set_thumbnail(url=f"https://fortnite-api.com/images/cosmetics/br/{value.lower()}/smallicon.png")
                await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            try:
                cosmetic = await BenBotAsync.get_cosmetic(
                    lang="en",
                    searchLang="en",
                    name=value,
                    matchMethod="contains",
                    backendType="AthenaPickaxe"
                )
                await fn_client.party.me.clear_emote()
                await fn_client.party.me.set_pickaxe(asset=cosmetic.id)
                await client.party.me.set_emote(asset="EID_IceKing")
                embed = discord.Embed(title=f'{client.user.display_name}', color=discord.Color.blue())
                embed.add_field(name=f"**Pickaxe Name:** `{cosmetic.name}`\n**Pickaxe Id:** `{cosmetic.id}`", value="\u200b", inline=False)
                embed.set_thumbnail(url=f"https://fortnite-api.com/images/cosmetics/br/{cosmetic.id}/smallicon.png")
                await interaction.response.send_message(embed=embed, ephemeral=True)
            except: 
                embed = discord.Embed(title=f'Nothing found', color=discord.Color.red())
                await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        embed = discord.Embed(title=f"To use the following command create a bot using {startbot_slash_id}", color=discord.Color.red())
        await interaction.response.send_message(embed=embed,ephemeral=True)

# -- Variants command

@discord_bot.tree.command(name="variants", description = "Set the variant of an item")
@app_commands.allowed_installs(guilds=True, users=True)
async def variants(interaction: discord.Interaction, item_type: Literal["Skin", "Backpack", "Pickaxe"], pattern: int = None, numeric: int = None, clothing_color: int = None, jersey_color: str = None, parts: int = None, progressive: int = None, particle: int = None, material: int = None, emissive: int = None):
    if str(interaction.user.id) in online_fn_client:
        fn_client = online_fn_client[str(interaction.user.id)]
        client = fn_client
        variants = client.party.me.create_variant(
            pattern=pattern,
            numeric=numeric,
            clothing_color=clothing_color,
            jersey_color=jersey_color,
            parts=parts,
            progressive=progressive,
            particle=particle,
            material=material,
            emissive=emissive
            )
        if item_type == "Skin":
            asset_value = client.party.me.outfit
            await client.party.me.set_outfit(asset=asset_value,variants=variants)
        elif item_type == "Backpack":
            asset_value = client.party.me.backpack
            await client.party.me.set_backpack(asset=asset_value,variants=variants)
        elif item_type == "Pickaxe":
            asset_value = client.party.me.pickaxe
            await client.party.me.set_pickaxe(asset=asset_value,variants=variants)
            await client.party.me.set_emote(asset="EID_IceKing")
        embed = discord.Embed(title=f"Variant setted to your {item_type}", color=discord.Color.blue())
        embed.set_thumbnail(url=f"https://fortnite-api.com/images/cosmetics/br/{asset_value}/smallicon.png")
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        embed = discord.Embed(title=f"To use the following command create a bot using {startbot_slash_id}", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)

# -- Add / Remove Friend command

@discord_bot.tree.command(name="add", description = "Add a friend to the bot account")
@app_commands.allowed_installs(guilds=True, users=True)
async def add(interaction: discord.Interaction, user_name: str):
    if str(interaction.user.id) in online_fn_client:
        fn_client = online_fn_client[str(interaction.user.id)]
        try:
            user = await fn_client.fetch_user(user_name)
            if user.id in str(fn_client.friends):
                embed = discord.Embed(title=f'{fn_client.user.display_name}',description=f"{user.display_name} is already your friend ❌", color=discord.Color.red())
                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                await fn_client.add_friend(user.id)
                embed = discord.Embed(title=f"{fn_client.user.display_name}", description=f"I sent the friend request to `{user_name}` ➕", color=discord.Color.green())
                await interaction.response.send_message(embed=embed, ephemeral=True)
        except rebootpy.HTTPException:
            embed = discord.Embed(title=f'{fn_client.user.display_name}',description="Something went wrong when trying to add this friend. ⚙️", color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except AttributeError:
            embed = discord.Embed(title=f'{fn_client.user.display_name}',description="No users found with this name ❌", color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except rebootpy.FriendshipRequestAlreadySent:
            embed = discord.Embed(title=f'{fn_client.user.display_name}',description="A friendship request already exists for this user. ❌", color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            raise e

    else:
        embed = discord.Embed(title=f"To use the following command create a bot using {startbot_slash_id}", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)

@discord_bot.tree.command(name="remove", description = "Remove a friend to the bot account")
@app_commands.allowed_installs(guilds=True, users=True)
async def remove(interaction: discord.Interaction, user_name: str):
    if str(interaction.user.id) in online_fn_client:
        fn_client = online_fn_client[str(interaction.user.id)]
        try:
            user = await fn_client.fetch_user(user_name)
            if not user.id in str(fn_client.friends):
                embed = discord.Embed(title=f'{fn_client.user.display_name}',description=f"{user.display_name} is not your friend ❌", color=discord.Color.red())
                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                await fn_client.remove_or_decline_friend(user.id)
                embed = discord.Embed(title=f"{fn_client.user.display_name}", description=f"I removed the friend request from `{user_name}` ➖", color=discord.Color.green())
                await interaction.response.send_message(embed=embed, ephemeral=True)
        except rebootpy.HTTPException:
            embed = discord.Embed(title=f'{fn_client.user.display_name}',description="Something went wrong when trying to remove this friend. ⚙️", color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except AttributeError:
            embed = discord.Embed(title=f'{fn_client.user.display_name}',description="No users found with this name ❌", color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            raise e

    else:
        embed = discord.Embed(title=f"To use the following command create a bot using {startbot_slash_id}", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)

# - Level Command

@discord_bot.tree.command(name="level", description = "Set a level and the pass tier of the account")
@app_commands.allowed_installs(guilds=True, users=True)
async def level(interaction: discord.Interaction, number: int, pass_tier: Literal["Buyed", "Not buyed"]):
    if str(interaction.user.id) in online_fn_client:
        fn_client = online_fn_client[str(interaction.user.id)]
        if pass_tier == "Buyed":
            await fn_client.party.me.set_battlepass_info(has_purchased=True, level=number)
            embed = discord.Embed(title=f"💰 {fn_client.user.display_name} 🪙", description=f"I set the user level to `{number}` and set the battle pass level as `purchased`", color=discord.Color.gold())
            await interaction.response.send_message(embed=embed, ephemeral=True)
        elif pass_tier == "Not buyed":
            await fn_client.party.me.set_battlepass_info(has_purchased=False, level=number)
            embed = discord.Embed(title=f"🕸️ {fn_client.user.display_name} 📦", description=f"I set the user level to `{number}` and set the battle pass level as `not purchased`", color=discord.Color.light_gray())
            await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        embed = discord.Embed(title=f"To use the following command create a bot using {startbot_slash_id}", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)

# - Lobby Status Command

@discord_bot.tree.command(name="lobby_status", description = "Set the state of the bot in lobby (ready, not ready...)")
@app_commands.allowed_installs(guilds=True, users=True)
async def lobbystatus(interaction: discord.Interaction, value: Literal["Ready", "Not ready", "Sitting out", "Sleeping"]):
    if str(interaction.user.id) in online_fn_client:
        fn_client = online_fn_client[str(interaction.user.id)]
        if value == "Ready":
            await fn_client.party.me.set_ready(rebootpy.ReadyState.READY)
        elif value == "Not ready":
            await fn_client.party.me.set_ready(rebootpy.ReadyState.NOT_READY)
        elif value == "Sitting out":
            await fn_client.party.me.set_ready(rebootpy.ReadyState.SITTING_OUT)
        elif value == "Sleeping":
            await fn_client.party.me.set_ready(rebootpy.ReadyState.SLEEPING)
        embed = discord.Embed(title=f"{fn_client.user.display_name}", description=f"I set the lobby status to `{value}`", color=discord.Color.blue())
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        embed = discord.Embed(title=f"To use the following command create a bot using {startbot_slash_id}", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)

# - Randomize Commannd

@discord_bot.tree.command(name="randomize", description = "Set a random skin, backpack, picxaxe or set")
@app_commands.allowed_installs(guilds=True, users=True)
async def randomize(interaction: discord.Interaction, type: Literal["skin", "backpack", "picxaxe", "set"]):
    if str(interaction.user.id) in online_fn_client:
        fn_client = online_fn_client[str(interaction.user.id)]
        thumbnail_value = False
        embed = discord.Embed(title=f"{fn_client.user.display_name}", color=discord.Color.blue())
        if type == "skin" or type == "set":
            skins = await BenBotAsync.get_cosmetics(
                lang="en",
                backendType="AthenaCharacter"
                )
            skin = random.choice(skins)
            await fn_client.party.me.set_outfit(asset=skin.id)
            embed.add_field(name=f'**Random skin**', value=f'**Name:** {skin.name}\n**Id:** {skin.id}', inline=False)
            if thumbnail_value == False:
                embed.set_thumbnail(url=f"https://fortnite-api.com/images/cosmetics/br/{skin.id}/smallicon.png")
                thumbnail_value = True
        if type == "backpack" or type == "set":
            backpacks = await BenBotAsync.get_cosmetics(
                lang="en",
                backendType="AthenaBackpack"
                )
            backpack = random.choice(backpacks)
            await fn_client.party.me.set_backpack(asset=backpack.id)
            embed.add_field(name=f'**Random backpack**', value=f'**Name:** {backpack.name}\n**Id:** {backpack.id}', inline=False)
            if thumbnail_value == False:
                embed.set_thumbnail(url=f"https://fortnite-api.com/images/cosmetics/br/{backpack.id}/smallicon.png")
                thumbnail_value = True
        if type == "picxaxe" or type == "set":
            pickaxes = await BenBotAsync.get_cosmetics(
                lang="en",
                backendType="AthenaPickaxe"
            )
            pickaxe = random.choice(pickaxes)
            await fn_client.party.me.set_pickaxe(asset=pickaxe.id)
            embed.add_field(name=f'**Random pickaxe**', value=f'**Name:** {pickaxe.name}\n**Id:** {pickaxe.id}', inline=False)
            await fn_client.party.me.set_emote(asset="EID_IceKing")
            if thumbnail_value == False:
                embed.set_thumbnail(url=f"https://fortnite-api.com/images/cosmetics/br/{pickaxe.id}/smallicon.png")
                thumbnail_value = True
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        embed = discord.Embed(title=f"To use the following command create a bot using {startbot_slash_id}", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)

# - Promote Command

@discord_bot.tree.command(name="promote", description = "Promote a member of the party if the bot is the leader")
@app_commands.allowed_installs(guilds=True, users=True)
async def promote(interaction: discord.Interaction, member_name: str):
    if str(interaction.user.id) in online_fn_client:
        fn_client = online_fn_client[str(interaction.user.id)]
        try:
            user = await fn_client.fetch_user(member_name)
            member = fn_client.party.get_member(user.id)
            await member.promote()
            embed = discord.Embed(title=f"I promoted {member_name}! 👑", color=discord.Color.gold())
            embed.set_thumbnail(url=f"https://benbotfn.tk/cdn/images/{fn_client.party.me.outfit}/icon.png")
        except rebootpy.errors.Forbidden:
            embed = discord.Embed(title=f'Cannot promote **{member.display_name}**, as i am not party leader ❌', color=discord.Color.red())
        except AttributeError:
            embed = discord.Embed(title="No users found with this name ❌", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        embed = discord.Embed(title=f"To use the following command create a bot using {startbot_slash_id}", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)

# - Info Command

@discord_bot.tree.command(name="info", description = "Get the info about the bot")
@app_commands.allowed_installs(guilds=True, users=True)
async def info(interaction: discord.Interaction):
    if str(interaction.user.id) in online_fn_client:
        fn_client = online_fn_client[str(interaction.user.id)]
        currentskin = fn_client.party.me.outfit
        currentpickaxe = fn_client.party.me.pickaxe
        currentbackpack = fn_client.party.me.backpack
        currentemote = fn_client.party.me.emote

        embed = discord.Embed(title = f"{fn_client.user.display_name}",description = f"Lobby Battle Royale - {fn_client.party.member_count} / 16" ,color=discord.Color.blue())
        embed.set_thumbnail(url=f'https://fortnite-api.com/images/cosmetics/br/{currentskin}/icon.png?width=150&height=150')
        embed.add_field(name = "Skin", value = f"{currentskin} 👤", inline=False)
        embed.add_field(name = "Backpack", value = f"{currentbackpack} 🎒", inline=False)
        embed.add_field(name = "Pickaxe", value = f"{currentpickaxe} ⛏️", inline=True)
        embed.add_field(name = "Last Emote", value = f"{currentemote} 🕺", inline=True)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        embed = discord.Embed(title=f"To use the following command create a bot using {startbot_slash_id}", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)

# - Hide
@discord_bot.tree.command(name="hide", description = "Hide or show a user from the lobby")
@app_commands.allowed_installs(guilds=True, users=True)
async def hide(interaction: discord.Interaction, name: str, value: Literal["True", "False"]):
    #https://rebootpy.readthedocs.io/en/latest/api.html?highlight=party#rebootpy.ClientParty.set_squad_assignments
    try:
        fn_client = online_fn_client[str(interaction.user.id)]
        user = await fn_client.fetch_user(name)
        party_user = fn_client.party.get_member(user.id)
        assignments_value = {}
        if value == "True":
            assignments_value[party_user] = rebootpy.SquadAssignment(hidden=True)
            await fn_client.party.set_squad_assignments(assignments=assignments_value)
            # - DS
            embed = discord.Embed(title=f"I hid the user `{name}`", color=discord.Color.green())
            await interaction.response.send_message(embed=embed, ephemeral=True)
        elif value == "False":
            assignments_value[party_user] = rebootpy.SquadAssignment(hidden=False)
            await fn_client.party.set_squad_assignments(assignments=assignments_value)
            # - DS
            embed = discord.Embed(title=f"I showed the user `{name}`", color=discord.Color.blue())
            await interaction.response.send_message(embed=embed, ephemeral=True)
    except Exception as e:
        if "account_not_found" in str(e):
            embed = discord.Embed(title=f"**No users found with the name `{name}`**",color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(title=f"**Unknown error**",color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
            channel = discord_bot.get_channel(id_error_channel)
            embed = discord.Embed(title=f"**Errore**", description=f"`Errore Hide`\n\n**Errore:** `{str(e)}`\nError: {e}",color=discord.Color.red())
            await channel.send(embed=embed)


# - Help Command

@discord_bot.tree.command(name="help", description = "Get the list of all of the commands of the bot")
@app_commands.allowed_installs(guilds=True, users=True)
async def help(interaction: discord.Interaction):
    slash_list = ""
    for slash_command in discord_bot.tree.walk_commands(type=discord.AppCommandType.chat_input):
        slash_list = f"`/{slash_command.name}` - *{slash_command.description}*\n" + slash_list
    embed = discord.Embed(title="📒 Slash Commands 📄", description=slash_list, color=discord.Color.blue())
    await interaction.response.send_message(embed=embed, ephemeral=True)




#--------------------
"""
# Useless
@discord_bot.event
async def on_message(message):
    if message.author.bot:
        return
    if message.content.startswith(prefix):
        embed = discord.Embed(title="Commands with prefix are not supported anymore, please use </help:1305109828846354454> to see the list of commands!", description=slash_list, color=discord.Color.red())
        await message.reply(embed=embed, delete_after=5)
    await discord_bot.process_commands(message) 
"""

@discord_bot.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.CommandNotFound):
        #embed = discord.Embed(title=f"**Error: Command does not exist**",color=discord.Color.red())
        #await ctx.send(embed=embed, delete_after=10)
        embed = discord.Embed(title="Commands with prefix are not supported anymore, please use </help:1305109828846354454> to see the list of commands!", color=discord.Color.red())
        await ctx.send(embed=embed, delete_after=10)
    elif isinstance(error, discord.ext.commands.errors.CommandInvokeError):
        embed = discord.Embed(title=f"**Error: Command written incorrectly**",color=discord.Color.red())
        await ctx.send(embed=embed, delete_after=10)

        channel = discord_bot.get_channel(id_error_channel)
        embed = discord.Embed(title=f"**Errore - Command Invoke Error**", description=f"**Tipo di errore:** `{str(isinstance)}` - `Command Error`\n\n**Errore completo:** `{error}`",color=discord.Color.red())
        await channel.send(embed=embed)
        print(error)
    else:
        embed = discord.Embed(title=f"**Unknown error**",color=discord.Color.red())
        await ctx.send(embed=embed, delete_after=10)

        channel = discord_bot.get_channel(id_error_channel)
        embed = discord.Embed(title=f"**Errore - Sconosciuto Generico**", description=f"**Tipo di errore:** `{str(isinstance)}` - `Command Error`\n\n**Errore completo:** `{error}`",color=discord.Color.red())
        await channel.send(embed=embed)
        print(error)


@discord_bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
    try:
        embed = discord.Embed(title=f"**Unknown error**",color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
    except:
        pass
    channel = discord_bot.get_channel(id_error_channel)
    embed = discord.Embed(title=f"**Errore - Slash**", description=f"**Tipo di errore:** `{str(isinstance)}` - `App Command Error`\n\n**Comando:** `{interaction.command.name}`\n**Errore completo:** `{error}`",color=discord.Color.red())
    await channel.send(embed=embed)


        
discord_bot.run(bot_token)
