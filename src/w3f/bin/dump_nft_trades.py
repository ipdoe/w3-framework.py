from w3f.lib.contracts import doe_nft_contract
from w3f.lib.contracts.opensea import seaport_1p5
from w3f.lib.web3 import  j_dump_file, j_dumps
import w3f.lib.web3 as web3
from w3f import ROOT_PATH
from w3f.lib.util import load_json
from web3.types import FilterParams

import w3f.hidden_details as hd



class MyDict(dict):
    pass
    # def __init__(self, *args, **kwargs):
    #     dict.__init__(self, *args, **kwargs)

d = seaport_1p5.OrderFulfilledEvent({
    "args": {
      "offerer": "0x60F18213040F38645156Fb99A5C23F81C7f295e1",
      "zone": "0x004C00500000aD104D7DBd00e3ae0A5C00560C00",
      "orderHash": "0x56b6db9a14ed704f5988d540abc3db3ec8b69dd3366cb7e8e45e7b9418d21365",
      "recipient": "0x962D363E9e89c6a26A64f7aC7421aDB65FdD6F7a",
      "offer": [
        {
          "itemType": 2,
          "token": "0xD8CDB4b17a741DC7c6A57A650974CD2Eba544Ff7",
          "identifier": 6014,
          "amount": 1
        }
      ],
      "consideration": [
        {
          "itemType": 0,
          "amount": 19900000000000000,
          "recipient": "0x60F18213040F38645156Fb99A5C23F81C7f295e1"
        },
        {
          "itemType": 0,
          "token": "0x0000000000000000000000000000000000000000",
          "identifier": 0,
          "amount": 100000000000000,
          "recipient": "0x8ce63245151C2cC5dd2827d550182aB52D2851BD"
        }
      ]
    },
    "event": "OrderFulfilled",
    "logIndex": 183,
    "transactionIndex": 77,
    "transactionHash": "0x4a3eb8bf3fefeecadb5b809b45188dac95027b37b1834b74418b783a13acca75",
    "address": "0x00000000000000ADc04C56Bf30aC9d3c0aAF14dC",
    "blockHash": "0xda60a852ebe9d17f5006bc961c71029a6a0163fdc28a6ef979a0c494272b4f8c",
    "blockNumber": 17553138
  })



w3 = web3.InfuraEth(hd.infura_key).w3
print(f"Connected to Web3: {w3.is_connected()}")



# Contracts
DOE_NFT = doe_nft_contract.DoeNtf(w3)
SEAPORT = seaport_1p5.Seaport(w3)
peculiar_trade = "0x239922f99296ca61fc40f7de2457a93c9ff7129221fa79416c1a040a109456eb"
receipt = w3.eth.get_transaction_receipt(peculiar_trade)
logs = SEAPORT.contract.events.OrderFulfilled().process_receipt(receipt)
print(j_dump_file(ROOT_PATH / "dat/peculiar_trade.json", logs, indent=2))

exit(0)

# Filters
block = 17553138
seaport_logs = SEAPORT.filter_order_fulfilled(doe_nft_contract.ADDRESS, FilterParams(fromBlock=block, toBlock=block))
print(f"Seaport size: {len(seaport_logs)}")
print(j_dumps(seaport_logs))

# seaport_logs = w3.eth.filter({
#     "fromBlock": block,
#     "toBlock": block,
#     "address": [seaport_1p5.ADDRESS],
#     "topics": [SEAPORT.get_event_signature("OrderFulfilled")]}).get_all_entries()

# doe_logs = DOE_NFT.contract.events.Transfer.create_filter(
#     fromBlock=block,
#     toBlock=block
#     # , topics=[DOE_NFT.get_event_signature("Transfer")]
#     ).get_all_entries()

# doe_logs = DOE_NFT.contract.events["Transfer"].create_filter(
#     fromBlock=block,
#     toBlock=block
#     # , topics=[DOE_NFT.get_event_signature("Transfer")]
#     ).get_all_entries()



# doe_logs = w3.eth.filter({
#     "fromBlock": block,
#     "toBlock": block,
#     "address": [doe_nft_contract.ADDRESS],
#     "topics": [DOE_NFT.get_event_signature("Transfer")]}).get_all_entries()

# Results
# TX 0x4a3eb8bf3fefeecadb5b809b45188dac95027b37b1834b74418b783a13acca75
# is present in both logs, therefore is a DOE NFT sale

# print(f"DoE size: {len(doe_logs)}")
# j_dump_file(ROOT_PATH / "dat/tmp/seaport_logs_dump.json", seaport_logs)
# j_dump_file(ROOT_PATH / "dat/tmp/doe_logs_dump.json", doe_logs)

# filtered_list = [
#     d for d in seaport_logs
#     if d["args"]["offer"][0]["token"] == "0xD8CDB4b17a741DC7c6A57A650974CD2Eba544Ff7"
# ]

# def to_hash_dict(logs):
#     dict = {}
#     for item in logs: dict.setdefault(item["transactionHash"], []).append(item)
#     return dict

# def intersect(transfers_dict, orders, instersection):
#     for item in orders:
#         tx_hash = item["transactionHash"]
#         if tx_hash in transfers_dict:
#             intersection.setdefault(tx_hash, []).append(item)

# seaport_logs = load_json(ROOT_PATH / "dat/tmp/seaport_logs_dump.json")
# doe_logs = load_json(ROOT_PATH / "dat/tmp/doe_logs_dump.json")

# intersection = {}
# transfers_dict = to_hash_dict(doe_logs)
# print(j_dumps(transfers_dict))
# intersect(transfers_dict, seaport_logs, intersection)

# print(j_dumps(intersection))
