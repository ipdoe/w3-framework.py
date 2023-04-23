
from web3 import Web3

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
