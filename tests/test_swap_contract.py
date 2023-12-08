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
    # with open(TEST_DATA / "bnb-eth_tx.json", "r") as f:
        # swap_log_obj = BSC_CONTRACT.decode_swap_event(json.load(f))
        # print(swap_log_obj)
        # print(swap_log_obj.buy_sell_msg(2000))

test__Swap__Sell()