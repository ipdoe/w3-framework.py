#!/usr/bin/env python3

import sys, os, json
import w3f.lib.logger as log
import w3f.hidden_details as hd

from w3f.lib.contracts.staking import kdoe_rewards
from w3f.lib.contracts import kdoe_token
from w3f.lib.contracts import kdoe_eth
from w3f.lib import doe_nft_data
from w3f.lib import kdoe_wealth
from w3f.lib import crypto_oracle
from opensea import OpenseaAPI

# ETH_PRICE = crypto_oracle.EthOracle()

from web3 import Web3

# def get_wealth(w3, w3_arb, wallet):
#     nft_cnt = get_nft_cnt(w3, wallet)
#     arb_doe = get_arbitrum_worth(w3_arb, wallet)
#     wallet_doe = float(doe_token_contract.get_main_balance(w3, wallet))
#     return [wallet_doe, arb_doe, nft_cnt]

def main():
    log.log_version()
    wallet = "0x7eD309643FB211e846a6D0A73Cd384e2e7A67B69"
    wallet = "0x5dA93cF2d5595Dd68Daed256DFbFF62c7ebBB298"

    # api = OpenseaAPI(apikey=hd.op_sea_key)
    # result = api.assets(asset_contract_address="0xd8cdb4b17a741dc7c6a57a650974cd2eba544ff7",
    # #                 token_ids=["1", "2"])
    # last_sales = doe_nft_data.get_last_sale_prices(range(9969, 9970))
    # last_sales = doe_nft_data.get_last_sale_price(9969)
    # log.log_json(last_sales)
    w3 = Web3(Web3.HTTPProvider(hd.eth_mainnet))
    # mainnet = kdoe_wealth.get_mainet_kdoe(w3, wallet)
    # print(f": {mainnet.total():{kdoe_wealth.kdoe_fmt()}}")
    # print(kdoe_wealth.get_doe_nfts(w3, wallet))
    # print(kdoe_wealth.get_kdoe_price_usd(w3, 1550))
    # nft_holdings_stats = kdoe_wealth.get_nft_holdings_stats(w3, wallet)
    # for nft in nft_holdings_stats:
    #     stats: doe_nft_data.PriceStats
    #     stats = nft_holdings_stats[nft]

    #     print(f"#{nft: >4}{stats.to_str()}")
    print("\n".join(kdoe_wealth.Wealth(w3, wallet).to_msg_chunks(500)))




# def get_nft_cnt(w3, wallet):
#     staked_nfts = doe_nft_staking_contract.get_tokens_of(w3, wallet)
#     wallet_nfts = doe_nft_contract.get_inventory(w3, wallet)
#     return len(staked_nfts) + len(wallet_nfts)

if __name__ == "__main__":
    main()



