from w3f.lib.contracts import kdoe_eth_abi
from w3f.lib import swap

address = "0xdd8F50f1059c50D7D75fE2f5D7d262964fB2Ae98"
name = "eth-kdoe"
tokens = [swap.SwapToken('kdoe', 'ether', decimals=2), 
          swap.SwapToken('eth', 'ether', decimals=4)]
abi = kdoe_eth_abi.get_abi()
swap = swap.Swap(abi, name, address, tokens, 0)
