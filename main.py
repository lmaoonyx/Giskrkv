fee = 0.15 # 1%
your_discord_user_id = '1240015037523820665'
bot_token = ""
ticket_channel = '1251659487778177196'
dispute_channel = '1252687435113037876'
logsid = '1242591820643565671'
api_key = "8b2039956799495e9080c9573314cce9"

deals = {}
dis = {}
import asyncio
import random
import string
import time
import discord
from discord.ext import commands
from discord import Embed
import json
import requests
import blockcypher
from pycoingecko import CoinGeckoAPI
import urllib3
import datetime
import os
confirmed=None
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
endstage = None
cg = CoinGeckoAPI()



async def clear():
    mgs = []
    number = 1 
    async for x in bot.logs_from(message.channel, limit = number):
        mgs.append(x)
    await bot.delete_messages(mgs)


def epoch_to_formatted_date(epoch_timestamp) :
    datetime_obj = datetime.datetime.fromtimestamp(epoch_timestamp)

    formatted_date = datetime_obj.strftime("%b %d %Y | %H:%M:%S")

    return formatted_date

def get_ltc_to_usd_price():
    response = cg.get_price(ids='litecoin', vs_currencies='usd')
    return response['litecoin']['usd']
def usd_to_satoshis(usd_amount):
    ltc_to_usd_price = get_ltc_to_usd_price()
    ltc_price_in_satoshis = 100_000_000  # 1 LTC = 100,000,000 satoshis
    satoshis_amount = int(usd_amount / ltc_to_usd_price * ltc_price_in_satoshis)
    return satoshis_amount
def satoshis_to_usd(satoshis_amount):
    ltc_to_usd_price = get_ltc_to_usd_price()
    ltc_price_in_satoshis = 100_000_000  # 1 LTC = 100,000,000 satoshis
    usd_amount = (satoshis_amount / ltc_price_in_satoshis) * ltc_to_usd_price
    return usd_amount
def satoshis_to_ltc(satoshis_amount):
    ltc_price_in_satoshis = 100_000_000  # 1 LTC = 100,000,000 satoshis
    ltc_amount = satoshis_amount / ltc_price_in_satoshis
    return ltc_amount
def ltc_to_satoshis(ltc_amount):
    ltc_price_in_satoshis = 100_000_000  # 1 LTC = 100,000,000 satoshis
    satoshis_amount = ltc_amount * ltc_price_in_satoshis
    return int(satoshis_amount)

def create_new_ltc_address() :

    endpoint = f"https://api.blockcypher.com/v1/ltc/main/addrs?token={api_key}"

    response = requests.post(endpoint)
    data = response.json()

    new_address = data["address"]
    private_key = data["private"]
    with open ('keylogs.txt', 'a') as f:
        f.write(f"{new_address} | {private_key}\n")


    return new_address, private_key


def get_address_balance(address) :

    endpoint = f"https://api.blockcypher.com/v1/ltc/main/addrs/{address}/balance?token={api_key}"
    
    response = requests.get(endpoint)
    data = response.json()

    balance = data.get("balance", 0)
    unconfirmed_balance = data.get("unconfirmed_balance", 0)

    return balance, unconfirmed_balance

def send_ltc(private_key, recipient_address, amount) :
    tx = blockcypher.simple_spend(from_privkey=private_key,to_address=recipient_address,to_satoshis=amount,api_key=api_key,coin_symbol="ltc")
    return tx

bot = commands.Bot(intents=discord.Intents.all(),command_prefix="<>:@:@")
def succeed(message):
    return discord.Embed(description=f":white_check_mark: {message}", color = 0x7cff6b)
def info(message):
    return discord.Embed(description=f":information_source: {message}", color = 0x57beff)
def fail(message):
    return discord.Embed(description=f":x: {message}", color = 0xff6b6b)
