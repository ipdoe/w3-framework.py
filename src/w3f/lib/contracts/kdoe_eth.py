from w3f.lib.contracts import kdoe_eth_abi
from w3f.lib import swap
from collections import namedtuple
from web3 import Web3

ADDRESS = "0xdd8F50f1059c50D7D75fE2f5D7d262964fB2Ae98"
name = "eth-kdoe"
tokens = [swap.SwapToken('kdoe', 'ether', decimals=2),
          swap.SwapToken('eth', 'ether', decimals=4)]
abi = kdoe_eth_abi.get_abi()
swap = swap.Swap(abi, name, ADDRESS, tokens, 0)

Reserves = namedtuple("Reserves", ["kdoe", "eth", "block"])
def get_reserves(w3):
    contract = w3.eth.contract(address=ADDRESS, abi=abi)
    reserves = contract.functions.getReserves().call()
    Web3.fromWei(reserves[0], "ether")
    return Reserves(Web3.fromWei(reserves[0], "ether"), Web3.fromWei(reserves[1], "ether"), reserves[2])

def get_kdoe_price(w3):
    reserves = get_reserves(w3)
    return reserves.eth / reserves.kdoe
