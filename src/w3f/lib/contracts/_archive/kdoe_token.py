from web3 import Web3
from w3f.lib.contracts import kdoe_token_abi
from w3f.lib.web3 import Contract, W3

ETH_ADDRESS = "0x5f190F9082878cA141F858c1c90B4C59fe2782C5"
BSC_ADDRESS = "0xB9eEE0069bb54C2aA5762D184455686ec58A431F"
ETH_ABI = kdoe_token_abi.get_abi()
NAME = "kdoe"
BSC_NAME = "bsc-kdoe"


class EthContract(Contract):
    def __init__(self, w3: W3) -> None:
        super().__init__(NAME, w3, ETH_ADDRESS, ETH_ABI)

    def balance_of(self, wallet):
        balanceOf = self.contract.functions.balanceOf(wallet).call()
        return Web3.from_wei(balanceOf, 'ether')


class BscContract(Contract):
    def __init__(self, w3: W3) -> None:
        super().__init__(BSC_NAME, w3, BSC_ADDRESS, ETH_ABI)

    def balance_of(self, wallet):
        balanceOf = self.contract.functions.balanceOf(wallet).call()
        return Web3.from_wei(balanceOf, 'ether')