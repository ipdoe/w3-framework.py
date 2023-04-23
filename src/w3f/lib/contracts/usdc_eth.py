import w3f.lib.contracts.usdc_eth_abi as usdc_eth_abi
import w3f.lib.swap as SWAP

address = '0xB4e16d0168e52d35CaCD2c6185b44281Ec28C9Dc'
name = 'usdc-eth'
tokens = [SWAP.SwapToken('usdc', 'mwei', decimals=2),
          SWAP.SwapToken('eth', 'ether', decimals=4)]
abi = usdc_eth_abi.get_abi()
SWAP = SWAP.Swap(abi, name, address, tokens)
