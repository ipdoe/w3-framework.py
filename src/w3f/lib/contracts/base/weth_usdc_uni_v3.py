from w3f.lib.contracts.base import CHAIN  # noqa: F401
from w3f.lib.swap import UniV3SwapContract
from w3f.lib.web3 import W3

ADDRESS = "0xd0b53D9277642d899DF5C87A3966A349A798F224"
CHAIN_ID = CHAIN


class Contract(UniV3SwapContract):
    def __init__(self, w3: W3) -> None:
        if CHAIN_ID != w3.chainId:
            raise RuntimeError(f"Wrong ChainId: {CHAIN_ID} != {w3.chainId}")
        super().__init__(w3, ADDRESS, buy_idx=0)
