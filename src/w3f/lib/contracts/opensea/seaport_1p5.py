from enum import Enum

from web3 import Web3
import w3f.lib.contracts.opensea.seaport_1p5_abi as abi
import w3f.lib.web3 as web3


ADDRESS = '0x00000000000000ADc04C56Bf30aC9d3c0aAF14dC'

class Seaport(web3.Contract):
    def __init__(self, w3: Web3) -> None:
        super().__init__(w3, ADDRESS, abi.get_abi())
