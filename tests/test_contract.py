import pytest
from w3f.lib.contracts import mongs_nft, doe_nft_contract
from w3f.lib.web3 import InfuraEth, W3
import w3f.hidden_details as hd

from . import TEST_DATA


@pytest.fixture(scope="module")
def web_3():
    w3 = InfuraEth(hd.infura_key)
    print(f"Connected to Web3: {w3.w3.is_connected()}")
    yield w3


def test__get_nfts(web_3: W3):
    assert len(mongs_nft.Contract(web_3).get_nfts("0x5dA93cF2d5595Dd68Daed256DFbFF62c7ebBB298")) > 0
    assert len(doe_nft_contract.Contract(web_3).get_nfts("0x5dA93cF2d5595Dd68Daed256DFbFF62c7ebBB298")) > 10
