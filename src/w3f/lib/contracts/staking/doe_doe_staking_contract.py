from web3 import Web3
import w3f.lib.contracts.staking.doe_doe_abi as doe_doe_abi
import requests, datetime, json

contract_address = "0x82e12e8B9DFa7c0aaed46554766Af224b1Ccda63"

def get_balance(w3, wallet):
    contract = w3.eth.contract(address=contract_address, abi=doe_doe_abi.get_abi())
    balanceOf =  Web3.fromWei(contract.functions.balanceOf(wallet).call(), "ether")
    earned = Web3.fromWei(contract.functions.earned(wallet).call(), "ether")

    return {
        "Staked": balanceOf,
        "Rewards": earned,
        }


def all_doe_stake_transactions(api_key):
    data = {
        'module': 'account',
        'action': 'txlist',
        'address': contract_address,
        'startblock':'13554136',
        'endblock':'99999999',
        'sort': 'asc',
        'apikey': api_key,
    }
    return requests.get("https://api.etherscan.io/api", data=data).json()['result']

def dump_all_stakers(api_key):
    addresses = []
    dump = all_doe_stake_transactions(api_key)
    for tx in dump:
        addr = Web3.toChecksumAddress(tx['from'])
        if addr not in addresses:
            addresses.append(addr)

    return addresses

def get_sorted_balances(w3, addr_list):
    holders_lst = []
    hodlers = {}
    for addr in addr_list:
        balance = get_balance(w3, addr)
        total = float(balance['Staked'] + balance['Rewards'])
        if (total > 0.0):
            balance_summary = [addr, total, float(balance['Staked']), float(balance['Rewards'])]
            holders_lst.append(balance_summary)
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

