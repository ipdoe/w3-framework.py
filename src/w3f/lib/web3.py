
import pathlib
import json
from web3 import Web3
from web3._utils.filters import Filter
from web3._utils.events import construct_event_topic_set
from web3._utils.encoding import Web3JsonEncoder
from web3.datastructures import AttributeDict
import web3.contract
import web3.types
from eth_typing import HexStr
from hexbytes import HexBytes
from typing import NamedTuple, List

def j_dumps(dictionary, indent=2):
    class my_jenc(Web3JsonEncoder):
        def default(self, obj):
            if isinstance(obj, bytes):
                return HexStr(HexBytes(obj).hex())
            return Web3JsonEncoder.default(self, obj)
    return json.dumps(dictionary, indent=indent, cls=my_jenc)

def j_dump_file(path: pathlib.Path, dictionary, indent=2):
    with open(path, 'w') as f:
        f.write(j_dumps(dictionary, indent))

    class my_jenc(Web3JsonEncoder):
        def default(self, obj):
            if isinstance(obj, bytes):
                return HexStr(HexBytes(obj).hex())
            return Web3JsonEncoder.default(self, obj)
    return json.dumps(dictionary, indent=indent, cls=my_jenc)

class W3:
    def __init__(self, http_provider: str, ws: str = None) -> None:
        self.w3 = Web3(Web3.HTTPProvider(http_provider))
        self.ws = ws
        self._avg_block_time: float = None

    def get_avg_block_time(self):
        if self._avg_block_time is None:
            current = self.w3.eth.get_block('latest')
            past = self.w3.eth.get_block(self.w3.eth.block_number - 500)
            self._avg_block_time = float((current.timestamp - past.timestamp) / 500.0)

    def get_latest_block_timestamp(self):
        return self.w3.eth.get_block('latest').timestamp

    def get_block_by_timestamp(self, timestamp) -> int:
        latest_block_timestamp = self.get_latest_block_timestamp()
        average_time = latest_block_timestamp - timestamp
        if average_time < 0: raise ValueError('timestamp given by you exceed current block timestamp!')
        average_block = average_time / self.get_avg_block_time()

        return int(self.w3.eth.block_number - average_block)

class Contract():
    AllNftTransfers = NamedTuple("AllNftTransfers", [("received", List[AttributeDict]), ("sent", List[AttributeDict])])

    def __init__(self, w3: Web3, address, abi) -> None:
        self.w3 = w3
        self.contract = w3.eth.contract(address=address, abi=abi)

    def get_event_signature(self, name: str):
        for event in self.contract.events._events:
            if event["name"] == name:
                return self._get_event_signature(event)
        return None

    def _get_event_signature(self, event: web3.types.ABIEvent):
        return construct_event_topic_set(event, self.w3.codec)[0]

    def get_abi_event_by_signature(self, hash: str):
        for event in self.contract.events._events:
            if self._get_event_signature(event) == hash:
                return self.contract.events[event["name"]]
        return None

    def decode_event(self, name, log_data):
        return self.contract.events[name]().process_log(log_data)

    def create_filter(self, event_name, params: web3.types.FilterParams) -> Filter:
        return self.contract.events[event_name].create_filter(**params)

    def get_all_transfers(self, address, fromBlock=0, toBlock='latest') -> AllNftTransfers:
        if toBlock == 'latest':
            toBlock = self.w3.eth.block_number

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
            fromBlock=fromBlock, toBlock=toBlock, argument_filters={'to':f'{address}'}
        ).get_all_entries()

        sent = self.contract.events.Transfer.create_filter(
            fromBlock=fromBlock, toBlock=toBlock, argument_filters={'from':f'{address}'}
        ).get_all_entries()

        return Contract.AllNftTransfers(received, sent)

    def wallet_inventory(self, wallet):
        raise NotImplementedError

    def get_nfts_from_transfer_logs(self, address, fromBlock=0, toBlock='latest'):
        if toBlock == 'latest':
            toBlock = self.w3.eth.block_number

        all_transfers = self.get_all_transfers(address=address, fromBlock=fromBlock, toBlock=toBlock) # type: ignore

        nft_count = {}
        for transfer in all_transfers.received:
            nft_count.setdefault(transfer["args"]["tokenId"], 0)
            nft_count[transfer["args"]["tokenId"]] = nft_count[transfer["args"]["tokenId"]] + 1

        for transfer in all_transfers.sent:
            nft_count.setdefault(transfer["args"]["tokenId"], 0)
            nft_count[transfer["args"]["tokenId"]] = nft_count[transfer["args"]["tokenId"]] - 1

        return [id for id in nft_count if nft_count[id] > 0]

    def get_nfts(self, address, fromBlock=0, toBlock='latest') -> List[int]:
        try:
            return self.wallet_inventory(address)
        except:
            return self.get_nfts_from_transfer_logs(address=address, fromBlock=fromBlock, toBlock=toBlock) # type: ignore

    # decode event data
    # contract.events.OrderFulfilled().process_log(logs[0])

class InfuraEth(W3):
    def __init__(self, api_key: str) -> None:
        super().__init__(
            f"https://mainnet.infura.io/v3/{api_key}",
            f"wss://mainnet.infura.io/ws/v3/{api_key}")

class InfuraArb(W3):
    def __init__(self, api_key: str) -> None:
        super().__init__(
            f"https://arbitrum-mainnet.infura.io/v3/{api_key}",
            f"wss://arbitrum-mainnet.infura.io/ws/v3/{api_key}")

class AnkrBsc(W3):
    def __init__(self) -> None:
        super().__init__("https://rpc.ankr.com/bsc")

class GetBlockBsc(W3):
    def __init__(self, api_key: str) -> None:
        super().__init__(
            f"https://bsc.getblock.io/{api_key}/mainnet/",
            f"wss://bsc.getblock.io/{api_key}/mainnet/")
