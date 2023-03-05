import pytest

from w3f.lib import doe_nft_data

COLLECTION_STATS = doe_nft_data.get_collection_stats()
METADATA = doe_nft_data.Metadata()

def test__Metadata__get_rarity():
    assert METADATA.get_rarity(2156) == 315
    assert METADATA.get_rarity(9969) == 60

def test__Metadata__get_type():
    assert METADATA.get_type(2156) == "doge"
    assert METADATA.get_type(9969) == "alien"
    assert METADATA.get_type(2999) == "elon"

def test__Metadata__get_twin():
    assert METADATA.get_twin(2156) == 0
    assert METADATA.get_twin(9969) == 0
    assert METADATA.get_twin(2999) == 0
    assert METADATA.get_twin(1342) != 0

def test__get_estimated_price__ok():
    assert doe_nft_data.get_estimated_price(2156, doe_nft_data.Metadata(), COLLECTION_STATS, 0.5)

def test__get_last_sale_prices__ok():
    assert doe_nft_data.get_last_sale_prices([2156])

def test__get_collection_stats__ok():
    assert COLLECTION_STATS.floor_price

def test__get_rarity_bonus__ok():
    assert doe_nft_data.get_rarity_bonus(1)
    assert doe_nft_data.get_rarity_bonus(100)
    assert doe_nft_data.get_rarity_bonus(1000)
    assert doe_nft_data.get_rarity_bonus(9999)

def test__get_type_floor__ok():
    assert doe_nft_data.get_type_floor(0.5, "none") == 0.5
    assert doe_nft_data.get_type_floor(0.5, "elon") != 0.5
    assert doe_nft_data.get_type_floor(0.5, "traitless") != 0.5
    assert doe_nft_data.get_type_floor(0.5, "alien") != 0.5
    assert doe_nft_data.get_type_floor(0.5, "zombie") != 0.5