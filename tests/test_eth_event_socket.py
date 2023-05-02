
import json
from w3f.lib import eth_event_socket as ees
from w3f.lib import logger as log

from . import TEST_DATA

def test__SwapData():
    with (TEST_DATA / "swap_log_event_sell.json").open() as f:
        event_data = json.load(f)['params']['result']

        swap = ees.SwapData(event_data)
        assert swap.ammounts.out_idx == 1
        assert swap.ammounts.in_a == 291000000000000000000000
        assert swap.ammounts.out_a == 2122365376906334429
        assert swap.addr == "0x555B6eE8faB3DfdBcCa9121721c435FD4C7a1fd1"
        assert "etherscan.io" in swap.addr_link
        assert swap.tx == "0x1244a4ca9876b8908ce7d8c3f150c9595e04c8bdb36342ce17e810cd5552b67f"
        assert "etherscan.io" in swap.tx_link

        swap = ees.SwapData(event_data, ees.Chain.BSC)
        assert swap.ammounts.in_a == 291000000000000000000000
        assert swap.ammounts.out_a == 2122365376906334429
        assert swap.addr == "0x555B6eE8faB3DfdBcCa9121721c435FD4C7a1fd1"
        assert "bscscan.com" in swap.addr_link
        assert swap.tx == "0x1244a4ca9876b8908ce7d8c3f150c9595e04c8bdb36342ce17e810cd5552b67f"
        assert "bscscan.com" in swap.tx_link
