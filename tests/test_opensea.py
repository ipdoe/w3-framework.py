
from w3f.lib import opensea
import w3f.hidden_details as hd

def test__get_os_username():
    os = opensea.OpenseaApi(hd.op_sea_key_ipdoe)
    assert os.get_username("0x5dA93cF2d5595Dd68Daed256DFbFF62c7ebBB298") == "IPDOE"

