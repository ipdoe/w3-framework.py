
from w3f.lib.contracts.staking import kdoe_rewards
from w3f.lib import logger as log
import w3f.hidden_details as hd

from web3 import Web3

staking_wallet = "0x7eD309643FB211e846a6D0A73Cd384e2e7A67B69"
W3 = Web3(Web3.HTTPProvider(hd.eth_mainnet))

def test__get_balance():
    balance = kdoe_rewards.get_balance(W3, staking_wallet)
    log.log(balance)
