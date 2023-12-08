
import pathlib
import json
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
from eth_typing import HexStr
from typing import NamedTuple, List
from ens import ENS

from w3f.lib.logger import log
from w3f.lib.swap import SwapToken
from w3f.lib.util import print_json, web3_pretty_json

class Chain(Enum):
    ETH = 0
    BSC = 1
    ARB = 2

EXPLORER = {
    Chain.ETH: "https://etherscan.io/{}",
    Chain.BSC: "https://bscscan.com/{}",
    Chain.ARB: "https://arbiscan.io/{}",
}

def j_dumps(dictionary, indent=2):
    # class my_jenc(Web3JsonEncoder):
    #     def default(self, obj):
    #         if isinstance(obj, bytes):
    #             return HexStr(HexBytes(obj).hex())
    #         return Web3JsonEncoder.default(self, obj)

    return json.dumps(dictionary, indent=indent, cls=Web3JsonEncoder)

def j_dump_file(path: pathlib.Path, dictionary, indent=2):
    with open(path, 'w') as f:
        f.write(j_dumps(dictionary, indent))

class W3:
    def __init__(self, http_provider: str, chain = Chain.ETH, ws = "") -> None:
        self.w3 = Web3(Web3.HTTPProvider(http_provider))
        self.ws = ws
        self._avg_block_time: float = 0
        self.chain = chain

    def get_avg_block_time(self):
        if self._avg_block_time is None:
            current = self.w3.eth.get_block('latest')
            past = self.w3.eth.get_block(self.w3.eth.block_number - 500)
            self._avg_block_time = float((current.timestamp - past.timestamp) / 500.0) # type: ignore

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

    def __init__(self, name: str, w3: W3, address, abi) -> None:
        self.name = name
        self.address = address
        self.w3 = w3
        self.contract = w3.w3.eth.contract(address=address, abi=abi)
        self.explorer = EXPLORER[self.w3.chain]

    def addr_link(self, addr):
        return self.explorer.format(f'address/{addr}')

    def tx_link(self, addr):
        return self.explorer.format(f'tx/{addr}')

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
        log_data['topics'] = [HexBytes(v) for v in log_data['topics'] if isinstance(v, str)]
        if isinstance(log_data['data'], str):
            log_data['data'] = HexBytes(log_data['data'])
        return log_data

    def decode_event(self, name, log_data):
        return self.contract.events[name]().process_log(self.format_log(log_data))

    def create_filter(self, event_name, params: web3.types.FilterParams) -> Filter:
        return self.contract.events[event_name].create_filter(**params)

    def get_all_swaps(self, fromBlock=0, toBlock: Union[str, int]='latest') -> List[AttributeDict]:
        if toBlock == 'latest':
            toBlock = self.w3.w3.eth.block_number

        return self.contract.events.Swap.create_filter(
            fromBlock=fromBlock, toBlock=toBlock).get_all_entries()

    def get_all_transfers(self, address, fromBlock=0, toBlock='latest') -> AllNftTransfers:
        if toBlock == 'latest':
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
            toBlock = self.w3.w3.eth.block_number

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

