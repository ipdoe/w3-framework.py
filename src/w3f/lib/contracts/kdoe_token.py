from web3 import Web3
from w3f.lib.contracts import kdoe_token_abi

ETH_ADDRESS = "0x5f190F9082878cA141F858c1c90B4C59fe2782C5"
BSC_ADDRESS = "0xB9eEE0069bb54C2aA5762D184455686ec58A431F"

def get_main_balance(w3, wallet):
    return _get_balance(w3, ETH_ADDRESS, wallet)

def get_bsc_balance(w3, wallet):
    return _get_balance(w3, BSC_ADDRESS, wallet)

def _get_balance(w3, addr, wallet):
    contract = w3.eth.contract(address=addr, abi=kdoe_token_abi.get_abi())
    balanceOf = contract.functions.balanceOf(wallet).call()
    return Web3.fromWei(balanceOf, 'ether')