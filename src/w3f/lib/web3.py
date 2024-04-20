import asyncio
import copy
import json
import websockets
from hexbytes import HexBytes
from typing import Union
from enum import Enum

from web3 import Web3
from web3._utils.filters import Filter
from web3._utils.events import construct_event_topic_set
from web3._utils.encoding import Web3JsonEncoder
from web3.datastructures import AttributeDict
import web3.contract
import web3.types
from web3.types import TxData
from eth_typing import HexStr
from typing import NamedTuple, List
from ens import ENS

from w3f.lib import network
from w3f.lib.logger import log
from w3f.lib import json
from w3f.lib.swap import SwapToken
from w3f.lib.util import print_json, web3_pretty_json
from w3f.lib.web3_events import UniV2Swap
from w3f.lib.fungible_token import FungibleToken


class W3:
    def __init__(self, provider: network.NodeProvider, key) -> None:
        self.w3 = Web3(Web3.HTTPProvider(provider.http(key)))
        self.ws = provider.ws(key)
        self._avg_block_time: float = 0
        self.chainId = provider.chain()

    def get_avg_block_time(self):
        if self._avg_block_time is None:
            current = self.w3.eth.get_block("latest")
            past = self.w3.eth.get_block(self.w3.eth.block_number - 500)
            self._avg_block_time = float((current.timestamp - past.timestamp) / 500.0)  # type: ignore

    def get_latest_block_timestamp(self):
        return self.w3.eth.get_block("latest").timestamp

    def get_block_by_timestamp(self, timestamp) -> int:
        latest_block_timestamp = self.get_latest_block_timestamp()
        average_time = latest_block_timestamp - timestamp
        if average_time < 0:
            raise ValueError("timestamp given by you exceed current block timestamp!")
        average_block = average_time / self.get_avg_block_time()

        return int(self.w3.eth.block_number - average_block)

    def ws_connect(self, ping_timeout: float):
        return websockets.connect(self.ws, ping_timeout=ping_timeout)

    async def wait_event(self, ws):
        try:
            json_response = json.loads(await ws.recv())
        except asyncio.TimeoutError:
            return None
        return json_response["params"]["result"]


