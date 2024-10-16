from web3 import Web3
import w3f.lib.contracts.staking.slp_eth_doe_abi as slp_eth_doe_abi

def get_data(w3, wallet):
    contract_address = "0xD2696e995A2EF33C9b4A3c47F6AA2651beb48B21"
    contract = w3.eth.contract(address=contract_address, abi=slp_eth_doe_abi.get_abi())
    balanceOf =  Web3.from_wei(contract.functions.balanceOf(wallet).call(), "ether")
    reserves = contract.functions.getReserves().call()
    totalSupply = Web3.from_wei(contract.functions.totalSupply().call(), "ether")

    return {
        "liquidity": balanceOf,
        "totalSupply" : totalSupply,
        "reserves": {
            "ETH" : Web3.from_wei(reserves[0], "ether"),
            "DOE" : Web3.from_wei(reserves[1], "ether"),
            "blockTs" : reserves[2],
        },
    }
