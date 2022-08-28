import w3f.lib.contracts.usdc_doe_abi as usdc_doe_abi
import w3f.lib.swap as swap

address = "0xa626EB9cC7Dec00703586414d0811E1ba2021443"
name = 'usdc-doe'
tokens = [swap.SwapToken('usdc', 'mwei', decimals=2), 
          swap.SwapToken('doe', 'ether', decimals=2)]
abi = usdc_doe_abi.get_abi()
swap = swap.Swap(abi, name, address, tokens)