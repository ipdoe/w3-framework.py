#!/usr/bin/env python3

import asyncio, discord, websockets, json, os
from w3f.lib import bots
from w3f.lib import doe_nft_data
from w3f.lib import whoami
import w3f.lib.logger as log
import w3f.lib.op_events as osea
import w3f.lib.crypto_oracle as co
import w3f.hidden_details as hd

DSCRD_CHANS = bots.DscrdChannels()
TG_CHAN = bots.TgChannel()

######## Details required from the user
import w3f.hidden_details as hd
DISCORD_TOKEN = hd.dscrd['token']
DSCRD_CHANS.doe_nft_listing.id = hd.dscrd['doe_nft_listing']
DSCRD_CHANS.doe_nft_sales.id = hd.dscrd['doe_nft_sales']
DSCRD_CHANS.doe_nft_floor.id = hd.dscrd['doe_nft_floor']
DSCRD_CHANS.doe_token_buys.id = hd.dscrd['doe_token_buys']
def set_ipdoe_chans():
    try:
        global DSCRD_CHANS
        DSCRD_CHANS.ipdoe_dbg.id = hd.dscrd['ipdoe_dbg']
        DSCRD_CHANS.ipdoe_nft.id = hd.dscrd['ipdoe_nft']
        DSCRD_CHANS.ipdoe_nft_sales.id = hd.dscrd['ipdoe_nft_sales']
        DSCRD_CHANS.ipdoe_nft_listings.id = hd.dscrd['ipdoe_nft_listings']
        DSCRD_CHANS.ipdoe_nft_offers.id = hd.dscrd['ipdoe_nft_offers']
        # DSCRD_CHANS.ipdoe_nft_sales.id = 0
        # DSCRD_CHANS.ipdoe_nft_listings.id = 0
        # DSCRD_CHANS.ipdoe_nft_offers.id = 0
        DSCRD_CHANS.ipdoe_swaps.id = hd.dscrd['ipdoe_swaps']
    except Exception as e:
        log.log("Failed to setup all ipdoe channels: " + str(e))
tg_token = hd.TG['token']
tg_main_chan = hd.TG['main_channel']
tg_test_chan = hd.TG['test_channel']
######## Details required from the user

client = discord.Client()
doe_channel = None
dbg_channel = None
ipdoe_nft_chan = None
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

async def ws_loop():
    ws_url = f'wss://stream.openseabeta.com/socket/websocket?token={hd.op_sea_key}'
    log.log(f'url: {ws_url[:-26]}...')
    async for ws in websockets.connect(ws_url):
        try:
            log.log("Connection OK")
            await subscribe(ws)
            while True:
                response = json.loads(await ws.recv())
                event = osea.create_event(response, ETH_PRICE.get())
                if isinstance(event, osea.ItemBase):
                    embed = to_discord_embed(event)
                    log.log(embed.description)
                    if type(event) is osea.ItemListed:
                        await DSCRD_CHANS.ipdoe_nft_listings.send(embed)
                        await DSCRD_CHANS.doe_nft_listing.send(embed)
                    elif type(event) is osea.ItemSold:
                        ####  ITME SOLD --> Tell the world!!!!
                        await DSCRD_CHANS.ipdoe_nft_sales.send(embed)
                        await DSCRD_CHANS.doe_nft_sales.send(embed)
                        await TG_CHAN.send_with_img(f'[ ]({event.img_url()}){embed.description}')
                        ####  ITME SOLD --> Tell the world!!!!
                    elif type(event) is osea.ItemReceivedOffer or type(event) is osea.ItemReceivedBid:
                        await DSCRD_CHANS.ipdoe_nft_offers.send(embed)
                    await DSCRD_CHANS.ipdoe_nft.send(embed)

                log.log(event.base_describe())
                await DSCRD_CHANS.ipdoe_dbg.send(event.base_describe())

        except websockets.ConnectionClosed as cc:
            log.log(f'ConnectionClosed: {cc}')
            await DSCRD_CHANS.ipdoe_dbg.send(f'ConnectionClosed: {cc}')
        except Exception as e:
            log.log(f'Exception: {e}')
            await DSCRD_CHANS.ipdoe_dbg.send(f'Exception: {e}')

@client.event
async def on_ready():
    global DSCRD_CHANS
    global TG_CHAN
    set_ipdoe_chans()
    DSCRD_CHANS.init_channels(client)
    await TG_CHAN.init(tg_token, tg_main_chan, 'tg_main_chan')
    ETH_PRICE.create_task()
    await DSCRD_CHANS.ipdoe_dbg.send(f"Start: {os.path.basename(__file__)} {whoami.get_whoami()}")
    asyncio.create_task(ws_loop())

def main():
    whoami.log_whoami()
    client.run(DISCORD_TOKEN)

if __name__ == "__main__":
    main()
