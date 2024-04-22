#!/usr/bin/env python3

import asyncio
import websockets

import w3f.lib.logger as log
from w3f.lib import whoami
from w3f.lib.crypto_oracle import EthOracle
from w3f.lib.contracts.base.weth_usdc_uni_v3 import Contract
from w3f.lib.web3 import AlchemyBase

# ####### Details required from the user
import w3f.hidden_details as hd
PROVIDER_KEY = hd.API_KEYS["alchemy-base"]
# ####### Details required from the user


async def ws_event_loop(contract: Contract, oracle: EthOracle):
    log.log(f"asyncio.create_task(ws_event_loop({contract.name}))")
    async for ws in contract.ws_connect():
        try:
            subscription = await contract.subscribe_event(ws, "Swap")
            log.log(f"Socket subscription {contract.name}: {subscription}")
            while True:
                trade_msg = await contract.wait_trade_msg_v3(ws, 1)
                print(trade_msg)

        except websockets.ConnectionClosed as cc:
            log.log(f"[token] ConnectionClosed: {cc}")
        except Exception as e:
            log.log(f"[token] Exception: {e}")


async def run():
    oracle = EthOracle()
    oracle.create_task()
    w3 = AlchemyBase(PROVIDER_KEY)
    contract = Contract(w3=w3)
    task = asyncio.create_task(ws_event_loop(contract, oracle))
    await task


def main():
    whoami.log_whoami()
    asyncio.run(run())


if __name__ == "__main__":
    main()
