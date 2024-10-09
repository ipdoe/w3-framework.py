#!/usr/bin/env python3

import asyncio
import discord
import json
import websockets
from websockets.client import WebSocketClientProtocol

import w3f.lib.logger as log
import w3f.lib.op_events as osea
from w3f.lib import bots
from w3f.lib.bots import TgBot, ChatType
from w3f.lib import whoami
from w3f.lib.metadata import Metadata
from w3f.lib.crypto_oracle import EthOracle
from w3f.lib.local_discord import DiscordChannels

MOCK_MSG = """[ ](https://api.dogsofelon.io/ipfs/a28d5dc2279a0f535adcae2aad0c3bdb/images/7021.png)📰📰 Listing 7021 📰📰
Rank: 1784
Price: 99.0 ETH ($235,935.07)
[From: ](https://opensea.io/assets/ethereum/0xd8cdb4b17a741dc7c6a57a650974cd2eba544ff7/7021)"""

MOCK_CAPTION = """📰📰 Listing 7021 📰📰
Rank: 1784
Price: 99.0 ETH ($235,935.07)
[From: 0x123456](https://opensea.io/assets/ethereum/0xd8c"""
MOCK_PHOTO = "https://api.dogsofelon.io/ipfs/a28d5dc2279a0f535adcae2aad0c3bdb/images/7021.png"


class OsNftBuyBot(bots.DscrdClient):
    def __init__(self, name: str, discord_chans: DiscordChannels, oracle: EthOracle, discord_token: str,
                 metadata: Metadata, os_token, tgBot: TgBot) -> None:
        self.name = name
        self.discord_chans = discord_chans
        self.oracle = oracle
        self.metadata = metadata
        self.os_token = os_token
        self.tgBot = tgBot
        super().__init__(discord_token)

    def to_discord_embed(self, item: osea.ItemBase):
        embed = discord.Embed()
        embed.description = item.describe(self.metadata.get_rarity(item.nft_id))
        embed.set_image(url=item.image_url)
        return embed

    def to_tg_photo(self, item: osea.ItemBase):
        return item.describe(self.metadata.get_rarity(item.nft_id)), item.image_url

    async def subscribe(self, ws: WebSocketClientProtocol):
        subscription = {"topic": f"collection:{self.metadata.OS_SLUG}", "event": "phx_join", "payload": {}, "ref": 0}
        await ws.send(json.dumps(subscription))
        response = json.loads(await asyncio.wait_for(ws.recv(), timeout=10))
        msg = f"Subscription to {response['topic']}: {response['payload']['status']}"
        log.log(msg)
        await self.tgBot.send_debug(msg)
        await self.discord_chans.send_debug(msg)

    async def send_event(self, event: osea.EventBase):
        try:
            if event.timestamp.older_than():
                await self.discord_chans.send_debug(f"Older than: {event.base_describe()}")
                log.log(f"Older than: {event.base_describe()}")
            else:
                if isinstance(event, osea.ItemBase):
                    msg_sent = False
                    embed = self.to_discord_embed(event)
                    tg_caption, tg_photo = self.to_tg_photo(event)
                    if type(event) is osea.ItemListed:
                        log.log(tg_caption)
                        msg_sent = await self.tgBot.send_photo(ChatType.LISTING, caption=tg_caption, photo_url=tg_photo)
                        msg_sent = await self.discord_chans.send_listings(embed) or msg_sent
                    elif type(event) is osea.ItemSold:
                        # ###  ITME SOLD --> Tell the world!!!!
                        msg_sent = await self.tgBot.send_photo(ChatType.SALE, caption=tg_caption, photo_url=tg_photo)
                        msg_sent = await self.discord_chans.send_buys(embed)
                        # ###  ITME SOLD --> Tell the world!!!!
                    elif type(event) is osea.ItemReceivedOffer or type(event) is osea.ItemReceivedBid:
                        msg_sent = await self.discord_chans.send_other(embed)

                    if (msg_sent):
                        log.log(embed.description)
                        await self.discord_chans.send_debug(event.base_describe())
                        await self.tgBot.send_debug(str(embed.description))

        except Exception as e:
            log.log(f'Exception: {e}')
            await asyncio.sleep(1)

    async def dequeu_loop(self, nft_event_q: asyncio.Queue):
        log.log("Dequeuing")
        while True:
            event = await nft_event_q.get()
            await self.send_event(event)

    async def ws_loop(self):
        log.log("Websocket loop running")
        nft_event_q = asyncio.Queue()
        asyncio.create_task(self.dequeu_loop(nft_event_q))
        ws_url = f'wss://stream.openseabeta.com/socket/websocket?token={self.os_token}'
        log.log(f'url: {ws_url[:-26]}...')
        async for ws in websockets.connect(ws_url):
            try:
                log.log("Connection OK")
                await self.subscribe(ws)
                while True:
                    os_event = osea.create_event(json.loads(await ws.recv()), self.oracle.get(), self.os_token)
                    nft_event_q.put_nowait(os_event)
            except websockets.ConnectionClosed as cc:
                log.log(f'ConnectionClosed: {cc}')
                await self.discord_chans.send_debug(f'ConnectionClosed: {cc}')
            except Exception as e:
                log.log(f'Exception: {e}')
                await self.discord_chans.send_debug(f'Exception: {e}')

    async def on_ready(self):
        log.log("Discord ready")
        self.discord_chans.init_channels(self)
        log.log("Channels initialized")
        if not self.ready:
            self.ready = True
            self.oracle.create_task()
            asyncio.create_task(self.ws_loop())
            await self.tgBot.send_debug(log.slog("Started"))
        await self.discord_chans.send_debug(f"Start: {whoami.get_whoami(f'{self.name}')}")

    def run(self):
        self.loop.create_task(self.tgBot.start())
        super().run()
