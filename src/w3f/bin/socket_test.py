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

import logging
# logger = logging.getLogger('websockets')
# logger.setLevel(logging.DEBUG)

# handler = logging.StreamHandler()
# handler.setFormatter(logging.Formatter(fmt='%(asctime)s %(message)s'))
# logger.addHandler(handler)

logging.basicConfig(
    format="%(asctime)s %(name)s %(module)s %(message)s",
    level=logging.DEBUG,
)

# For testing with other contracts
# Change the swap[] list with these
import w3f.lib.contracts.usdc_eth_uni_v2 as usdc_eth_uni_v2
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
CLIENT = bots.DscrdClient(DISCORD_TOKEN)
ETH_ORACLE = co.EthOracle()
BNB_ORACLE = co.BnbOracle()
W3_ETH = InfuraEth(hd.infura_key)
W3_BSC = GetBlockBsc(hd.GETBLOCK_KEY)

async def ws_event_loop(w3: W3, swap: SWAP.Swap, oracle):
    log.log(f"asyncio.create_task(ws_event_loop({swap.name}))")
    print(f"Connected to Web3: {w3.w3.is_connected()}")
    async for ws in websockets.connect(w3.ws, ping_timeout=41):
        try:
            subscription = await ews.SwapData.subscribe(ws, swap.address)
            log.log(f'Socket subscription {swap.name}: {subscription}')
            while True:
                    swap_data = await ews.SwapData.wait(ws, swap.chain)
                    log.log(swap_data)
                    if swap_data is not None:
                        text_msg = swap.buy_sell_msg(swap_data, oracle.get())
                        log.log(text_msg)

        except websockets.ConnectionClosed as cc:
            log.log(f'[token] ConnectionClosed: {cc}')
        except Exception as e:
            log.log(f'[token] Exception: {e}')

async def run():
    ETH_ORACLE.create_task()
    BNB_ORACLE.create_task()
    task = asyncio.create_task(ws_event_loop(W3_ETH, SWAPS[0], ETH_ORACLE))
    try:
        asyncio.create_task(ws_event_loop(W3_ETH, SWAPS[1], ETH_ORACLE))
    except: pass
    try:
        asyncio.create_task(ws_event_loop(W3_BSC, BSC_SWAP, BNB_ORACLE))
    except: pass
    await task


def main():
    whoami.log_whoami()
    asyncio.run(run())


if __name__ == "__main__":
    main()
