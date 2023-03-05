from web3 import Web3
import w3f.lib.contracts.doe_nft_abi as doe_nft_abi

ADDRESS = "0xD8CDB4b17a741DC7c6A57A650974CD2Eba544Ff7"

def wallet_inventory(w3, wallet):
    contract = w3.eth.contract(address=ADDRESS, abi=doe_nft_abi.get_abi())
    return contract.functions.walletInventory(wallet).call()
