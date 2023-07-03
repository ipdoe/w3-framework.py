from web3 import Web3
import w3f.lib.contracts.staking.doe_doe_abi as doe_doe_abi
import requests, datetime, json

contract_address = "0x82e12e8B9DFa7c0aaed46554766Af224b1Ccda63"
STARTING_BLOCK = 13554136

def get_balance(w3, wallet, block_identifier='latest'):
    contract = w3.eth.contract(address=contract_address, abi=doe_doe_abi.get_abi())
    balanceOf =  Web3.from_wei(contract.functions.balanceOf(wallet).call(block_identifier=block_identifier), "ether")
    earned = Web3.from_wei(contract.functions.earned(wallet).call(block_identifier=block_identifier), "ether")

    return {
        "Staked": balanceOf,
        "Rewards": earned,
        }

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
    return all_doe_stake_transactions_since(api_key, STARTING_BLOCK)

def dump_all_stakers_since(api_key, start_block):
    addresses = []
    dump = all_doe_stake_transactions_since(api_key, start_block)
    for tx in dump:
        addr = Web3.to_checksum_address(tx['from'])
        if addr not in addresses:
            addresses.append(addr)

    return addresses

def dump_all_stakers(api_key):
    return dump_all_stakers_since(api_key, STARTING_BLOCK)

def get_all_balances(w3, addr_list, block_identifier='latest'):
    holders_lst = []
    hodlers = {}
    for addr in addr_list:
        balance = get_balance(w3, addr, block_identifier)
        total = float(balance['Staked'] + balance['Rewards'])
        if (total > 0.0):
            balance_summary = [addr, total, float(balance['Staked']), float(balance['Rewards'])]
            holders_lst.append(balance_summary)
    holders_lst.sort(key=lambda x: x[1], reverse=True)

    for hodler in holders_lst:
        hodlers[hodler[0]] = {"total": hodler[1], "staked": hodler[2], "rewards": hodler[3]}
    return hodlers

def get_sorted_balances(w3, addr_list, block_identifier='latest'):
    print(len(addr_list))
    holders_lst = []
    hodlers = {}
    cnt = 0
    for addr in addr_list:
        balance = get_balance(w3, addr, block_identifier)
        total = float(balance['Staked'] + balance['Rewards'])
        if (cnt % 20) == 0: print(cnt)
        if (total > 0.0):
            balance_summary = [addr, total, float(balance['Staked']), float(balance['Rewards'])]
            holders_lst.append(balance_summary)
        cnt = cnt + 1
    holders_lst.sort(key=lambda x: x[1], reverse=True)

    for hodler in holders_lst:
        hodlers[hodler[0]] = {"total": hodler[1], "staked": hodler[2], "rewards": hodler[3]}
    return hodlers

def dump_hodlers_json(path, hodlers):
    # todo: last comma in the file is not json compatible
    with open(path, 'w') as w:
        w.write("{")
        for hodler in hodlers:
            w.write(f'\"{hodler}\": {json.dumps(hodlers[hodler])},\n')
        w.write("}\n")
