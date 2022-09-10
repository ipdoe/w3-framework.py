#!/usr/bin/env python3

from web3 import Web3
import asyncio,  discord, datetime,  git,  websockets
import telegram as tg
import w3f.lib.swap as swap
import w3f.lib.eth_event_socket as ews
import w3f.lib.bots as bots
import w3f.lib.logger as log
import w3f.lib.crypto_oracle as co
import w3f.lib.contracts.usdc_doe as usdc_doe
import w3f.lib.contracts.eth_doe as eth_doe

# For testing with other contracts
# Change the swap[] list with these
import w3f.lib.contracts.usdc_eth as usdc_eth
import w3f.lib.contracts.eth_usdt as eth_usdt

DSCRD_CHANS = bots.DscrdChannels()
######## Details required from the user
import w3f.hidden_details as hd
infura_key = hd.infura_key
DISCORD_TOKEN = hd.dscrd['token']
DSCRD_CHANS.doe_token_buys.id = hd.dscrd['doe_token_buys']
DSCRD_CHANS.ipdoe_dbg.id = hd.dscrd['ipdoe_dbg']
DSCRD_CHANS.ipdoe_swaps.id = hd.dscrd['ipdoe_swaps']
tg_token = hd.TG['token']
tg_main_chan = hd.TG['main_channel']
tg_fr_chan = hd.TG['fr_channel']
######## Details required from the user

swaps = [usdc_doe.swap, eth_doe.swap]
# swaps = [usdc_eth.swap, eth_usdt.swap]

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
    DSCRD_CHANS.init_channels(client)
    ETH_PRICE.create_task()
    log.log("ETH_PRICE.create_task()")
    asyncio.create_task(ws_event_loop(swaps[0]))
    log.log("asyncio.create_task(ws_event_loop(swaps[0]))")
    asyncio.create_task(ws_event_loop(swaps[1]))
    log.log("asyncio.create_task(ws_event_loop(swaps[1]))")

def get_usd_price(swap_data: ews.SwapData, swap: swap.Swap):
    in_token = swap.tokens[swap_data.in_t.id]
    if (in_token.tracker == 'eth'):
        return float(in_token.to_decimal(swap_data.in_t.ammount)) * ETH_PRICE.get()
    return 0.0

async def handle_event(swap_data: ews.SwapData, swap: swap.Swap):
    usd = get_usd_price(swap_data, swap)
    text_msg = f"In: {swap.tokens[swap_data.in_t.id].to_string(swap_data.in_t.ammount)}"
    if (usd > 0.0):
        text_msg = text_msg + f' (${usd:,.2f})'
    text_msg = text_msg + f"\nOut: {swap.tokens[swap_data.out_t.id].to_string(swap_data.out_t.ammount)}\n"
    text_msg = text_msg + f'Tx: [{swap_data.tx[0:8]}](https://etherscan.io/tx/{swap_data.tx})'

    # Check buy
    red_green_msg = '🔴🔴🔴🔴🔴🔴\n' + text_msg
    buy = swap.buy_token == swap_data.out_t.id
    if buy:
        red_green_msg = '🟢🟢🟢🟢🟢🟢\n' + text_msg
        await DSCRD_CHANS.doe_token_buys.send(to_embed(red_green_msg))
        send_tg_message(hd.TG['test_channel'], red_green_msg)

    log.log(red_green_msg) # Debug message
    await DSCRD_CHANS.ipdoe_swaps.send(to_embed(red_green_msg))

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
                    decoded = await ews.wait_swap(ws)
                    if decoded is not None:
                        await handle_event(decoded, swap)
                        ll_event.reset()
                except Exception as e:
                    ll_event.log(f'{e}')
                    if (ll_event.reached_limit()):
                        await DSCRD_CHANS.ipdoe_dbg.send(log.slog(f'Exit swap {swap.name}: {e}'))
                        raise
            
        except websockets.ConnectionClosed as cc:
            ll_connect.log(f'ConnectionClosed: {cc}')
        except Exception as e:
            ll_connect.log(f'Exception: {e}')

def main():
    log.log_version()
    client.run(DISCORD_TOKEN)

if __name__ == "__main__":
    main()