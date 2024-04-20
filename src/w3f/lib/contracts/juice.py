import pathlib

import w3f.lib.web3
from w3f.lib.contracts import _get_abi
from w3f.lib.web3 import W3

_BASENAME = pathlib.PurePath(__file__).name
ADDRESS = "0xc4c4e2Dd743CCBBC7A8e20a7073Be281b2924519"
NAME = "JUICE"


class Contract(w3f.lib.web3.Contract):
    def __init__(self, w3: W3) -> None:
        super().__init__(NAME, w3, ADDRESS, _get_abi(_BASENAME))
