import json
from w3f.lib import eth_event_socket as ees
from w3f.lib import logger as log
from w3f.lib.contracts import kdoe_eth

from . import TEST_DATA

def test__Swap__Sell():
    with (TEST_DATA / "swap_log_event_sell.json").open() as f:
        swap = ees.SwapData(json.load(f)['params']['result'])

        assert not kdoe_eth.ETH_SWAP.is_buy(swap)
        assert '🔴🔴' in kdoe_eth.ETH_SWAP.buy_sell_msg(swap, 10)

def test__Swap__Buy():
    with (TEST_DATA / "swap_log_event_buy.json").open() as f:
        swap = ees.SwapData(json.load(f)['params']['result'])

        assert kdoe_eth.ETH_SWAP.is_buy(swap)
        assert '🧩🧩' in kdoe_eth.ETH_SWAP.buy_sell_msg(swap, 10)
