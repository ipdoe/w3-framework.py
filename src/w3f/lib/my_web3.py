
from web3 import Web3

class W3:
    def __init__(self, w3: Web3) -> None:
        self.w3 = w3
        current = self.w3.eth.get_block('latest')
        past = self.w3.eth.get_block(self.w3.eth.block_number - 500)
        self.avg_block_time = float((current.timestamp - past.timestamp) / 500.0)

    def get_latest_block_timestamp(self):
        return self.w3.eth.get_block('latest').timestamp

    def get_block_by_timestamp(self, timestamp) -> int:
        latest_block_timestamp = self.get_latest_block_timestamp()
        average_time = latest_block_timestamp - timestamp
        if average_time < 0: raise ValueError('timestamp given by you exceed current block timestamp!')
        average_block = average_time / self.avg_block_time

        return int(self.w3.eth.block_number - average_block)