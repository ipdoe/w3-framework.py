#!/usr/bin/env python3

import pathlib

import w3f.hidden_details as hd


from w3f.lib import whoami
from w3f.lib.bots import TgBot, ChatType
from w3f.lib.crypto_oracle import EthOracle
from w3f.lib.local_discord import DiscordChannels
from w3f.lib.os_nft_buy_bot import OsNftBuyBot
from w3f.lib.metadata import DoeMetadata


def main():
    BASENAME = pathlib.PurePath(__file__).name
    METADATA = DoeMetadata()

    # ####### Details required from the user
    DISCORD_TOKEN = hd.DISCORD['token']
    TG_TOKEN = hd.TG['doe_nft_buy_token']

    TG_CHAT_IDS = {ChatType[k]: v for k, v in hd.TG["DoeBuyBot"].items()}
    DSCRD_CHANS = DiscordChannels(buys_id=hd.DISCORD[METADATA.OS_SLUG].get("buys", 0),
                                  listings_id=hd.DISCORD[METADATA.OS_SLUG].get("listings", 0),
                                  other_id=hd.DISCORD[METADATA.OS_SLUG].get("other", 0),
                                  debug_id=hd.DISCORD[METADATA.OS_SLUG].get("debug", 0))
    OS_TOKEN = hd.OS_KEY
    # ####### Details required from the user

    ORACLE = EthOracle()

    whoami.log_whoami(BASENAME)
    OsNftBuyBot(BASENAME, DSCRD_CHANS, ORACLE, DISCORD_TOKEN, METADATA, OS_TOKEN, TgBot(TG_TOKEN, TG_CHAT_IDS)).run()


if __name__ == "__main__":
    main()
