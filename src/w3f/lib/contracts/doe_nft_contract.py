import pathlib
import w3f.lib.contracts.doe_nft_abi as abi
import w3f.lib.web3 as web3
from w3f.lib.web3 import W3

__BASENAME = pathlib.PurePath(__file__).name
ADDRESS = "0xD8CDB4b17a741DC7c6A57A650974CD2Eba544Ff7"
NAME = "doe_nft"


class Contract(web3.Contract):
    def __init__(self, w3: W3) -> None:
        super().__init__(NAME, w3, ADDRESS, abi.get_abi())

    def wallet_inventory(self, wallet):
        return self.contract.functions.walletInventory(wallet).call()
