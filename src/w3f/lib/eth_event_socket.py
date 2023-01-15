import asyncio, json
from unicodedata import decimal
from web3 import Web3
from eth_abi import decode_single, decode_abi
from w3f.lib import logger
from ens import ENS

class SwapData:
    class token:
        def __init__(self, ammount: decimal, id):
            self.ammount = ammount
            self.id = id

    def __init__(self, in_t: token, out_t: token, addr: str, tx):
        self.in_t = in_t
        self.out_t = out_t
        self.addr = addr
        self.addr_link = f"[{self.addr[:8]}](https://etherscan.io/address/{self.addr})"
        self.tx = tx
        self.tx_link = f"[{self.tx[:8]}](https://etherscan.io/tx/{self.tx})"

async def subscribe_event(websocket, contract:str, event_signature:str, id=1):
    await websocket.send(json.dumps({"id": id, "method": "eth_subscribe", "params": ["logs", {
        "address": [contract],
        "topics": [Web3.keccak(text=event_signature).hex()]}]}))
    return await websocket.recv()

# in0, in1, out0, out1
async def subscribe_swap(webscoket, contract:str, id=1):
    return await subscribe_event(webscoket, contract, 
            'Swap(address,uint256,uint256,uint256,uint256,address)', id)

async def wait_swap(ns: ENS, ws):
    try:
        # json_response = json.loads(await asyncio.wait_for(ws.recv(), timeout=60))
        json_response = json.loads(await ws.recv())
        addr = Web3.toChecksumAddress(hex(int(json_response['params']['result']['topics'][2], 16)))
        # logger.log(ns.name(addr))
        
    except asyncio.TimeoutError:
        return None

    decoded = decode_single('(uint256,uint256,uint256,uint256)',
        bytearray.fromhex(json_response['params']['result']['data'][2:]))

    # decoded: {in0, in1, out0, out1}
    if decoded[0] == 0:
        return SwapData(
            SwapData.token(decoded[1], 1), 
            SwapData.token(decoded[2], 0),
            addr,
            json_response['params']['result']['transactionHash'])
    
    return SwapData(
        SwapData.token(decoded[0], 0), 
        SwapData.token(decoded[3], 1),
        addr,
        json_response['params']['result']['transactionHash'])