class Contract:
    AllNftTransfers = NamedTuple(
        "AllNftTransfers",
        [("received", List[AttributeDict]), ("sent", List[AttributeDict])],
    )

    def __init__(self, name: str, w3: W3, address, abi) -> None:
        self.name = name
        self.address = address
        self.w3 = w3
        self.contract = w3.w3.eth.contract(address=address, abi=abi)
        self.explorer = network.EXPLORER[w3.chainId]

    def addr_link(self, addr):
        return self.explorer.address(addr)

    def tx_link(self, tx):
        return self.explorer.tx(tx)

    def get_events_list(self):
        return self.contract.events._events

    def get_event_signature(self, name: str):
        for event in self.contract.events._events:
            if event["name"] == name:
                return self._get_event_signature(event)
        return None

    def _get_event_signature(self, event: web3.types.ABIEvent):
        return construct_event_topic_set(event, self.w3.w3.codec)[0]

    def get_abi_event_by_signature(self, hash: str):
        for event in self.contract.events._events:
            if self._get_event_signature(event) == hash:
                return self.contract.events[event["name"]]
        return None

    def format_log(self, log_data):
        log_data["topics"] = [
            HexBytes(v) for v in log_data["topics"] if isinstance(v, str)
        ]
        if isinstance(log_data["data"], str):
            log_data["data"] = HexBytes(log_data["data"])
        return log_data

    def decode_event(self, log_data) -> dict:
        log_data = copy.deepcopy(log_data)
        event_name = self.get_abi_event_by_signature(log_data["topics"][0]).event_name
        return self.contract.events[event_name]().process_log(self.format_log(log_data))

    def create_filter(self, event_name, params: web3.types.FilterParams) -> Filter:
        return self.contract.events[event_name].create_filter(**params)

    def get_all_swaps(
        self, fromBlock=0, toBlock: Union[str, int] = "latest"
    ) -> List[AttributeDict]:
        if toBlock == "latest":
            toBlock = self.w3.w3.eth.block_number

        return self.contract.events.Swap.create_filter(
            fromBlock=fromBlock, toBlock=toBlock
        ).get_all_entries()

    def get_all_transfers(
        self, address, fromBlock=0, toBlock="latest"
    ) -> AllNftTransfers:
        if toBlock == "latest":
            toBlock = self.w3.w3.eth.block_number

        # example raw log filter.
        # self.w3.eth.filter({
        #     "fromBlock": 0,
        #     "toBlock": 'latest',
        #     "address": "0xb4a7d131436ed8EC06aD696FA3BF8d23C0aB3Acf", # Mong contract
        #     "topics": [
        #         "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef", # Transfer Event hash
        #         "0x0000000000000000000000005da93cf2d5595dd68daed256dfbff62c7ebbb298"  # from address
        # ]}).get_all_entries()

        received = self.contract.events.Transfer.create_filter(
            fromBlock=fromBlock, toBlock=toBlock, argument_filters={"to": f"{address}"}
        ).get_all_entries()

        sent = self.contract.events.Transfer.create_filter(
            fromBlock=fromBlock,
            toBlock=toBlock,
            argument_filters={"from": f"{address}"},
        ).get_all_entries()

        return Contract.AllNftTransfers(received, sent)

    def wallet_inventory(self, wallet):
        raise NotImplementedError

    def get_nfts_from_transfer_logs(self, address, fromBlock=0, toBlock="latest"):
        if toBlock == "latest":
            toBlock = self.w3.w3.eth.block_number

        all_transfers = self.get_all_transfers(address=address, fromBlock=fromBlock, toBlock=toBlock)  # type: ignore

        nft_count = {}
        for transfer in all_transfers.received:
            nft_count.setdefault(transfer["args"]["tokenId"], 0)
            nft_count[transfer["args"]["tokenId"]] = (
                nft_count[transfer["args"]["tokenId"]] + 1
            )

        for transfer in all_transfers.sent:
            nft_count.setdefault(transfer["args"]["tokenId"], 0)
            nft_count[transfer["args"]["tokenId"]] = (
                nft_count[transfer["args"]["tokenId"]] - 1
            )

        return [id for id in nft_count if nft_count[id] > 0]

    def get_nfts(self, address, fromBlock=0, toBlock="latest") -> List[int]:
        try:
            return self.wallet_inventory(address)
        except Exception:
            return self.get_nfts_from_transfer_logs(address=address, fromBlock=fromBlock, toBlock=toBlock)  # type: ignore

    # TODO: Revise ping_timeout
    def ws_connect(self, ping_timeout=41.0):
        return self.w3.ws_connect(ping_timeout=ping_timeout)

    async def subscribe_event(self, ws, event: str, id=1):
        await ws.send(json.dumps({
                "id": id,
                "method": "eth_subscribe",
                "params": [
                    "logs",
                    {
                        "address": [self.address],
                        "topics": [self.get_event_signature(event)],
                    },
                ],
            })
        )

        return await ws.recv()

    # decode event data
    # contract.events.OrderFulfilled().process_log(logs[0])

    async def wait_event(self, ws):
        event = await self.w3.wait_event(ws)
        return self.decode_event(event)


