import json, pathlib
from w3f.lib.contracts import kdoe_eth
from w3f.lib.web3 import W3, GetBlockBsc, InfuraEth
import w3f.hidden_details as hd

from . import TEST_DATA

# W3_ETH = InfuraEth(hd.infura_key)
W3_BSC = GetBlockBsc(hd.GETBLOCK_KEY)

# ETH_CONTRACT = kdoe_eth.Contract(W3_ETH)
BSC_CONTRACT = kdoe_eth.BscContract(W3_BSC)


def test__Swap__Sell():
    print(pathlib.Path.cwd())
    with open(TEST_DATA / "bnb-eth_tx.json", "r") as f:
        swap_log_obj = BSC_CONTRACT.decode_swap_event(json.load(f))
        assert not swap_log_obj.swap_tokens.buy
        assert swap_log_obj.swap_tokens.in_token == swap_log_obj.swap_tokens.buy_token
        assert swap_log_obj.swap_tokens.out_token == swap_log_obj.swap_tokens.sell_token
        assert swap_log_obj.swap_tokens.in_token.ammount == 37334.37833057468
        assert swap_log_obj.swap_tokens.out_token.ammount == 1.241691191404858
        assert swap_log_obj.tx_addr == "0xba0Bdc59060e9840a9A3555805b668F85AdD9008"
        assert swap_log_obj.tx_hash == "0xf1e338e023d2c1e9df45bb0cbda25a02a9308a5870efbb00b1d64c94d55f8126"
        assert "🔴🔴" in swap_log_obj.buy_sell_msg(200)
        assert "($248.34)" in swap_log_obj.buy_sell_msg(200)
