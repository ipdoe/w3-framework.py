from enum import Enum
from dataclasses import dataclass

from web3 import Web3
from web3.types import FilterParams
import w3f.lib.contracts.opensea.seaport_1p5_abi as abi
import w3f.lib.web3 as web3


ADDRESS = '0x00000000000000ADc04C56Bf30aC9d3c0aAF14dC'

ItemType = Enum('ItemType', ['NATIVE', 'ERC20', 'ERC721', 'ERC1155', 'ERC721_WITH_CRITERIA', 'ERC1155_WITH_CRITERIA'],
                start=0)

@dataclass
class SpentItem:
    itemType: ItemType
    token_addr: str
    dentifier: int
    amount: int

@dataclass
class ReceivedItem:
    itemType: ItemType
    token_addr: str
    dentifier: int
    amount: int
    recipient_addr: str

class OrderFulfilledEvent(dict):
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self.event_args = self["args"]
        self.seller = self.event_args["offerer"]
        self.buyer = self.event_args["recipient"]
        self.offer = self.event_args["offer"]

class Seaport(web3.Contract):
    def __init__(self, w3: Web3) -> None:
        super().__init__(w3, ADDRESS, abi.get_abi())

    def filter_order_fulfilled(self, nft_contract: str, param: FilterParams):
        # Return all items that have traded the nft_contract
        return [
            d for d in self.create_filter("OrderFulfilled", param).get_all_entries()
            if Seaport._try_find_token_contract(nft_contract, d["args"]["offer"])
        ]

    @staticmethod
    def _try_find_token_contract(contract, offer_list: list) -> bool:
        contract = Web3.to_checksum_address(contract)
        try:
            return offer_list[0]["token"] == contract
        except:
            return False

    @staticmethod
    def decode_order_fulfilled(event_args: dict):
        event_args = event_args["args"]
        seller = event_args["offerer"]
        buyer = event_args["offerer"]