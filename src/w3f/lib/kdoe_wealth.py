import w3f.lib.logger as log

from w3f.lib.contracts.staking import kdoe_rewards
from w3f.lib.contracts import kdoe_token
from w3f.lib.contracts import doe_nft_contract
from w3f.lib.contracts import kdoe_eth
from w3f.lib import doe_nft_data

from collections import namedtuple
from web3 import Web3


class MainnetKdoe(namedtuple("MainnetKdoe", ["mainnet", "staking"])):
    def __new__(self, field1, field2):
        return super().__new__(self, field1, field2)

    def total(self):
        return self.mainnet + sum(self.staking)

class Wealth():
    def __init__(self, w3, wallet, metadata: doe_nft_data.Metadata = None,
                 collection_stats: doe_nft_data.CollectionStats = None):
        self.w3 = w3
        self.wallet = Web3.toChecksumAddress(wallet)
        self._metadata = metadata
        self._collection_stats = collection_stats
        self.mainnet = get_mainet_kdoe(w3, self.wallet)
        self.nfts = get_nft_holdings_stats(w3, self.wallet, metadata, collection_stats)

    def total(self):
        return self.mainnet + sum(self.staking)

    def _nfts_to_lines(self):
        result = []
        for nft in self.nfts["nfts"]:
            result.append(f"#{nft:>4} {self.nfts['nfts'][nft].to_str()}\n")

        if result:
            result[-1] = result[-1][:-1]
        return result


    def _nfts_to_str(self):
        return "".join(self._nfts_to_lines())

    def _mainnet_to_str(self):
        return f"Mainnet: {self.mainnet.total():{kdoe_fmt()}} KDOE\n" \
               f"NFT Count: {self.nfts['nft_cnt']}\n" \
               f"NFTs estimate: {self.nfts['nft_total']:,.4f} ETH\n"

    def to_str(self):
        return self._mainnet_to_str() + self._nfts_to_str()

    def to_msg_chunks(self, msg_limit: int):
        chunk_size = 0
        lines = [self._mainnet_to_str()] + self._nfts_to_lines()
        chunks = []
        current_chunk = []
        for line in lines:
            if chunk_size + len(line) > msg_limit:
                chunks.append("".join(current_chunk))
                current_chunk = []
                chunk_size = 0
            current_chunk.append(line)
            chunk_size = chunk_size + len(line)

        chunks.append("".join(current_chunk))
        return chunks

def kdoe_fmt():
    return ",.2f"

def get_mainet_kdoe(w3, wallet):
    mainnet = kdoe_token.get_main_balance(w3, wallet)
    staking = kdoe_rewards.get_balance(w3, wallet)
    return MainnetKdoe(mainnet, staking)

def get_doe_nfts(w3, wallet):
    staking = kdoe_rewards.address_to_token(w3, wallet)
    mainnet = doe_nft_contract.wallet_inventory(w3, wallet)
    return staking + mainnet

def get_kdoe_price_usd(w3, eth_price):
    return float(kdoe_eth.get_kdoe_price(w3)) * eth_price

def get_nft_holdings_stats(w3, wallet, metadata: doe_nft_data.Metadata = None, collection_stats=None):
    nfts = get_doe_nfts(w3, wallet)
    if metadata is None:
        metadata = doe_nft_data.Metadata()
    if collection_stats is None:
        collection_stats = doe_nft_data.get_collection_stats()
    sale_prices = doe_nft_data.get_last_sale_prices(nfts)
    holdings = {"nft_total": 0}
    holdings["nft_cnt"] = len(nfts)
    holdings["nfts"] = {}
    for nft in nfts:
        holdings["nfts"][nft] = doe_nft_data.get_estimated_price(nft, metadata, collection_stats, sale_prices[nft]["eth_now"])
        holdings["nft_total"] = holdings["nft_total"] + holdings["nfts"][nft].estimated

    return holdings