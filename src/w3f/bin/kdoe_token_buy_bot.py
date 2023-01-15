#!/usr/bin/env python3

import asyncio, discord, websockets, os
import telegram as tg
import w3f.lib.swap as swap
import w3f.lib.eth_event_socket as ews
import w3f.lib.bots as bots
import w3f.lib.logger as log
import w3f.lib.crypto_oracle as co
from w3f.lib.contracts import kdoe_eth
from w3f.lib import whoami
from web3 import Web3
from ens import ENS

# For testing with other contracts
# Change the swap[] list with these
import w3f.lib.contracts.usdc_eth as usdc_eth
import w3f.lib.contracts.eth_usdt as eth_usdt

DSCRD_CHANS = bots.DscrdChannels()
NS = None
######## Details required from the user
import w3f.hidden_details as hd
infura_key = hd.infura_key
DISCORD_TOKEN = hd.dscrd['token']
tg_token = hd.TG['token']
tg_main_chan = hd.TG['main_channel']
tg_fr_chan = hd.TG['fr_channel']
######## Details required from the user

# swaps = [usdc_eth.swap, eth_usdt.swap]
swaps = [kdoe_eth.swap]

intents = discord.Intents.default()
client = discord.Client()
bots_ = bots.Bots.init_none()
ETH_PRICE = co.EthPrice()

def to_embed(message):
    embed = discord.Embed()
    embed.description = message
    return embed

def send_tg_message(chat_id, message):
    if bots_.tg is not None:
        try:
            bots_.tg.send_message(chat_id=chat_id, parse_mode=tg.ParseMode.MARKDOWN,
                disable_web_page_preview=True, text=message)
        except Exception as e:
            log.log("Failed to send message to TG\n" + str(e))

@client.event
async def on_ready():
    log.log(f'We have logged in as {client.user}')
    try:
        bots_.tg = tg.Bot(token=tg_token)
    except:
        log.log("TG inactive")
    global DSCRD_CHANS
    DSCRD_CHANS.init_with_hidden_details(client)
    ETH_PRICE.create_task()
    log.log("ETH_PRICE.create_task()")
    asyncio.create_task(ws_event_loop(swaps[0]))
    log.log(f"asyncio.create_task(ws_event_loop({swaps[0].name}))")
    try:
        asyncio.create_task(ws_event_loop(swaps[1]))
        log.log(f"asyncio.create_task(ws_event_loop({swaps[1].name}))")
    except: pass
    await DSCRD_CHANS.ipdoe_dbg.send(f"Start: {os.path.basename(__file__)} {whoami.get_whoami()}")
    await DSCRD_CHANS.ipdoe_swaps.send(f"Start: {os.path.basename(__file__)} {whoami.get_whoami()}")

def get_usd_price(swap_data: ews.SwapData, swap: swap.Swap):
    token = swap.tokens[swap_data.in_t.id]
    if (token.tracker == 'eth'):
        return float(token.to_decimal(swap_data.in_t.ammount)) * ETH_PRICE.get()
    token = swap.tokens[swap_data.out_t.id]
    if (token.tracker == 'eth'):
        return float(token.to_decimal(swap_data.out_t.ammount)) * ETH_PRICE.get()
    return 0.0

async def ws_event_loop(swap: swap.Swap):
    ll_connect = log.LogLatch()
    async for ws in websockets.connect(hd.eth_mainnet_ws):
        try:
            ll_connect.reset()
            subscription = await ews.subscribe_swap(ws, swap.address)
            log.log(f'Socket subscription {swap.name} [{infura_key[0:5]}...]: {subscription}')
            await DSCRD_CHANS.ipdoe_dbg.send(log.slog(f'Entered swap {swap.name}'))
            ll_event = log.LogLatch()
            while True:
                try:
                    swap_data = await ews.wait_swap(NS, ws)
                    if swap_data is not None:
                        text_msg = swap.buy_sell_msg(swap_data, get_usd_price(swap_data, swap))
                        log.log(text_msg)
                        await DSCRD_CHANS.ipdoe_swaps.send(to_embed(text_msg))
                        ll_event.reset()
                except Exception as e:
                    ll_event.log(f'{e}')
                    if (ll_event.reached_limit()):
                        await DSCRD_CHANS.ipdoe_dbg.send(log.slog(f'Exit swap {swap.name}: {e}'))
                        raise
            
        except websockets.ConnectionClosed as cc:
            log.log(f'[token] ConnectionClosed: {cc}')
            await DSCRD_CHANS.ipdoe_dbg.send(f'[token] ConnectionClosed: {cc}')
        except Exception as e:
            log.log(f'[token] Exception: {e}')
            await DSCRD_CHANS.ipdoe_dbg.send(f'[token] Exception: {e}')

def main():
    global NS
    whoami.log_whoami()
    w3 = Web3(Web3.HTTPProvider(hd.eth_mainnet))
    print(f"Connected to Web3: {w3.isConnected()}")
    NS = ENS.fromWeb3(w3)
    client.run(DISCORD_TOKEN)

if __name__ == "__main__":
    main()