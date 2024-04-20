import w3f.lib.web3
from w3f.lib.contracts import _get_abi
from w3f.lib.web3 import W3
from w3f.lib.fungible_token import FungibleToken

_ABI = _get_abi("uni_v2")
ADDRESS = "0xBb2b8038a1640196FbE3e38816F3e67Cba72D940"
NAME = "wbtc-weth_uni-v2"
TOKENS = [FungibleToken('wbtc', 'ether', decimals=6),
          FungibleToken('weth', 'ether', decimals=4)]
# SWAP = swap.Swap(_ABI, NAME, ADDRESS, TOKENS, 1)


class Contract(w3f.lib.web3.SwapContract):
    def __init__(self, w3: W3) -> None:
        super().__init__(NAME, w3, ADDRESS, _ABI,  TOKENS[0],  TOKENS[1], 0)
