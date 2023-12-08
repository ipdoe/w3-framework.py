#!/usr/bin/env python3

import asyncio, discord, websockets, os, json
import telegram as tg
import w3f.lib.swap as SWAP
import w3f.lib.eth_event_socket as ews
import w3f.lib.bots as bots
import w3f.lib.logger as log
import w3f.lib.crypto_oracle as co
from w3f.lib.contracts import kdoe_eth
from w3f.lib import whoami
from w3f.lib.web3 import W3, GetBlockBsc, InfuraEth, SwapContract
from ens import ENS

import logging
# logger = logging.getLogger('websockets')
# logger.setLevel(logging.DEBUG)

# handler = logging.StreamHandler()
# handler.setFormatter(logging.Formatter(fmt='%(asctime)s %(message)s'))
# logger.addHandler(handler)

# logging.basicConfig(
#     format="%(asctime)s %(name)s %(module)s %(message)s",
#     level=logging.DEBUG,
# )

# For testing with other contracts
# Change the swap[] list with these
# import w3f.lib.contracts.usdc_eth as usdc_eth
import w3f.lib.contracts.eth_usdt as eth_usdt

######## Details required from the user
import w3f.hidden_details as hd
INFURA_KEY = hd.infura_key
DISCORD_TOKEN = hd.dscrd['token']
TG_TOKEN = "hd.TG['token']"
TG_MAIN_CHAN = "hd.TG['main_channel']"
######## Details required from the user


# SWAPS = eth_usdt.Contract()
# SWAPS = [kdoe_eth.ETH_SWAP]
BSC_SWAP = kdoe_eth.BNB_SWAP
DSCRD_CHANS = bots.DscrdChannels()
CLIENT = bots.DscrdClient(DISCORD_TOKEN)
BOTS_ = bots.Bots.init_none()
ETH_ORACLE = co.EthOracle()
BNB_ORACLE = co.BnbOracle()
W3_ETH = InfuraEth(hd.infura_key)
W3_BSC = GetBlockBsc(hd.GETBLOCK_KEY)

ETH_CONTRACT = kdoe_eth.Contract(W3_ETH)
BSC_CONTRACT = kdoe_eth.BscContract(W3_BSC)


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
    except Exception:
        log.log("TG inactive")
    DSCRD_CHANS.init_with_hidden_details(CLIENT)
    if not CLIENT.ready:
        CLIENT.ready = True
        ETH_ORACLE.create_task()
        BNB_ORACLE.create_task()
        asyncio.create_task(ws_event_loop(ETH_CONTRACT, ETH_ORACLE, '🧩'))
        try:
            asyncio.create_task(ws_event_loop(BSC_CONTRACT, BNB_ORACLE, '🟡'))
        except Exception:
            pass
    msg = f"Start: {os.path.basename(__file__)} {whoami.get_whoami()}"
    log.log(msg)
    await DSCRD_CHANS.ipdoe_dbg.send(f"Start: {os.path.basename(__file__)} {whoami.get_whoami()}")


async def wait(ws):
    try:
        json_response = json.loads(await ws.recv())
    except asyncio.TimeoutError:
        return None

    return json_response['params']['result']


async def ws_event_loop(swap: SwapContract, oracle, buy_char):
    log.log(f"asyncio.create_task(ws_event_loop({swap.name}))")
    print(f"Connected to Web3: {swap.w3.w3.is_connected()}")
    async for ws in websockets.connect(swap.w3.ws, ping_timeout=41):
        try:
            subscription = await ews.SwapData.subscribe(ws, swap.address)
            msg = f'Socket subscription {swap.name}: {subscription}'
            log.log(msg)
            await DSCRD_CHANS.ipdoe_dbg.send_and_log(f'Socket subscription {swap.name}: {subscription}')
            ll_event = log.LogLatch()
            while True:
                try:
                    log_data = await wait(ws)
                    with open("dump_tx.json", 'w') as f:
                        json.dump(log_data, f, indent=2)
                    if log_data is not None:
                        swap_event = swap.decode_swap_event(log_data)
                        text_msg = swap_event.buy_sell_msg(oracle.get(), buy_char)
                        log.log(text_msg)
                        await DSCRD_CHANS.ipdoe_swaps.send(to_embed(text_msg))
                        ll_event.reset()
                except Exception as e:
                    ll_event.log(f'{e}')
                    if (ll_event.reached_limit()):
                        await DSCRD_CHANS.ipdoe_dbg.send_and_log(f'Exit swap {swap.name}: {e}')
                        raise

        except websockets.ConnectionClosed as cc:
            msg = f'[token] ConnectionClosed: {cc}'
            await DSCRD_CHANS.ipdoe_dbg.send_and_log(msg)
            log.log(msg)
        except Exception as e:
            msg = f'[token] Exception: {e}'
            await DSCRD_CHANS.ipdoe_dbg.send_and_log(msg)
            log.log(msg)


def main():
    whoami.log_whoami()
    CLIENT.run()


if __name__ == "__main__":
    main()