class SwapContract(Contract):
    class BuySellToken:
        @staticmethod
        def _green_red(char, usd_val, divisor):
            return char * max(1, min(int(usd_val) // divisor, 1000))

        def __init__(self, tokens: List[SwapToken], buy_idx: int, amountIn: list, amountOut: list) -> None:
            sell_idx = 1 - buy_idx

            if amountOut[buy_idx]:
                # Buy
                self.buy = True
                self.in_token = tokens[sell_idx]
                self.out_token = tokens[buy_idx]
                self.in_token.set_ammount(amountIn[sell_idx])
                self.out_token.set_ammount(amountOut[buy_idx])
                self.buy_token = self.out_token
                self.sell_token = self.in_token
            else:
                # Sell
                self.buy = False
                self.in_token = tokens[buy_idx]
                self.out_token = tokens[sell_idx]
                self.in_token.set_ammount(amountIn[buy_idx])
                self.out_token.set_ammount(amountOut[sell_idx])
                self.buy_token = self.in_token
                self.sell_token = self.out_token

        def buy_sell_msg(self, oracle_usd_price, buy_char = '🟢', divisor = 100, sell_char = '🔴'):
            swap_char = buy_char if self.buy else sell_char
            swap_usd_val = self.buy_token.ammount * oracle_usd_price
            token_price_usd = swap_usd_val / self.buy_token.ammount

            usd_msg = f" (${swap_usd_val:,.2f})" if swap_usd_val > 0.0 else ""
            price_msg = f"Price: ${token_price_usd:f}\n" if token_price_usd > 0.0 else ""

            return f"{self._green_red(swap_char, swap_usd_val, divisor)}\n" \
               f"In: {self.in_token.to_string()}{usd_msg}\n" \
               f"Out: {self.out_token.to_string()}\n" \
               f"{price_msg}"

    class SwapLogObj:
        def __init__(self, tokens: List[SwapToken], buy_idx: int, swap_log: dict, contract: Contract) -> None:
            self.sender = swap_log['args']['sender']
            self.to = swap_log['args']['to']

            amountIn = [swap_log['args']['amount0In'], swap_log['args']['amount1In']]
            amountOut = [swap_log['args']['amount0Out'], swap_log['args']['amount1Out']]

            self.swap_tokens = SwapContract.BuySellToken(tokens, buy_idx, amountIn, amountOut)
            self.tx_hash: str = swap_log['transactionHash']
            if isinstance(self.tx_hash, HexBytes):
                self.tx_hash = self.tx_hash.hex()

            try:
                tx = contract.w3.w3.eth.get_transaction(self.tx_hash)
                self.tx_addr = tx['from']
                self.tx_msg = f"addr: [{self.tx_addr[:8]}]({contract.addr_link(self.tx_addr)}),  " \
                    f"Tx: [{self.tx_hash[:8]}]({contract.tx_link(self.tx_hash)})"
            except:
                self.tx_msg = ""
                pass
            # self.tx_addr_name = ENS.from_web3(self.w3).name(self.tx_addr)
            # log(self.tx_addr_name)

        def buy_sell_msg(self, oracle_usd_price, buy_char = '🟢', divisor = 100, sell_char = '🔴'):
            return self.swap_tokens.buy_sell_msg(oracle_usd_price, buy_char, divisor, sell_char) + \
                f"{self.tx_msg}"

        def __str__(self) -> str:
            return f'{self.__dict__}'

    def __init__(self, name: str, w3: W3, address, abi, token0: SwapToken, token1: SwapToken, buyIdx: int) -> None:
        super().__init__(name, w3, address, abi)
        self.tokens = [token0, token1]
        self.buy_idx = buyIdx

    def process_logs(self,  fromBlock=0, toBlock: Union[str, int]='latest'):
        return self.process_swaps(self.get_all_swaps(fromBlock, toBlock))

    def make_swap_obj(self, swap_log):
        return SwapContract.SwapLogObj(self.tokens, self.buy_idx, swap_log, self)

    def process_swaps(self, swap_logs: list):
        processed: List[SwapContract.SwapLogObj] = []
        for swap_log in swap_logs:
            print_json(swap_log)
            processed.append(self.make_swap_obj(swap_log))
        return processed

    def decode_swap_event(self, log_data):
        return SwapContract.SwapLogObj(self.tokens, self.buy_idx, self.decode_event("Swap", log_data), self)



class InfuraEth(W3):
    def __init__(self, api_key: str) -> None:
        super().__init__(
            f"https://mainnet.infura.io/v3/{api_key}",
            Chain.ETH,
            f"wss://mainnet.infura.io/ws/v3/{api_key}")

class InfuraArb(W3):
    def __init__(self, api_key: str) -> None:
        super().__init__(
            f"https://arbitrum-mainnet.infura.io/v3/{api_key}",
            Chain.ARB,
            f"wss://arbitrum-mainnet.infura.io/ws/v3/{api_key}")

class AnkrBsc(W3):
    def __init__(self) -> None:
        super().__init__("https://rpc.ankr.com/bsc",
                         Chain.BSC)

class GetBlockBsc(W3):
    def __init__(self, api_key: str) -> None:
        super().__init__(
            f"https://bsc.getblock.io/{api_key}/mainnet/",
            Chain.BSC,
            f"wss://bsc.getblock.io/{api_key}/mainnet/")
