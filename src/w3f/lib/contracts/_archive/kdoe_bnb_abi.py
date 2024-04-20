import json, pathlib
from w3f import ROOT_PATH

NAME = "kdoe_bsc-bnb"
ADDRESS = "0x3537C4532ebf720fF130ae6A5a92dC39DE31a4D8"

def get_abi():
    # basename = pathlib.PurePath(__file__).name
    # abi_path = (ROOT_PATH / "lib/contracts" / basename).with_suffix(".abi")
    # with open(abi_path, 'r') as f:
    #     return json.load(f)
    basename = pathlib.PurePath(__file__).name
    abi_path = (ROOT_PATH / "lib/contracts" / basename).with_suffix(".abi")
    with open(abi_path, 'r') as f:
        return json.load(f)
