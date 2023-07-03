#!/usr/bin/env python3

import w3f.lib.logger as log
from w3f.lib.contracts.staking import doe_doe_staking_contract
import w3f.hidden_details as hd
from web3 import Web3

def main():
    w3 = Web3(Web3.HTTPProvider(hd.eth_mainnet))
    print(f"Connected to Web3: {w3.is_connected()}")
    current_block = w3.eth.block_number
    stakers_list = doe_doe_staking_contract.dump_all_stakers(hd.etherscan_key)
    balances = doe_doe_staking_contract.get_sorted_balances(w3, stakers_list, block_identifier=current_block)
    # log.log_json(balances)
    doe_doe_staking_contract.dump_hodlers_json(f"holders-{current_block}.json", balances)


if __name__ == "__main__":
    main()



