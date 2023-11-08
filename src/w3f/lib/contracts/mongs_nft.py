import json
import pathlib

from web3 import Web3

from w3f import ROOT_PATH
import w3f.lib.web3

_BASENAME = pathlib.PurePath(__file__).name
_ABI = (ROOT_PATH / "lib/contracts" / _BASENAME).with_suffix(".abi")
ADDRESS = "0xb4a7d131436ed8EC06aD696FA3BF8d23C0aB3Acf"

class Contract(w3f.lib.web3.Contract):
    def __init__(self, w3: Web3) -> None:
        with open(_ABI, 'r') as abi_json:
            super().__init__(w3, ADDRESS, json.load(abi_json))
