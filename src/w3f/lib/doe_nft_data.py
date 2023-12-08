from web3 import Web3
import requests, json, os, pathlib
from collections import namedtuple
from typing import List
from w3f.lib.logger import to_json_str
from w3f.lib.contracts.doe_nft_contract import ADDRESS
import w3f.hidden_details as hd

_HEADERS = {'User-Agent': 'Mozilla/5.0', "X-API-KEY": hd.op_sea_key}
_DAT_PATH = pathlib.Path("src/w3f/dat")
OP_SEA_URL = "https://api.opensea.io/api/v1"


CollectionStats = namedtuple("CollectionStats", ["thirty_day_average_price", "floor_price"])
PriceStats = namedtuple("PriceStats", ["averaged_floor", "last_sale", "rarity", "estimated", "type"])

class PriceStats(namedtuple("PriceStats", ["averaged_floor", "last_sale", "rarity", "estimated", "type"])):
    def __new__(self, p1, p2, p3, p4, p5):
        return super().__new__(self,  p1, p2, p3, p4, p5)

    def to_str(self):
        type_str = "t-less" if self.type == "traitless" else self.type
        return f"[{self.rarity: >4}] {type_str: >6}: {self.estimated: 8,.4f} ETH"

class Metadata:
    def __init__(self) -> None:
        with open(_DAT_PATH / "doe_rarity.json") as rarity:
            with open(_DAT_PATH / "doe_types.json") as types:
                self.rarity = json.load(rarity)
                self.types = json.load(types)

    def get_rarity(self, id):
        return self.rarity[int(id) - 1]['rank']

    def get_type(self, id):
        if id > 9997:
            return 'none'
        if id in self.types['elons']:
            return 'elon'
        if id in self.types['aliens']:
            return 'alien'
        if id in self.types['zombies']:
            return 'zombie'
        if id in self.types['traitless']:
            return 'traitless'
        return 'doge'

    def get_twin(self, id) -> int:
        try:
            return self.types['twins_dict'][str(id)]
        except:
            return 0

def get_estimated_price(id, metadata: Metadata, stats: CollectionStats, last_sale):
    type = metadata.get_type(id)
    averaged_floor = (stats.thirty_day_average_price + stats.floor_price) / 2
    rarity = metadata.get_rarity(id)
    rarity_bonus = get_rarity_bonus(rarity)
    type_floor = get_type_floor(averaged_floor, type)

    return PriceStats(
        averaged_floor,
        last_sale,
        rarity,
        max(type_floor, averaged_floor * rarity_bonus, last_sale),
        type
    )


def get_last_sale_prices(ids: List):
    contract = ADDRESS
    max_chunk = 20

    last_sales = {}
    for i in range(0, len(ids), max_chunk):
        query_param = {
            "token_ids": ids[i:i + max_chunk],
            "asset_contract_address": contract,
        }

        data = requests.get(f"{OP_SEA_URL}/assets", headers=_HEADERS, params=query_param).json()
        for asset in data["assets"]:
            id = int(asset["token_id"])
            last_sale = {}
            try:
                last_sale['token'] = asset['last_sale']['payment_token']['symbol']
                last_sale['price'] = float(Web3.from_wei(int(asset['last_sale']['total_price']), 'ether'))
                last_sale['eth_now'] = last_sale['price'] * float(asset['last_sale']['payment_token']['eth_price'])
                last_sale['usd_now'] = last_sale['price'] * float(asset['last_sale']['payment_token']['usd_price'])
            except Exception:
                last_sale['token'] = ""
                last_sale['price'] = 0.0
                last_sale['eth_now'] = 0.0
                last_sale['usd_now'] = 0.0
            last_sales[id] = last_sale

    return last_sales

def get_collection_stats():
    url = f"{OP_SEA_URL}/collection/dogs-of-elon/stats"
    data = requests.get(url, headers=_HEADERS).json()
    return CollectionStats(data['stats']['thirty_day_average_price'], data['stats']['floor_price'])

def get_rarity_bonus(rank):
    if rank < 100:
        return 5
    if rank < 500:
        return 4
    if rank < 1000:
        return 3
    if rank < 3000:
        return 1.1
    return 1.0

def get_type_floor(floor, type):
    if type == 'zombie':
        return 1
    if type == 'alien':
        return 2
    if type == 'traitless':
        return 4
    if type == 'elon':
        return 5
    return floor
