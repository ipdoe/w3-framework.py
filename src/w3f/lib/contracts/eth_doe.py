import decimal
import w3f.lib.contracts.eth_doe_abi as eth_doe_abi
import w3f.lib.swap as swap

address = "0x9d9681d71142049594020bD863D34D9F48d9DF58"
name = "eth-doe"
tokens = [swap.SwapToken('eth', 'ether', decimals=4), 
          swap.SwapToken('doe', 'ether', decimals=2)]
abi = eth_doe_abi.get_abi()
swap = swap.Swap(abi, name, address, tokens)
