import w3f.lib.logger as log

from w3f.lib.contracts.staking import kdoe_rewards
from w3f.lib.contracts import kdoe_token
from w3f.lib.contracts import doe_nft_contract, mongs_nft
from w3f.lib.contracts import kdoe_eth
from w3f.lib import doe_nft_data, mong_metadata
from w3f.lib.web3 import W3

from collections import namedtuple
from web3 import Web3


class MainnetKdoe(namedtuple("MainnetKdoe", ["mainnet", "staking"])):
    def __new__(cls, field1, field2):
        return super().__new__(cls, field1, field2)

    def total(self):
        return self.mainnet + sum(self.staking)


class Wealth():
    def __init__(self, w3: W3, w3_bsc: W3, wallet, metadata: doe_nft_data.Metadata,
                 mong_metadata: mong_metadata.MongMetadata, collection_stats: doe_nft_data.CollectionStats = None):
        self.w3 = w3
        self.w3_bsc = w3_bsc
        self.wallet = Web3.to_checksum_address(wallet)
        self.eth_contract = kdoe_token.EthContract(w3)
        self.doe_nft = doe_nft_contract.Contract(w3)
        self.mongs_nft = mongs_nft.Contract(w3)
        self.bsc_contract = kdoe_token.BscContract(w3_bsc)
        self._metadata = metadata
        self._mong_metadata = mong_metadata
        self._collection_stats = collection_stats
        mainnet = self.eth_contract.balance_of(wallet)
        staking = kdoe_rewards.get_balance(w3.w3, wallet)
        self.mainnet = MainnetKdoe(mainnet, staking)
        self.nfts = self.get_nft_holdings_stats(metadata, collection_stats)
        self.bsc = self.bsc_contract.balance_of(self.wallet)

    def total(self):
        return self.mainnet.mainnet + sum(self.mainnet.staking)

    def _nfts_to_lines(self):
        result = []
        for nft in self.nfts["nfts"]:
            result.append(f"#{nft:>4} {self.nfts['nfts'][nft].to_str()}\n")

        for mong_id in self.nfts["mong"]:
            result.append(
                f"mong: #{self._mong_metadata.get_trimmed_id(mong_id)} [{self._mong_metadata.get_rarity(mong_id): >4}]\n")

        if result:
            result[-1] = result[-1][:-1]
        return result

    def _nfts_to_str(self):
        return "".join(self._nfts_to_lines())

    def _mainnet_to_str(self):
        return f"Mainnet: {self.mainnet.total():{kdoe_fmt()}} KDOE\n" \
               f"BSC: {self.bsc:{kdoe_fmt()}} KDOE\n" \
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

    def get_doe_nfts(self):
        staking = kdoe_rewards.address_to_token(self.w3.w3, self.wallet)
        mainnet = self.doe_nft.wallet_inventory(self.wallet)
        return staking + mainnet

    def get_nft_holdings_stats(self, metadata: doe_nft_data.Metadata = None, collection_stats=None):
        nfts = self.get_doe_nfts()
        if metadata is None:
            metadata = doe_nft_data.Metadata()
        if collection_stats is None:
            collection_stats = doe_nft_data.get_collection_stats()
        sale_prices = doe_nft_data.get_last_sale_prices(nfts)
        holdings = {}
        holdings["nft_total"] = 0
        holdings["nft_cnt"] = len(nfts)
        holdings["mong"] = self.mongs_nft.get_nfts(self.wallet)
        holdings["nfts"] = {}
        for nft in nfts:
            holdings["nfts"][nft] = doe_nft_data.get_estimated_price(nft, metadata, collection_stats, sale_prices[nft]["eth_now"])
            holdings["nft_total"] = holdings["nft_total"] + holdings["nfts"][nft].estimated

        return holdings

def kdoe_fmt():
    return ",.2f"


def get_mong_nfts(w3: W3, wallet):
    mainnet = mongs_nft.Contract(w3).get_nfts(wallet)
    return mainnet

def get_kdoe_price_usd(w3, eth_price):
    return float(kdoe_eth.get_kdoe_price(w3)) * eth_price

def get_nft_holdings_stats(w3: W3, wallet, metadata: doe_nft_data.Metadata = None, collection_stats=None):
    nfts = get_doe_nfts(w3, wallet)
    if metadata is None:
        metadata = doe_nft_data.Metadata()
    if collection_stats is None:
        collection_stats = doe_nft_data.get_collection_stats()
    sale_prices = doe_nft_data.get_last_sale_prices(nfts)
    holdings = {}
    holdings["nft_total"] = 0
    holdings["nft_cnt"] = len(nfts)
    holdings["mong"] = get_mong_nfts(w3, wallet)
    holdings["nfts"] = {}
    for nft in nfts:
        holdings["nfts"][nft] = doe_nft_data.get_estimated_price(nft, metadata, collection_stats, sale_prices[nft]["eth_now"])
        holdings["nft_total"] = holdings["nft_total"] + holdings["nfts"][nft].estimated

    return holdings
