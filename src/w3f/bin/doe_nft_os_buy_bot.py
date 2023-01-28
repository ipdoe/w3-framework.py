#!/usr/bin/env python3

import asyncio, discord, websockets, json, os
from w3f.lib import bots
from w3f.lib import doe_nft_data
from w3f.lib import whoami
import w3f.lib.logger as log
import w3f.lib.op_events as osea
import w3f.lib.crypto_oracle as co
import w3f.hidden_details as hd

######## Details required from the user
import w3f.hidden_details as hd
DISCORD_TOKEN = hd.dscrd['token']
TG_TOKEN = hd.TG['token']
TG_MAIN_CHAN = hd.TG['main_channel']
TG_TEST_CHAN = hd.TG['test_channel']
######## Details required from the user

DSCRD_CHANS = bots.DscrdChannels()
TG_CHAN = bots.TgChannel()
CLIENT = bots.DscrdClient()
COLLECTION_SLUG = 'dogs-of-elon'
ETH_PRICE = co.EthPrice()
METADATA = doe_nft_data.Metadata()

def to_discord_embed(item: osea.ItemBase):
    embed = discord.Embed()
    embed.description = item.describe(METADATA.get_rarity(item.nft_id))
    embed.set_image(url=item.img_url())
    return embed

async def subscribe(ws):
    await ws.send(json.dumps({
        "topic": f"collection:{COLLECTION_SLUG}", "event": "phx_join", "payload": {}, "ref": 0
        }))
    response = json.loads(await asyncio.wait_for(ws.recv(), timeout=10))
    msg = f"Subscription to {response['topic']}: {response['payload']['status']}"
    log.log(msg)
    await DSCRD_CHANS.ipdoe_dbg.send(msg)

async def send_event(event):
    msg_sent = False
    while not msg_sent:
        try:
            if isinstance(event, osea.ItemBase):
                embed = to_discord_embed(event)
                log.log(embed.description)
                if type(event) is osea.ItemListed:
                    msg_sent = await DSCRD_CHANS.ipdoe_nft_listings.send(embed)
                    await DSCRD_CHANS.doe_nft_listing.send(embed)
                elif type(event) is osea.ItemSold:
                    ####  ITME SOLD --> Tell the world!!!!
                    msg_sent = await DSCRD_CHANS.ipdoe_nft_sales.send(embed)
                    await DSCRD_CHANS.doe_nft_sales.send(embed)
                    await TG_CHAN.send_with_img(f'[ ]({event.img_url()}){embed.description}')
                    ####  ITME SOLD --> Tell the world!!!!
                elif type(event) is osea.ItemReceivedOffer or type(event) is osea.ItemReceivedBid:
                    msg_sent = await DSCRD_CHANS.ipdoe_nft_offers.send(embed)
                await DSCRD_CHANS.ipdoe_nft.send(embed)

            log.log(event.base_describe())
            msg_sent |= await DSCRD_CHANS.ipdoe_dbg.send(event.base_describe())
        except Exception as e:
            log.log(f'Exception: {e}')

async def dequeu_loop(nft_event_q: asyncio.Queue):
    log.log("Dequeuing")
    while True:
        event = await nft_event_q.get()
        await send_event(event)

async def ws_loop():
    log.log("Websocket loop running")
    nft_event_q = asyncio.Queue()
    asyncio.create_task(dequeu_loop(nft_event_q))
    ws_url = f'wss://stream.openseabeta.com/socket/websocket?token={hd.op_sea_key}'
    log.log(f'url: {ws_url[:-26]}...')
    async for ws in websockets.connect(ws_url):
        try:
            log.log("Connection OK")
            await subscribe(ws)
            while True:
                os_event = osea.create_event(json.loads(await ws.recv()), ETH_PRICE.get())
                nft_event_q.put_nowait(os_event)
        except websockets.ConnectionClosed as cc:
            log.log(f'ConnectionClosed: {cc}')
            await DSCRD_CHANS.ipdoe_dbg.send(f'ConnectionClosed: {cc}')
        except Exception as e:
            log.log(f'Exception: {e}')
            await DSCRD_CHANS.ipdoe_dbg.send(f'Exception: {e}')

@CLIENT.event
async def on_ready():
    log.log("Discord ready")
    DSCRD_CHANS.init_with_hidden_details(CLIENT)
    await TG_CHAN.init(TG_TOKEN, TG_MAIN_CHAN, 'tg_main_chan')
    log.log("Channels initialized")
    if not CLIENT.ready_called:
        CLIENT.ready_called = True
        ETH_PRICE.create_task()
        asyncio.create_task(ws_loop())

    await DSCRD_CHANS.ipdoe_dbg.send(f"Start: {os.path.basename(__file__)} {whoami.get_whoami()}")

def main():
    whoami.log_whoami()
    CLIENT.run(DISCORD_TOKEN)

if __name__ == "__main__":
    main()
