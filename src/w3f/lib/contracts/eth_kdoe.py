from  w3f.lib.contracts import eth_kdoe_abi
from w3f.lib import swap

address = "0x9d9681d71142049594020bD863D34D9F48d9DF58"
name = "eth-kdoe"
tokens = [swap.SwapToken('kdoe', 'ether', decimals=2), 
          swap.SwapToken('eth', 'ether', decimals=4)]
abi = eth_kdoe_abi.get_abi()
swap = swap.Swap(abi, name, address, tokens)
