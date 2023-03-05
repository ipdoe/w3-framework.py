from web3 import Web3
from w3f.lib.contracts import kdoe_token_abi

ETH_ADDRESS = "0x5f190F9082878cA141F858c1c90B4C59fe2782C5"

def get_main_balance(w3, wallet):
    return _get_balance(w3, ETH_ADDRESS, wallet)

def _get_balance(w3, addr, wallet):
    contract = w3.eth.contract(address=addr, abi=kdoe_token_abi.get_abi())
    balanceOf = contract.functions.balanceOf(wallet).call()
    return Web3.fromWei(balanceOf, 'ether')