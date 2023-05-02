from w3f.lib.contracts import kdoe_eth_abi
from w3f.lib.contracts import kdoe_bsc_token_abi
from w3f.lib.eth_event_socket import Chain
from w3f.lib import swap
from collections import namedtuple
from web3 import Web3

ADDRESS = "0xdd8F50f1059c50D7D75fE2f5D7d262964fB2Ae98"
BSC_ADDRESS = "0x3537C4532ebf720fF130ae6A5a92dC39DE31a4D8"

ETH_KDOE_T = [swap.SwapToken('kdoe', 'ether', decimals=2),
              swap.SwapToken('eth', 'ether', decimals=4)]
BNB_KDOE_T = [swap.SwapToken('kdoe', 'ether', decimals=2),
              swap.SwapToken('bnb', 'ether', decimals=4)]
ABI = kdoe_eth_abi.get_abi()
BSC_ABI = kdoe_bsc_token_abi.get_abi()
BNB_SWAP = swap.Swap(BSC_ABI, "bnb-kdoe_bsc", BSC_ADDRESS, BNB_KDOE_T,
                     0, Chain.BSC, '🟡')
ETH_SWAP = swap.Swap(ABI, "eth-kdoe", ADDRESS, ETH_KDOE_T,
                     0, Chain.ETH, '🧩')


EthReserves = namedtuple("Reserves", ["kdoe", "eth", "block"])
BnbReserves = namedtuple("Reserves", ["kdoe", "bnb", "block"])
def get_reserves(w3, address=ADDRESS, abi=ABI):
    contract = w3.eth.contract(address=address, abi=abi)
    reserves = contract.functions.getReserves().call()
    Web3.fromWei(reserves[0], "ether")
    if address == BSC_ADDRESS:
        return BnbReserves(Web3.fromWei(reserves[0], "ether"), Web3.fromWei(reserves[1], "ether"), reserves[2])
    return EthReserves(Web3.fromWei(reserves[0], "ether"), Web3.fromWei(reserves[1], "ether"), reserves[2])

def get_kdoe_price(w3, address=ADDRESS, abi=ABI):
    reserves = get_reserves(w3, address, abi)
    return reserves[1] / reserves.kdoe
