from web3 import Web3
import w3f.lib.contracts.staking.doe_nft_abi as doe_nft_abi

address = "0x5B586BFE6C283FB4020dDdbf1F0A08Fd99665819"

def get_tokens_of(w3, wallet):
    contract = w3.eth.contract(address=address, abi=doe_nft_abi.get_abi())
    return contract.functions.getTokensOf(wallet).call()

def get_data(w3, wallet):
    contract = w3.eth.contract(address=address, abi=doe_nft_abi.get_abi())
    totalSupply = contract.functions.totalSupply().call()
    userRewardPerTokenPaid = contract.functions.userRewards(wallet).call()[0]
    earned = Web3.from_wei(contract.functions.earned(wallet).call(), "ether")
    rewardPerToken = contract.functions.rewardPerToken().call()
    getTokensOf = contract.functions.getTokensOf(wallet).call()

    return {
        "rewardRate": 102341260021419944000000000000000000, # = 102341260021419944*1e18
        "totalSupply": totalSupply,
        "userRewardPerTokenPaid": userRewardPerTokenPaid,
        "earned": earned,
        "rewardPerToken": rewardPerToken,
        "getTokensOf": getTokensOf,
    }
