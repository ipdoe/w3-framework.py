from w3f.lib.contracts import mongs_nft
import w3f.lib.web3 as web3
import w3f.hidden_details as hd

w3 = web3.InfuraEth(hd.infura_key).w3
print(f"Connected to Web3: {w3.is_connected()}")

contract = mongs_nft.Contract(w3)
all_nfts = contract.get_nfts("0x5da93cf2d5595dd68daed256dfbff62c7ebbb298")
print(all_nfts)
