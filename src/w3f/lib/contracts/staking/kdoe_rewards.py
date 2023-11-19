import pathlib
from web3 import Web3
from  w3f.lib.contracts.staking import kdoe_rewards_abi
import requests, datetime, json
from collections import namedtuple

contract_address = "0xF541Ab2f4DBa2071B12DA99a9Ee83B0C4b719d95"
CREATION_BLOCK = 16395899

StakingBalance = namedtuple("StakingBalance", ["staked", "rewards"])

def get_balance(w3: Web3, wallet, block_identifier='latest'):
    contract = w3.eth.contract(address=contract_address, abi=kdoe_rewards_abi.get_abi()) # type: ignore
    balanceOf =  Web3.from_wei(contract.functions.balanceOf(wallet).call(block_identifier=block_identifier), "ether")
    earned = Web3.from_wei(contract.functions.earned(wallet).call(block_identifier=block_identifier), "ether")
    return StakingBalance(balanceOf, earned)

def address_to_token(w3: Web3, wallet, block_identifier='latest'):
    contract: Web3 = w3.eth.contract(address=contract_address, abi=kdoe_rewards_abi.get_abi()) # type: ignore
    nftList = contract.functions.addressToToken(wallet).call(block_identifier=block_identifier)
    return nftList

def all_doe_stake_transactions_since(api_key, start_block):
    data = {
        'module': 'account',
        'action': 'txlist',
        'address': contract_address,
        'startblock': str(start_block),
        'endblock':'99999999',
        'sort': 'asc',
        'apikey': api_key,
    }
    return requests.get("https://api.etherscan.io/api", data=data).json()['result']

def all_doe_stake_transactions(api_key):
    return all_doe_stake_transactions_since(api_key, CREATION_BLOCK)

def dump_all_stakers_since(api_key, start_block):
    addresses = []
    dump = all_doe_stake_transactions_since(api_key, start_block)
    for tx in dump:
        addr = Web3.to_checksum_address(tx['from'])
        if addr not in addresses:
            addresses.append(addr)

    return addresses

def dump_all_stakers(api_key):
    return dump_all_stakers_since(api_key, CREATION_BLOCK)

def get_all_balances(w3, addr_list, block_identifier='latest'):
    holders_lst = []
    hodlers = {}
    for addr in addr_list:
        balance = get_balance(w3, addr, block_identifier)
        total = sum(balance)
        if (total > 0.0):
            holders_lst.append([addr, total, float(balance.staked), float(balance.rewards)])
    holders_lst.sort(key=lambda x: x[1], reverse=True)

    for hodler in holders_lst:
        hodlers[hodler[0]] = {"total": hodler[1], "staked": hodler[2], "rewards": hodler[3]}
    return hodlers

def get_sorted_balances(w3, addr_list, block_identifier='latest'):
    print(f"Stakers count: {len(addr_list)}")
    holders_lst = []
    hodlers = {}
    cnt = 0
    for addr in addr_list:
        balance = get_balance(w3, addr, block_identifier)
        total = sum(balance)
        if (cnt % 20) == 0: print(f"Processed: {cnt}")
        if (total > 0.0):
            holders_lst.append([addr, total, float(balance.staked), float(balance.rewards)])
        cnt = cnt + 1
    holders_lst.sort(key=lambda x: x[1], reverse=True)

    for hodler in holders_lst:
        hodlers[hodler[0]] = {"total": hodler[1], "staked": hodler[2], "rewards": hodler[3]}
    return hodlers

def dump_hodlers_json(path, hodlers: dict):
    with open(path, 'w') as w:
        w.write("{")
        lowest_hodler = hodlers.popitem()
        for hodler in hodlers:
            w.write(f'\"{hodler}\": {json.dumps(hodlers[hodler])},\n')
        w.write(f'\"{lowest_hodler[0]}\": {json.dumps(lowest_hodler[1])}\n')
        w.write("}\n")

def dump_sorted_stakers_json(w3, etherscan_key, path):
    block = w3.eth.block_number
    target = pathlib.Path(path) / f"kdoe_stakers_{block}.json"
    print(f"Snapshot: {block}")
    print(f"Target file: {target}")
    hodlers = get_sorted_balances(w3, dump_all_stakers(etherscan_key), block)
    dump_hodlers_json(target, hodlers)
