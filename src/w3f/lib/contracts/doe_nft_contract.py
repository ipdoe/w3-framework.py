from web3 import Web3
import w3f.lib.contracts.doe_nft_abi as abi
import w3f.lib.web3 as web3

ADDRESS = "0xD8CDB4b17a741DC7c6A57A650974CD2Eba544Ff7"

class DoeNtf(web3.Contract):
    def __init__(self, w3: Web3) -> None:
        super().__init__(w3, ADDRESS, abi.get_abi())

    def wallet_inventory(self, wallet):
        return self.contract.functions.walletInventory(wallet).call()
