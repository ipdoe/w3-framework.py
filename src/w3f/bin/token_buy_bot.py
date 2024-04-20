#!/usr/bin/env python3

import asyncio
import websockets

import w3f.lib.logger as log
from w3f.lib import whoami
from w3f.lib.crypto_oracle import EthOracle
from w3f.lib.web3 import InfuraEth, SwapContract

from w3f.lib.contracts.usdc_eth_uni_v2 import Contract

# ####### Details required from the user
import w3f.hidden_details as hd
INFURA_KEY = hd.infura_key
# ####### Details required from the user


async def ws_event_loop(contract: SwapContract, oracle: EthOracle):
    log.log(f"asyncio.create_task(ws_event_loop({contract.name}))")
    async for ws in contract.ws_connect():
        try:
            subscription = await contract.subscribe_event(ws, "Swap")
            log.log(f"Socket subscription {contract.name}: {subscription}")
            while True:
                trade_msg = await contract.wait_trade_msg(ws, oracle.get())
                print(trade_msg)

        except websockets.ConnectionClosed as cc:
            log.log(f"[token] ConnectionClosed: {cc}")
        except Exception as e:
            log.log(f"[token] Exception: {e}")


async def run():
    oracle = EthOracle()
    oracle.create_task()
    w3 = InfuraEth(hd.infura_key)
    contract = Contract(w3=w3)
    task = asyncio.create_task(ws_event_loop(contract, oracle))
    await task


def main():
    whoami.log_whoami()
    asyncio.run(run())


if __name__ == "__main__":
    main()
