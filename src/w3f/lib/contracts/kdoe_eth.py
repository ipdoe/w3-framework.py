from w3f.lib.contracts import kdoe_eth_abi
from w3f.lib.contracts import kdoe_bnb_abi
from w3f.lib.eth_event_socket import Chain
from w3f.lib import swap
from collections import namedtuple
from web3 import Web3
from w3f.lib.web3 import SwapContract, W3

NAME = "kdoe-eth"
ADDRESS = "0xdd8F50f1059c50D7D75fE2f5D7d262964fB2Ae98"

BSC_NAME = "kdoe_bsc-bnb"

KDOE_ETH_T = [swap.SwapToken('kdoe', 'ether', decimals=2),
              swap.SwapToken('eth', 'ether', decimals=4)]
KDOE_BNB_T = [swap.SwapToken('kdoe', 'ether', decimals=2),
              swap.SwapToken('bnb', 'ether', decimals=4)]
ABI = kdoe_eth_abi.get_abi()
BSC_ABI = kdoe_bnb_abi.get_abi()
BNB_SWAP = swap.Swap(BSC_ABI, "bnb-kdoe_bsc", kdoe_bnb_abi.ADDRESS, KDOE_BNB_T,
                     0, Chain.BSC, '🟡')
ETH_SWAP = swap.Swap(ABI, "eth-kdoe", ADDRESS, KDOE_ETH_T,
                     0, Chain.ETH, '🧩')


EthReserves = namedtuple("Reserves", ["kdoe", "eth", "block"])
BnbReserves = namedtuple("Reserves", ["kdoe", "bnb", "block"])


def get_reserves(contract):
    reserves = contract.functions.getReserves().call()
    Web3.from_wei(reserves[0], "ether")
    if contract.address == kdoe_bnb_abi.ADDRESS:
        return BnbReserves(Web3.from_wei(reserves[0], "ether"), Web3.from_wei(reserves[1], "ether"), reserves[2])
    return EthReserves(Web3.from_wei(reserves[0], "ether"), Web3.from_wei(reserves[1], "ether"), reserves[2])


def get_kdoe_price(contract):
    reserves = get_reserves(contract)
    return reserves[1] / reserves.kdoe


class Contract(SwapContract):
    def __init__(self, w3: W3) -> None:
        super().__init__(NAME, w3, ADDRESS, ABI,  *KDOE_ETH_T, buyIdx=0)

    def get_reserves(self):
        return get_reserves(self.contract)

    def get_kdoe_price(self):
        return get_reserves(self.contract)


class BscContract(SwapContract):
    def __init__(self, w3: W3) -> None:
        super().__init__(kdoe_bnb_abi.NAME, w3, kdoe_bnb_abi.ADDRESS, BSC_ABI,  *KDOE_BNB_T, buyIdx=0)


    def get_reserves(self):
        return get_reserves(self.contract)

    def get_kdoe_price(self):
        return get_reserves(self.contract)