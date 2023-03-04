#!/usr/bin/env python3

import sys, os, json
import w3f.lib.logger as log
import w3f.hidden_details as hd

from w3f.lib.contracts.staking import kdoe_rewards

from web3 import Web3

# def get_wealth(w3, w3_arb, wallet):
#     nft_cnt = get_nft_cnt(w3, wallet)
#     arb_doe = get_arbitrum_worth(w3_arb, wallet)
#     wallet_doe = float(doe_token_contract.get_main_balance(w3, wallet))
#     return [wallet_doe, arb_doe, nft_cnt]

def main():
    log.log_version()
    w3 = Web3(Web3.HTTPProvider(hd.eth_mainnet))

    hodlers = kdoe_rewards.dump_all_stakers(hd.etherscan_key)
    print(len(hodlers))
    block = w3.eth.block_number
    print(block)

    hodlers_wealth = kdoe_rewards.get_sorted_balances(w3, hodlers, block)
    kdoe_rewards.dump_hodlers_json(f"src/w3f/dat/kdoe_stakers_{block}.json", hodlers_wealth)

    # print(f"Connected to Web3: {w3.isConnected()}")
    # print(f"Connected to Web3: {w3_arb.isConnected()}")
    # cnt = 0
    # with open('src/w3f/dat/holders_staking_single_line_20221203.json', 'r') as f:
    #     data = json.load(f)
    #     for hodler in data:
    #         other_wealth = get_wealth(w3, w3_arb, hodler)
    #         print(f'{data[hodler]}, {other_wealth}')
    #         cnt = cnt + 1
    #         if cnt > 40:
    #             break

    # print(os.getcwd())
    # get_wealth(w3, w3_arb, hidden_details.user_wallet)

# def get_nft_cnt(w3, wallet):
#     staked_nfts = doe_nft_staking_contract.get_tokens_of(w3, wallet)
#     wallet_nfts = nft_contract.get_inventory(w3, wallet)
#     return len(staked_nfts) + len(wallet_nfts)

if __name__ == "__main__":
    main()



