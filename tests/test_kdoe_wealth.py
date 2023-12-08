import pytest
from w3f.lib.kdoe_wealth import Wealth
import w3f.lib.web3 as web3
import w3f.hidden_details as hd
from w3f.lib import doe_nft_data, mong_metadata
from w3f.lib.web3 import W3

from . import TEST_DATA


@pytest.fixture(scope="module")
def web_3():
    w3 = web3.InfuraEth(hd.infura_key)
    print(f"Connected to Web3: {w3.w3.is_connected()}")
    yield w3


@pytest.fixture(scope="module")
def web_3_bsc():
    w3 = web3.GetBlockBsc(hd.GETBLOCK_KEY)
    print(f"Connected to Web3: {w3.w3.is_connected()}")
    yield w3


def test__wealth(web_3: W3, web_3_bsc: W3):
    wallet = hd.user_wallet
    wealth = Wealth(web_3, web_3_bsc, wallet,
                    doe_nft_data.Metadata(), mong_metadata.MongMetadata())

    print(wealth.to_str())
