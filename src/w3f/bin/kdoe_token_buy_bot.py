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

######## Details required from the user
import w3f.hidden_details as hd
INFURA_KEY = hd.infura_key
DISCORD_TOKEN = hd.dscrd['token']
TG_TOKEN = hd.TG['token']
TG_MAIN_CHAN = hd.TG['main_channel']
######## Details required from the user

# swaps = [usdc_eth.swap, eth_usdt.swap]
SWAPS = [kdoe_eth.swap]

DSCRD_CHANS = bots.DscrdChannels()
CLIENT = bots.DscrdClient(DISCORD_TOKEN)
BOTS_ = bots.Bots.init_none()
ORACLE = co.EthOracle()

def to_embed(message):
    embed = discord.Embed()
    embed.description = message
    return embed

def send_tg_message(chat_id, message):
    if BOTS_.tg is not None:
        try:
            BOTS_.tg.send_message(chat_id=chat_id, parse_mode=tg.ParseMode.MARKDOWN,
                disable_web_page_preview=True, text=message)
        except Exception as e:
            log.log("Failed to send message to TG\n" + str(e))

@CLIENT.event
async def on_ready():
    log.log(f'We have logged in as {CLIENT.user}')
    try:
        BOTS_.tg = tg.Bot(token=TG_TOKEN)
    except:
        log.log("TG inactive")
    DSCRD_CHANS.init_with_hidden_details(CLIENT)
    if not CLIENT.ready:
        CLIENT.ready = True
        ORACLE.create_task()
        log.log("ORACLE.create_task()")
        asyncio.create_task(ws_event_loop(SWAPS[0]))
        try:
            asyncio.create_task(ws_event_loop(SWAPS[1]))
        except: pass
    await DSCRD_CHANS.ipdoe_dbg.send(f"Start: {os.path.basename(__file__)} {whoami.get_whoami()}")
    await DSCRD_CHANS.ipdoe_swaps.send(f"Start: {os.path.basename(__file__)} {whoami.get_whoami()}")

def get_usd_price(swap_data: ews.SwapData, swap: swap.Swap):
    token = swap.tokens[swap_data.in_t.id]
    if (token.tracker == 'eth'):
        return float(token.to_decimal(swap_data.in_t.ammount)) * ORACLE.get()
    token = swap.tokens[swap_data.out_t.id]
    if (token.tracker == 'eth'):
        return float(token.to_decimal(swap_data.out_t.ammount)) * ORACLE.get()
    return 0.0

async def ws_event_loop(swap: swap.Swap):
    log.log(f"asyncio.create_task(ws_event_loop({swap.name}))")
    w3 = Web3(Web3.HTTPProvider(hd.eth_mainnet))
    print(f"Connected to Web3: {w3.isConnected()}")
    name_service = ENS.fromWeb3(w3)
    async for ws in websockets.connect(hd.eth_mainnet_ws):
        try:
            subscription = await ews.subscribe_swap(ws, swap.address)
            log.log(f'Socket subscription {swap.name} [{INFURA_KEY[0:5]}...]: {subscription}')
            await DSCRD_CHANS.ipdoe_dbg.send(log.slog(f'Entered swap {swap.name}'))
            ll_event = log.LogLatch()
            while True:
                try:
                    swap_data = await ews.wait_swap(name_service, ws)
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
    whoami.log_whoami()
    CLIENT.run()

if __name__ == "__main__":
    main()
