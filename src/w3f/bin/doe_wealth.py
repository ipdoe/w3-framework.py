#!/usr/bin/env python3

import sys, os, json
import w3f.lib.logger as log
import w3f.lib.contracts.staking.doe_doe_staking_contract as doe_doe_staking_contract
import w3f.lib.contracts.staking.doe_nft_staking_contract as doe_nft_staking_contract
import w3f.lib.contracts.staking.slp_doe_staking_contract as slp_doe_staking_contract
import w3f.lib.contracts.staking.slp_eth_doe_contract as slp_eth_doe_contract
import w3f.lib.contracts.nft_contract as nft_contract
import w3f.lib.contracts.doe_token_contract as doe_token_contract
import hidden_details as hidden_details

from web3 import Web3

def get_wealth(w3, w3_arb, wallet):
    nft_cnt = get_nft_cnt(w3, wallet)
    arb_doe = get_arbitrum_worth(w3_arb, wallet)
    wallet_doe = float(doe_token_contract.get_main_balance(w3, wallet))
    return [wallet_doe, arb_doe, nft_cnt]

def main():
    log.log_version()
    w3 = Web3(Web3.HTTPProvider(hidden_details.eth_mainnet))
    w3_arb = Web3(Web3.HTTPProvider(hidden_details.arbirum_mainnet))
    print(f"Connected to Web3: {w3.isConnected()}")
    print(f"Connected to Web3: {w3_arb.isConnected()}")
    cnt = 0
    with open('src/w3f/dat/holders_staking_single_line_20221203.json', 'r') as f:
        data = json.load(f)
        for hodler in data:
            other_wealth = get_wealth(w3, w3_arb, hodler)
            print(f'{data[hodler]}, {other_wealth}')
            cnt = cnt + 1
            if cnt > 40:
                break

    # print(os.getcwd())
    # get_wealth(w3, w3_arb, hidden_details.user_wallet)

def get_nft_cnt(w3, wallet):
    staked_nfts = doe_nft_staking_contract.get_tokens_of(w3, wallet)
    wallet_nfts = nft_contract.get_inventory(w3, wallet)
    return len(staked_nfts) + len(wallet_nfts)

def get_arbitrum_worth(w3_arb, wallet):
    doe_arb_wallet = doe_token_contract.get_arb_balance(w3_arb, wallet)
    balance = slp_doe_staking_contract.get_balances(w3_arb, wallet)
    slp_data = slp_eth_doe_contract.get_data(w3_arb, wallet)

    mySlpSupply = balance['Staked']  + slp_data['liquidity']
    mySupplyPer = mySlpSupply / slp_data['totalSupply']

    return float(doe_arb_wallet + balance['Rewards'] + mySupplyPer * slp_data['reserves']['DOE'])

if __name__ == "__main__":
    main()



