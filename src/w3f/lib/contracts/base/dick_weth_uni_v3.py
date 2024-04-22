from w3f.lib.contracts.base import CHAIN  # noqa: F401
from w3f.lib.swap import UniV3SwapContract
from w3f.lib.web3 import W3

ADDRESS = "0x1B69F4a3aF36bA841551Ae20b9eDf5e52827bea5"
CHAIN_ID = CHAIN


class Contract(UniV3SwapContract):
    def __init__(self, w3: W3) -> None:
        if CHAIN_ID != w3.chainId:
            raise RuntimeError(f"Wrong ChainId: {CHAIN_ID} != {w3.chainId}")
        super().__init__(w3, ADDRESS, buy_idx=0)