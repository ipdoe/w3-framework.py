from w3f.lib.contracts import fetch_abi
from w3f.lib.network import ChainId
from w3f.lib import json

from w3f import ROOT_PATH

CONTRACT_ABI = ROOT_PATH / "lib/contracts/abi"


def __main__():
    # contract = "0xB4e16d0168e52d35CaCD2c6185b44281Ec28C9Dc"
    # j_abi = fetch_abi.fetch_abi(ChainId.ETH, contract)
    # json.pprint(j_abi)
    # json.dump_compact(j_abi, CONTRACT_ABI / "uni_v2.json")

    # contract = "0x3537C4532ebf720fF130ae6A5a92dC39DE31a4D8"
    # j_abi = fetch_abi.fetch_abi(ChainId.BSC, contract)
    # json.pprint(j_abi)
    # json.dump_compact(j_abi, CONTRACT_ABI / "cake_lp.json")

    # contract = "0xc4c4e2Dd743CCBBC7A8e20a7073Be281b2924519"
    # j_abi = fetch_abi.fetch_abi(ChainId.ETH, contract)
    # json.pprint(j_abi)
    # json.dump_compact(j_abi, CONTRACT_ABI / "juice.json")

    # contract = "0xcbcdf9626bc03e24f779434178a73a0b4bad62ed"
    # j_abi = fetch_abi.fetch_abi(ChainId.ETH, contract)
    # json.pprint(j_abi)
    # json.dump_compact(j_abi, CONTRACT_ABI / "uni_v3.json")


    contract = "0x1B69F4a3aF36bA841551Ae20b9eDf5e52827bea5"
    j_abi = fetch_abi.fetch_abi(ChainId.BASE, contract)
    json.pprint(j_abi)
    json.dump_compact(j_abi, CONTRACT_ABI / "uni_v3-2.json")

if __name__ == '__main__':
    __main__()