class SwapObj:
    def __init__(
        self,
        explorer: network.Explorer,
        swap: UniV2Swap,
        in_token: FungibleToken,
        out_token: FungibleToken,
        tx: TxData,
        is_buy: bool,
    ) -> None:
        self._explorer = explorer
        self._swap = swap
        self._buy_token, self._sell_token = in_token, out_token
        if is_buy:
            self._buy_token, self._sell_token = out_token, in_token
        self._in_token = in_token
        self._out_token = out_token
        self._tx = tx
        self._tx_addr = tx["from"]  # type: ignore
        self._is_buy = is_buy

    @staticmethod
    def _green_red(char, usd_val, divisor):
        return char * max(1, min(int(usd_val) // divisor, 1000))

    def _addr_msg(self):
        return f"Addr: [{self._tx_addr[:8]}]({self._explorer.address(self._tx_addr)})"

    def _tx_msg(self):
        return f"Tx: [{self._swap.tx_hash[:8]}]({self._explorer.tx(self._swap.tx_hash)})"

    def _addr_tx_msg(self):
        return f"{self._addr_msg()}, {self._tx_msg()}"

    def trade_msg(
        self, oracle_usd_price, buy_char: str, divisor: int, sell_char: str
    ):
        swap_char = buy_char if self._is_buy else sell_char
        swap_usd_val = self._sell_token.ammount * oracle_usd_price
        token_price_usd = swap_usd_val / self._buy_token.ammount

        usd_msg = f" (${swap_usd_val:,.2f})" if swap_usd_val > 0.0 else ""
        price_msg = f"Price: ${token_price_usd:f}" if token_price_usd > 0.0 else ""

        return (
            f"{self._green_red(swap_char, swap_usd_val, divisor)}\n"
            f"In: {self._in_token}{usd_msg}\n"
            f"Out: {self._out_token}\n"
            f"{price_msg}\n"
            f"{self._addr_tx_msg()}"
        )


class SwapContract(Contract):
    def __init__(
        self,
        name: str,
        w3: W3,
        address,
        abi,
        tokens: List[FungibleToken],
        buy_idx: int,
    ) -> None:
        super().__init__(name, w3, address, abi)
        self.tokens = tokens
        self.buy_idx = buy_idx

    def process_logs(self, fromBlock=0, toBlock: Union[str, int] = "latest"):
        return self.process_swaps(self.get_all_swaps(fromBlock, toBlock))

    def process_swaps(self, swap_logs: list):
        processed: List[UniV2Swap] = []
        for swap_log in swap_logs:
            print_json(swap_log)
            processed.append(UniV2Swap(swap_log))
        return processed

    def decode_swap_event(self, swap_event):
        return UniV2Swap(self.decode_event(swap_event))

    def _swap_obj(self, swap_event_or_log: UniV2Swap):
        if not isinstance(swap_event_or_log, UniV2Swap):
            swap_event_or_log = self.decode_swap_event(swap_event_or_log)

        in_token = self.tokens[swap_event_or_log.in_idx()].set_ammount(swap_event_or_log.amountIn)
        out_token = self.tokens[swap_event_or_log.out_idx()].set_ammount(swap_event_or_log.amountOut)
        tx = self.w3.w3.eth.get_transaction(HexStr(swap_event_or_log.tx_hash))
        is_buy = swap_event_or_log._out_idx == self.buy_idx
        return SwapObj(
            self.explorer, swap_event_or_log, in_token, out_token, tx, is_buy
        )

    def trade_msg(self, swap_log, oracle_usd_price, buy_char="🟢", divisor=100, sell_char="🔴"):
        return self._swap_obj(swap_log).trade_msg(oracle_usd_price, buy_char, divisor, sell_char)

    async def wait_swap(self, ws):
        swap = UniV2Swap(await self.wait_event(ws))
        return self._swap_obj(swap)

    async def wait_trade_msg(
        self, ws, oracle_usd_price, buy_char="🟢", divisor=100, sell_char="🔴"
    ):
        swapObj = await self.wait_swap(ws)
        return swapObj.trade_msg(oracle_usd_price, buy_char, divisor, sell_char)


class InfuraEth(W3):
    def __init__(self, api_key: str) -> None:
        super().__init__(network.PROVIDER["infura-eth"], api_key)


class InfuraArb(W3):
    def __init__(self, key: str) -> None:
        super().__init__(network.PROVIDER["infura-arb"], key)


# class AnkrBsc(W3):
#     def __init__(self) -> None:
#         super().__init__("https://rpc.ankr.com/bsc", network.ChainId.BSC)


class GetBlockBsc(W3):
    def __init__(self, key: str) -> None:
        super().__init__(network.PROVIDER["getblock-bsc"], key)
