import w3f.lib.contracts.eth_usdt_abi as eth_usdt_abi
import w3f.lib.swap as SWAP

address = '0x0d4a11d5EEaaC28EC3F61d100daF4d40471f1852'
name = 'eth-usdt'
tokens = [SWAP.SwapToken('eth', 'ether', decimals=4),
          SWAP.SwapToken('usdt', 'mwei', decimals=2)]
abi = eth_usdt_abi.get_abi()
SWAP = SWAP.Swap(abi, name, address, tokens)
