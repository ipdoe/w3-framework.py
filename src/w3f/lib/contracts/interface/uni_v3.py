import pathlib
from w3f.lib.contracts import _get_abi
from w3f.lib.contracts.interface.erc20 import Erc20
from w3f.lib.web3 import W3, Contract

NAME = pathlib.PurePath(__file__).stem
ABI = _get_abi(NAME)


class UniV3(Contract):
    def __init__(self, w3: W3, address: str) -> None:
        super().__init__(NAME, w3, address, ABI)
        token0 = self.contract.functions.token0().call()
        token1 = self.contract.functions.token1().call()
        self._tokens = (Erc20(w3, token0), Erc20(w3, token1))
        self.name = f"{self.name}-{self._tokens[0].name}-{self._tokens[1].name}"
