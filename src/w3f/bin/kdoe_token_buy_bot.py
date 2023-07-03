#!/usr/bin/env python3

import asyncio, discord, websockets, os
import telegram as tg
import w3f.lib.swap as SWAP
import w3f.lib.eth_event_socket as ews
import w3f.lib.bots as bots
import w3f.lib.logger as log
import w3f.lib.crypto_oracle as co
from w3f.lib.contracts import kdoe_eth
from w3f.lib import whoami
from w3f.lib.web3 import W3, GetBlockBsc, InfuraEth
from ens import ENS

# For testing with other contracts
# Change the swap[] list with these
import w3f.lib.contracts.usdc_eth as usdc_eth
import w3f.lib.contracts.eth_usdt as eth_usdt

######## Details required from the user
import w3f.hidden_details as hd
INFURA_KEY = hd.infura_key
DISCORD_TOKEN = hd.dscrd['token']
TG_TOKEN = "hd.TG['token']"
TG_MAIN_CHAN = "hd.TG['main_channel']"
######## Details required from the user


# SWAPS = [usdc_eth.SWAP, eth_usdt.SWAP]
SWAPS = [kdoe_eth.ETH_SWAP]
BSC_SWAP = kdoe_eth.BNB_SWAP
DSCRD_CHANS = bots.DscrdChannels()
CLIENT = bots.DscrdClient(DISCORD_TOKEN)
BOTS_ = bots.Bots.init_none()
ETH_ORACLE = co.EthOracle()
BNB_ORACLE = co.BnbOracle()
W3_ETH = InfuraEth(hd.infura_key)
W3_BSC = GetBlockBsc(hd.GETBLOCK_KEY)

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
        ETH_ORACLE.create_task()
        BNB_ORACLE.create_task()
        asyncio.create_task(ws_event_loop(W3_ETH, SWAPS[0], ETH_ORACLE))
        try:
            asyncio.create_task(ws_event_loop(W3_ETH, SWAPS[1], ETH_ORACLE))
        except: pass
        try:
            asyncio.create_task(ws_event_loop(W3_BSC, BSC_SWAP, BNB_ORACLE))
        except: pass
    await DSCRD_CHANS.ipdoe_dbg.send(f"Start: {os.path.basename(__file__)} {whoami.get_whoami()}")

async def ws_event_loop(w3: W3, swap: SWAP.Swap, oracle):
    log.log(f"asyncio.create_task(ws_event_loop({swap.name}))")
    print(f"Connected to Web3: {w3.w3.is_connected()}")
    async for ws in websockets.connect(w3.ws):
        try:
            subscription = await ews.SwapData.subscribe(ws, swap.address)
            await DSCRD_CHANS.ipdoe_dbg.send_and_log(f'Socket subscription {swap.name}: {subscription}')
            ll_event = log.LogLatch()
            while True:
                try:
                    swap_data = await ews.SwapData.wait(ws, swap.chain)
                    if swap_data is not None:
                        text_msg = swap.buy_sell_msg(swap_data, oracle.get())
                        log.log(text_msg)
                        await DSCRD_CHANS.ipdoe_swaps.send(to_embed(text_msg))
                        ll_event.reset()
                except Exception as e:
                    ll_event.log(f'{e}')
                    if (ll_event.reached_limit()):
                        await DSCRD_CHANS.ipdoe_dbg.send_and_log(f'Exit swap {swap.name}: {e}')
                        raise

        except websockets.ConnectionClosed as cc:
            await DSCRD_CHANS.ipdoe_dbg.send_and_log(f'[token] ConnectionClosed: {cc}')
        except Exception as e:
            await DSCRD_CHANS.ipdoe_dbg.send_and_log(f'[token] Exception: {e}')

def main():
    whoami.log_whoami()
    CLIENT.run()

if __name__ == "__main__":
    main()
