import asyncio, json
from unicodedata import decimal
from web3 import Web3
from eth_abi import decode_single, decode_abi

class SwapData:
    class token:
        def __init__(self, ammount: decimal, id):
            self.ammount = ammount
            self.id = id

    def __init__(self, in_t: token, out_t: token, tx):
        self.in_t = in_t
        self.out_t = out_t
        self.tx = tx

async def subscribe_event(websocket, contract:str, event_signature:str, id=1):
    await websocket.send(json.dumps({"id": id, "method": "eth_subscribe", "params": ["logs", {
        "address": [contract],
        "topics": [Web3.keccak(text=event_signature).hex()]}]}))
    return await websocket.recv()

# in0, in1, out0, out1
async def subscribe_swap(webscoket, contract:str, id=1):
    return await subscribe_event(webscoket, contract, 
            'Swap(address,uint256,uint256,uint256,uint256,address)', id)

async def wait_swap(ws):
    try:
        json_response = json.loads(await asyncio.wait_for(ws.recv(), timeout=60))
    except asyncio.TimeoutError:
        return None

    decoded = decode_single('(uint256,uint256,uint256,uint256)',
        bytearray.fromhex(json_response['params']['result']['data'][2:]))

    # decoded: {in0, in1, out0, out1}
    if decoded[0] == 0:
        return SwapData(
            SwapData.token(decoded[1], 1), 
            SwapData.token(decoded[2], 0),
            json_response['params']['result']['transactionHash'])
    
    return SwapData(
        SwapData.token(decoded[0], 0), 
        SwapData.token(decoded[3], 1),
        json_response['params']['result']['transactionHash'])
