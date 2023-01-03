
import json, os
from venv import create
from w3f.lib import op_events
from w3f.lib import logger as log

def test__PaymentToken():
    with open("tests/dat/item_listed.json", 'r') as f:
        payload = json.load(f)['payload']['payload']
        payment_token = op_events.PaymentToken(payload['payment_token'])
        assert payment_token.eth_price == 1.0
        assert payment_token.symbol == "ETH"
        assert payment_token.from_wei(float(payload['base_price'])) == 0.0349
        assert payment_token.to_string(float(payload['base_price'])) == f"{0.0349} ETH"

def test__ItemListed():
    with open("tests/dat/item_listed.json", 'r') as f:
        data = json.load(f)
        eth_price = 1550.55
        item_listed = op_events.ItemListed(data, eth_price)

        assert item_listed.value == 34900000000000000
        assert item_listed.value_str() == "0.0349 ETH ($54.11)"
        assert item_listed.title == "Listing"

def test__ItemReceivedOffer():
    with open("tests/dat/offer_event.json", 'r') as f:
        data = json.load(f)
        eth_price = 1550.55
        item_offer = op_events.ItemReceivedOffer(data, eth_price)

        assert item_offer.value == 265000000000000000
        assert item_offer.value_str() == "0.265 WETH ($410.90)"
        assert item_offer.title == "New Offer"

def test__ItemSold():
    with open("tests/dat/sold_event.json", 'r') as f:
        data = json.load(f)
        eth_price = 1550.55
        item_sold = op_events.ItemSold(data, eth_price)


        assert item_sold.value == 30000100000
        assert item_sold.value_str() == "300.001 GALA"
        assert item_sold.title == "Sale"

def test__create_event():
    eth_price = 1550.55
    with open("tests/dat/item_listed.json", 'r') as f:
        event = op_events.create_event(json.load(f), eth_price)
        assert type(event) is op_events.ItemListed

    with open("tests/dat/offer_event.json", 'r') as f:
        event = op_events.create_event(json.load(f), eth_price)
        assert type(event) is op_events.ItemReceivedOffer

    with open("tests/dat/sold_event.json", 'r') as f:
        event = op_events.create_event(json.load(f), eth_price)
        assert type(event) is op_events.ItemSold

def test__get_os_username():
    assert op_events.get_os_username("0x5dA93cF2d5595Dd68Daed256DFbFF62c7ebBB298")