import pathlib

import w3f.lib.web3
from w3f.lib.contracts import _get_abi

_BASENAME = pathlib.PurePath(__file__).name


class Contract(w3f.lib.web3.Contract):
    def __init__(self, w3: w3f.lib.web3.W3, name: str, addr: str) -> None:
        super().__init__(name, w3, addr, _get_abi(_BASENAME))
