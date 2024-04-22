import asyncio
import copy
import websockets
from hexbytes import HexBytes
from typing import NamedTuple, List, Union

from web3 import Web3
from web3.types import ABIEvent, FilterParams
from web3._utils.filters import Filter
from web3._utils.events import construct_event_topic_set
from web3.datastructures import AttributeDict

from w3f.lib import network
from w3f.lib import json


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

    def _get_event_signature(self, event: ABIEvent):
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

    def create_filter(self, event_name, params: FilterParams) -> Filter:
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


class InfuraEth(W3):
    def __init__(self, api_key: str) -> None:
        super().__init__(network.PROVIDER["infura-eth"], api_key)


class InfuraArb(W3):
    def __init__(self, key: str) -> None:
        super().__init__(network.PROVIDER["infura-arb"], key)


class AlchemyBase(W3):
    def __init__(self, api_key: str) -> None:
        super().__init__(network.PROVIDER["alchemy-base"], api_key)


# class AnkrBsc(W3):
#     def __init__(self) -> None:
#         super().__init__("https://rpc.ankr.com/bsc", network.ChainId.BSC)


class GetBlockBsc(W3):
    def __init__(self, key: str) -> None:
        super().__init__(network.PROVIDER["getblock-bsc"], key)
