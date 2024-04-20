import w3f.lib.contracts.eth_usdt_abi as eth_usdt_abi
from w3f.lib import swap
from w3f.lib.web3 import SwapContract, W3

ADDRESS = '0x0d4a11d5EEaaC28EC3F61d100daF4d40471f1852'
NAME = 'eth-usdt'
TOKENS = [swap.SwapToken('eth', 'ether', decimals=4),
          swap.SwapToken('usdt', 'mwei', decimals=2)]
ABI = eth_usdt_abi.get_abi()


class Contract(SwapContract):
    def __init__(self, w3: W3) -> None:
        super().__init__(NAME, w3, ADDRESS, ABI,  TOKENS[0],  TOKENS[1], 0)