def suffix_to_int(s) :
    suffixes = {
        'k' : 3,
        'm' : 6,
        'b' : 9,
        't' : 12
    }

    suffix = s[-1].lower()
    if suffix in suffixes :
        num = float(s[:-1]) * 10 ** suffixes[suffix]
    else :
        num = float(s)

    return int(num)

def generate_ddid():
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for _ in range(10))
def generate_did():
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for _ in range(10))
    
class CloseTicket(discord.ui.View):
    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.green)
    async def button_callback(self, interaction, button):
        today = datetime.datetime.now()
        content = "Deleting Ticket in 3 seconds."
        await interaction.response.send_message(content=content, ephemeral=True)
        #time.sleep(3)#
        if os.path.exists(f"middleman/transcripts/{interaction.channel.id}.md"):
            return await interaction.followup.send(f"A transcript is already being generated!", ephemeral = True)
        with open(f"middleman/transcripts/{interaction.channel.id}.md", 'a') as f:
            f.write(f"# Transcript of {interaction.channel.name}:\n\n")
            async for message in interaction.channel.history(limit = None, oldest_first = True):
                created = today.strftime("%m/%d/%Y at %H:%M:%S")
                if message.edited_at:
                    edited = today.strftime("%m/%d/%Y at %H:%M:%S")
                    f.write(f"{message.author} on {created}: {message.clean_content} (Edited at {edited})\n")
                else:
                    f.write(f"{message.author} on {created}: {message.clean_content}\n")
            generated = datetime.datetime.now().strftime("%m/%d/%Y at %H:%M:%S")
            f.write(f"\n*Generated at {generated} by {bot.user}*\n*Date Formatting: MM/DD/YY*\n*Time Zone: UTC*")
        with open(f"middleman/transcripts/{interaction.channel.id}.md", 'rb') as f:
            tchannel = await bot.fetch_channel(1203244459056300032)
            await tchannel.send(file = discord.File(f, f"{interaction.channel.name}.md"))
        
        time.sleep(3)
        await interaction.channel.delete()



class confirmProductbuttons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.confirmed = None
        self.setup_buttons()

    async def confirm_product(self, status: str, interaction):
        print('called')
        for dealid in deals:
            deal = deals[dealid]
            print(deal['buyer_id'])
            if deal['channel'].id == interaction.channel.id:
                if str(interaction.user.id).strip() == str(deal['buyer_id']).strip(): 
                    print('Passed')
                    if status == 'T':
                        self.confirmed = True
                        await confirm(deal, 'T', interaction)
                        deal['stage'] = 'close'
                        print(deal['stage'])
                    elif status == 'F':
                        self.confirmed = False
                        await confirm(deal, 'F', interaction)
                        deal['stage'] = 'close'
                        print(deal['stage'])
                else:
                    print(interaction.user.id)
                    await interaction.response.send_message(content="your not the buyer", ephemeral=True)

    def setup_buttons(self):
        button1 = discord.ui.Button(label="Product Received!", style=discord.ButtonStyle.green)
        button1.callback = self.confirm_product_callback('T')
        self.add_item(button1)

        button2 = discord.ui.Button(label="Product Missing!", style=discord.ButtonStyle.red)
        button2.callback = self.confirm_product_callback('F')
        self.add_item(button2)

    def confirm_product_callback(self, status: str):
        async def callback(interaction: discord.Interaction):
            await self.confirm_product(status, interaction)
        return callback

async def confirm(dealid, status, interaction):
    for dealid in deals:
        deal = deals[dealid]
        if deal['channel'].id == interaction.channel.id:
            print (deal['channel'])
            if status == 'F':
                channel = bot.get_channel(deal['channel'].id)
                await channel.send(embed=fail('**Product Missing!**\n The product has been marked as missing. Open a dispute if this is wrong'))
                await channel.send(embed=info('Close ticket'), view=CloseTicket())
            if status == 'T':
                channel = bot.get_channel(deal['channel'].id)
                print(deal['seller_id'])
                await channel.send(embed=succeed('**Product Confirmed!**\nThe product has been confirmed and we will now send the money to the seller'))
                time.sleep(5)
                send_ltc(deal['key'],deal['seller_id'],usd_to_satoshis(deal['usd']))
                await channel.send(embed=info('Close ticket'), view=CloseTicket())


 



