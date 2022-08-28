import w3f.lib.contracts.eth_usdt_abi as eth_usdt_abi
import w3f.lib.swap as swap

address = '0x0d4a11d5EEaaC28EC3F61d100daF4d40471f1852'
name = 'eth-usdt'
tokens = [swap.SwapToken('eth', 'ether', decimals=4), 
          swap.SwapToken('usdt', 'mwei', decimals=2)]
abi = eth_usdt_abi.get_abi()
swap = swap.Swap(abi, name, address, tokens)
