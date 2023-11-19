import pytest, json
from w3f.lib.kdoe_wealth import Wealth
import w3f.lib.web3 as web3
import w3f.hidden_details as hd
from web3 import Web3
from w3f.lib import doe_nft_data, mong_metadata

from . import TEST_DATA


@pytest.fixture(scope="module")
def web_3():
    w3 = web3.InfuraEth(hd.infura_key).w3
    print(f"Connected to Web3: {w3.is_connected()}")
    yield w3

@pytest.fixture(scope="module")
def web_3_bsc():
    w3 = web3.GetBlockBsc(hd.GETBLOCK_KEY).w3
    print(f"Connected to Web3: {w3.is_connected()}")
    yield w3

def test__wealth(web_3: Web3, web_3_bsc: Web3):
    wallet = hd.user_wallet
    wealth = Wealth(web_3, web_3_bsc, wallet,
                    doe_nft_data.Metadata(), mong_metadata.MongMetadata())

    print(wealth.to_str())