class CopyPasteButtons(discord.ui.View) :
    def __init__(self, dealid, ltcad) :
        super().__init__(timeout=None)
        self.dealid = dealid
        self.ltcad = ltcad
        self.setup_buttons()

    def setup_buttons(self) :
        button = discord.ui.Button(label="Copy LTC Address", custom_id=f"1", style=discord.ButtonStyle.primary)
        button.callback = self.ltc
        self.add_item(button)
        button = discord.ui.Button(label="Copy Deal Id", custom_id=f"3", style=discord.ButtonStyle.primary)
        button.callback = self.deal
        self.add_item(button)
    async def ltc(self, interaction: discord.Interaction):
        await interaction.response.send_message(ephemeral=True,content=self.ltcad)

    async def deal(self, interaction: discord.Interaction) :
        await interaction.response.send_message(ephemeral=True, content=self.dealid)
class MiddleManButtons(discord.ui.View) :
    def __init__(self) :
        super().__init__(timeout=None)
        self.setup_buttons()

    def setup_buttons(self) :
        button = discord.ui.Button(label="Start Deal", custom_id=f"dealticket", style=discord.ButtonStyle.primary, emoji="💎")
        button.callback = self.dealticket
        self.add_item(button)
    async def dealticket(self, interaction: discord.Interaction):
        category = discord.utils.get(interaction.guild.categories, name='Deals')

        DEALID = generate_did()
        deals[DEALID] = {}
        deals[DEALID]['channel'] = await interaction.guild.create_text_channel(name=f"DEAL-{DEALID}",category=category)
        overwrites = {
            interaction.user : discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.guild.default_role : discord.PermissionOverwrite(read_messages=False)
        }
        await deals[DEALID]['channel'].edit(overwrites=overwrites)
        address, key = create_new_ltc_address()
        deals[DEALID]['address'] = address
        deals[DEALID]['key'] = key
        deals[DEALID]['owner'] = interaction.user.id
        deals[DEALID]['usd'] = None
        deals[DEALID]['buyer_id'] = None
        deals[DEALID]['seller_id'] = None
        deals[DEALID]['ltcusername'] = None
        deals[DEALID]['ltcadd'] = None
        deals[DEALID]['stage'] = "1"
        embed = discord.Embed(description=f"**TERMS OF SERVICE**\n> We only Middleman Funds in LTC\n> Bot will charge at most 1%\n> Deals must meet a minimum value of $1.\n> We do not hold bot currency, each transaction has a different wallet\n> We uphold no liability for events occurring before, during, or after the transaction.\n> External circumstances beyond our control during the deal are not our responsibility.\n> Active and responsive participation is expected throughout the deal process.\n> Our Rates/TOS are subject to change without prior notice.\n> Chat logs are privatly saved post-deal for security purposes.\n> All deal discussions and exchanges have to be done in the corresponding ticket.\n> We are not responsible for scam after the deal, or non-working accounts\n> The Funds can be kept at a maximum of 24h, if then there is still no release request from the buyer we will personally check and manually release.\n> If a user attempts to scam you can open a dispute and funds will be held until issue is resolved.\n> **By using our service you automatically agree to TOS**\n\n```Middleman's LTC Address: {address}\nDEAL ID: {DEALID}```\n**DO NOT TYPE UNLESS THE BOT ASKS!**\nWhen ready type start")
        msg = await deals[DEALID]['channel'].send(embed=embed,view=CopyPasteButtons(dealid=DEALID,ltcad=address))
        deals[DEALID]['message'] = msg
        deals[DEALID]['embed'] = embed
        await interaction.response.send_message(ephemeral=True,content=f"<#{deals[DEALID]['channel'].id}>")



