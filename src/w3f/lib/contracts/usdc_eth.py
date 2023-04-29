import w3f.lib.contracts.usdc_eth_abi as usdc_eth_abi
from w3f.lib import swap

address = '0xB4e16d0168e52d35CaCD2c6185b44281Ec28C9Dc'
name = 'usdc-eth'
tokens = [swap.SwapToken('usdc', 'mwei', decimals=2),
          swap.SwapToken('eth', 'ether', decimals=4)]
abi = usdc_eth_abi.get_abi()
SWAP = swap.Swap(abi, name, address, tokens)
