from w3f.lib.contracts import _get_abi
from w3f.lib.web3 import SwapContract, W3
from w3f.lib.fungible_token import FungibleToken

_ABI = _get_abi("uni_v2")
ADDRESS = "0xB4e16d0168e52d35CaCD2c6185b44281Ec28C9Dc"
NAME = "uni-v2_usdc-eth"
TOKENS = [FungibleToken('usdc', 'mwei', decimals=2),
          FungibleToken('eth', 'ether', decimals=4)]


class Contract(SwapContract):
    def __init__(self, w3: W3) -> None:
        super().__init__(NAME, w3, ADDRESS, _ABI,  TOKENS, 0)