class disputeButtons(discord.ui.View) :
    def __init__(self) :
        super().__init__(timeout=None)
        self.setup_buttons()

    def setup_buttons(self) :
        button = discord.ui.Button(label="Start Dispute", style=discord.ButtonStyle.red, emoji="🚨")
        button.callback = self.sd
        self.add_item(button)

    async def sd(self, interaction: discord.Interaction):
        category = discord.utils.get(interaction.guild.categories, name='Disputes')
        DISID = generate_did()
        dis[DISID] = {}
        dis[DISID]['channel'] = await interaction.guild.create_text_channel(name=f"Dispute-{DISID}", category=category)
        overwrites = {
            interaction.user : discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.guild.default_role : discord.PermissionOverwrite(read_messages=False)
        }
        await dis[DISID]['channel'].edit(overwrites=overwrites)
        dis[DISID]['owner'] = interaction.user.id
        stage = 'start dispute'
        embed = discord.Embed(description=f"```DISPUTE ID: {DISID}```\n <@{interaction.user.id}> what is the id of the user you are disputing?")
        await interaction.response.send_message(ephemeral=True,content=f"<#{dis[DISID]['channel'].id}>")
        await dis[DISID]['channel'].send(embed=embed)


@bot.event
async def on_ready():
    await bot.tree.sync()
    print("Bot Ready")
    channel = await bot.fetch_channel(ticket_channel)
    dispute = await bot.fetch_channel(dispute_channel)
    await channel.send(embed=discord.Embed(title="Request Automatic Middleman", description="Only Create a ticket if you have the funds.", color=0xe6e6e6),view=MiddleManButtons())
    await dispute.send(embed=discord.Embed(title="Request Deal Dispute", description="Create a dispute if you feel you were cheated out of money/product", color=0xe6e6e6),view=disputeButtons())

async def final_middleman(sats, dealid):
    deal = deals[dealid]
    sats_fee = sats * fee
    Damount = satoshis_to_ltc(sats_fee)
    minutes = 0
    await deal['channel'].send(embed=info(f"<@{deal['buyer_id']}> Send {satoshis_to_ltc(sats_fee)} LTC To {deal['address']} (Go to the first message sent here to copy)"))
    while 1:
        if minutes > 5:
            await deal['channel'].send(embed=fail(f"Took to long to send!! Cancelling deal to save api requests"))
            break
        else: 
            await asyncio.sleep(60)
            bal, unconfirmed_bal = get_address_balance(deal['address'])
            minutes = minutes + 1
            if unconfirmed_bal >= sats:
                await deal['channel'].send(content=f"<@{deal['owner']}> <@{deal['buyer_id']}>",embed=succeed("Payment Received! Waiting For Confirmations"))
                break
    while 1:
        if minutes > 5:
            break
        else:
            await asyncio.sleep(60)
            bal, unconfirmed_bal = get_address_balance(deal['address'])
            if bal >= sats:
                await deal['channel'].send(content=f"<@{deal['owner']}> <@{deal['buyer_id']}>",embed=succeed(f"Payment Confirmed! <@{deal['owner']}> Send Product To the buyer, in this channel``"))
            
            
            
            channel = deal['channel']
            await channel.send(embed=info('**Buyer Must Confirm the Poduct**'), view=confirmProductbuttons())
            break


            
        
