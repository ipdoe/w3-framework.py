from w3f.lib.contracts import doe_nft_contract
from w3f.lib.contracts.opensea import seaport_1p5
from w3f.lib.web3 import  j_dump_file
import w3f.lib.web3 as web3
from w3f import ROOT_PATH

import w3f.hidden_details as hd

w3 = web3.InfuraEth(hd.infura_key).w3
print(f"Connected to Web3: {w3.is_connected()}")

# Contracts
DOE_NFT = doe_nft_contract.DoeNtf(w3)
SEAPORT = seaport_1p5.Seaport(w3)

# Filters
block = 17553138
seaport_logs = w3.eth.filter({
    "fromBlock": block,
    "toBlock": block,
    "address": [seaport_1p5.ADDRESS],
    "topics": [SEAPORT.get_event_signature("OrderFulfilled")]}).get_all_entries()

doe_logs = w3.eth.filter({
    "fromBlock": block,
    "toBlock": block,
    "address": [doe_nft_contract.ADDRESS],
    "topics": [DOE_NFT.get_event_signature("Transfer")]}).get_all_entries()


# Results
# TX 0x4a3eb8bf3fefeecadb5b809b45188dac95027b37b1834b74418b783a13acca75
# is present in both logs, therefore is a DOE NFT sale
print(f"Seaport size: {len(seaport_logs)}")
print(f"DoE size: {len(doe_logs)}")
j_dump_file(ROOT_PATH / "dat/tmp/seaport_logs_dump.json", seaport_logs)
j_dump_file(ROOT_PATH / "dat/tmp/doe_logs_dump.json", doe_logs)
