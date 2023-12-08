

from w3f.lib.web3 import InfuraEth
import w3f.hidden_details as hd
from w3f.lib.util import print_json

import json
from w3f import ROOT_PATH
from w3f.lib.eth_event_socket import SwapData
from w3f.lib.contracts import kdoe_eth
from web3 import Web3
from hexbytes import HexBytes
from w3f.lib.web3 import SwapContract
from web3.datastructures import AttributeDict


# from w3f.lib import eth_event_socket

# class Web3Swap:
#     def __init__(self, pair_contract: SwapContract) -> None:
#         self.pair_contract = pair_contract

#     def get_in_out(self, log_entry: AttributeDict):
#         in0_in1_out0_out1 = [log_entry['amount0In'], log_entry['amount1In'],
#                              log_entry['amount0Out'], log_entry['amount0Out']]

#         return in0_in1_out0_out1


BUY = ROOT_PATH.parent.parent / "tests/dat/swap_log_event_buy.json"
SELL = ROOT_PATH.parent.parent / "tests/dat/swap_log_event_sell.json"
w3 = InfuraEth(hd.infura_key)
print(f"Connected to Web3: {w3.w3.is_connected()}")

event = json.load(open(BUY))['params']['result']
pair_contract = kdoe_eth.Contract(w3)
ret = pair_contract.process_logs(fromBlock=17153415, toBlock=17153415)
print(ret[0].buy_sell_msg(2000.0))
