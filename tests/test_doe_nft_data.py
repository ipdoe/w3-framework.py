import pytest

from w3f.lib import doe_nft_data as doe_nft_data

def test__Metadata__get_rarity():
    metad = doe_nft_data.Metadata()
    assert metad.get_rarity(2156) == 315
    assert metad.get_rarity(9969) == 60

def test__Metadata__get_type():
    metad = doe_nft_data.Metadata()
    assert metad.get_type(2156) == "doge"
    assert metad.get_type(9969) == "alien"
    assert metad.get_type(2999) == "elon"

def test__Metadata__get_twin():
    metad = doe_nft_data.Metadata()
    assert metad.get_twin(2156) == 0
    assert metad.get_twin(9969) == 0
    assert metad.get_twin(2999) == 0
    assert metad.get_twin(1342) != 0

def test__get_collection_stats__ok():
    assert doe_nft_data.get_collection_stats()

def test__get_last_sale_price__ok():
    assert doe_nft_data.get_last_sale_price(2156)