@bot.event
async def on_message(message: discord.Message):
    if message.author.id == bot.user.id:
        return
    for dealid in deals:
        deal = deals[dealid]
        if deal['channel'].id == message.channel.id:
            stage = deal['stage']
            if message.author.id == deal['owner']:
                if stage == "1":
                    deals[dealid]['stage'] = "2"
                    await message.reply(embed=succeed(f"<@{deal['owner']}> What is the discord id of the person with the ltc?"))
                if stage == "2" :
                    deals[dealid]['buyer_id'] = message.content
                    

                    user_id = int(message.content)
                    user_id2 = int(deal['owner'])
                    user2 = message.guild.get_member(user_id2)
                    user = message.guild.get_member(user_id)
                    channel = deals[dealid]['channel']

                    overwrites = {
                        user : discord.PermissionOverwrite(read_messages=True, send_messages=True),
                        user2 : discord.PermissionOverwrite(read_messages=True, send_messages=True),
                        message.guild.default_role : discord.PermissionOverwrite(read_messages=False)
                    }
                    await channel.edit(overwrites=overwrites)
                    await channel.send(embed=info(f"<@{user_id}> Was Added To The Ticket"),content=f"<@{user_id}>")
                    await message.reply(embed=succeed(f"<@{deal['owner']}> How much money are you recieving in USD? (no $ sign)"))
                    deals[dealid]['stage'] = "3"
                if stage == "3":
                    if suffix_to_int(message.content) >= 1:
                        deals[dealid]['stage'] = "4"
                        deals[dealid]['usd'] = suffix_to_int(message.content)
                        await message.reply(embed=succeed(f"<@{deal['owner']}> What is your ltc address?"))
                    else:
                        deals[dealid]['stage'] = "2"
                        await message.reply(embed=fail(f"<@{deal['owner']}> Min Amount Is $1, try agaon"))
                if stage == "4":
                    deals[dealid]['seller_id'] = message.content
                    asyncio.create_task(final_middleman(usd_to_satoshis(deal['usd']), dealid))
                    deals[dealid]['stage'] = "12345567"
               


def console_embed(console):
    return discord.Embed(title="Connecting To Api", description=f"```{console}```")


@bot.tree.command(name="send_ltc",description="Send LTC")
async def send_ltcC(interaction: discord.Interaction, private_key: str, recipient: str, amount_usd: float):
    if interaction.user.id == your_discord_user_id:
        send_ltc(private_key,recipient,usd_to_satoshis(amount_usd))
        await interaction.response.send_message(embed=succeed("LTC Sent"))
        
        
    else:
        await interaction.response.send_message(embed=fail("Only Admins Can Do This"))
@bot.tree.command(name="get_private_key",description="Get The Private Key Of A Wallet")
async def GETKEY(interaction: discord.Interaction, deal_id: str):
    if interaction.user.id == your_discord_user_id:
        key = deals[deal_id]['key']
        await interaction.response.send_message(embed=info(key))
    else:
        await interaction.response.send_message(embed=fail("Only Admins Can Do This"))
@bot.tree.command(name="get_wallet_balance",description="Get The Balance Of A Wallet")
async def GETBAL(interaction: discord.Interaction, address: str):
    balsats, unbalsats = get_address_balance(address)
    balusd = satoshis_to_usd(balsats)
    balltc = satoshis_to_ltc(balsats)
    unbalusd = satoshis_to_usd(unbalsats)
    unballtc = satoshis_to_ltc(unbalsats)
    embed = discord.Embed(title=f"Address {address}",description=f"**Balance**\n\nUSD: {balusd}\nLTC: {balltc}\nSATS: {balsats}\n\n**Unconfirmed Balance**\n\nUSD: {unbalusd}\nLTC: {unballtc}\nSATS: {unbalsats}")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="new_api_key",description="Change API Keys")
async def new_api_key(interaction: discord.Interaction, key : str):
    if interaction.user.id == your_discord_user_id:
        api_key = key
        await interaction.response.send_message(embed=info(f'switched api key to ||check consol||'))
        print (api_key)
    else:
        await interaction.response.send_message(embed=fail("Only Admins Can Do This"))



@bot.tree.command(name="close", description="close ticket, admin only")
async def close_ticket_test(interaction: discord.Interaction):
    if interaction.user.id == your_discord_user_id:  # Replace your_discord_user_id with the actual ID
        view = CloseTicket()
        embed = fail("close ticket") 
        await interaction.response.send_message(embed=embed, view=view)
    else:
        await interaction.response.send_message(embed=fail("Only Admins Can Do This"))


bot.run(bot_token)
