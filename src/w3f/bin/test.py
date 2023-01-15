#!/usr/bin/env python3

import asyncio, discord, websockets, json, os
from w3f.lib import bots
from w3f.lib import doe_nft_data
from w3f.lib import whoami
import w3f.lib.logger as log
import w3f.lib.op_events as osea
import w3f.lib.crypto_oracle as co
import w3f.hidden_details as hd
from web3 import Web3
from ens import ENS

w3 = Web3(Web3.HTTPProvider(hd.eth_mainnet))
print(f"Connected to Web3: {w3.isConnected()}")
ns = ENS.fromWeb3(w3)
print(ns.name("0x5dA93cF2d5595Dd68Daed256DFbFF62c7ebBB298"))

exit()
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
                log.log(event.base_describe())

        except websockets.ConnectionClosed as cc:
            log.log(f'ConnectionClosed: {cc}')
        except Exception as e:
            log.log(f'Exception: {e}')

def main():
    whoami.log_whoami()
    asyncio.run(ws_loop())

if __name__ == "__main__":
    main()
