import asyncio, json
from decimal import Decimal

from web3 import Web3
from eth_abi.abi import decode
from w3f.lib import logger
from ens import ENS
from enum import Enum

class Chain(Enum):
    ETH = 0
    BSC = 1

EXPLORER = {
    Chain.ETH: "https://etherscan.io/{}",
    Chain.BSC: "https://bscscan.com/{}"
}

async def subscribe_event(websocket, contract:str, event_signature:str, id=1):
    await websocket.send(json.dumps({"id": id, "method": "eth_subscribe", "params": ["logs", {
        "address": [contract],
        "topics": [Web3.keccak(text=event_signature).hex()]}]}))
    return await websocket.recv()

class SwapData:
    SIGNATURE = 'Swap(address,uint256,uint256,uint256,uint256,address)'
    #                       in0,      in1,      out0,       out1
    IN0_IN1_OUT0_OUT1 = ('uint256', 'uint256', 'uint256', 'uint256')

    class token:
        def __init__(self, ammount: Decimal, idx):
            self.ammount = ammount
            self.idx = idx # TODO: remove this index and use only an in_idx because
            # the out is always the inverse

        def __str__(self) -> str:
            return f"[{self.idx}]: {self.ammount}"

        def __repr__(self):
            return str(self)

    class Ammounts:
        def __init__(self, out_idx: int, in_ammount: Decimal, out_ammount: Decimal):
            self.out_idx = out_idx
            self.in_a = in_ammount
            self.out_a = out_ammount

    def __init__(self, event_response: dict, chain = Chain.ETH):
        self.chain = chain
        self.data = event_response['data']
        self.ammounts = self._decode_to_in_out_tokens(self.data)
        self.addr = Web3.to_checksum_address(hex(int(event_response['topics'][2], 16)))
        self.addr_link = f"[{self.addr[:8]}]({EXPLORER[self.chain].format(f'address/{self.addr}')})"
        self.tx = event_response['transactionHash']
        self.tx_link = f"[{self.tx[:8]}]({EXPLORER[self.chain].format(f'tx/{self.tx}')})"
        # self.block = int(event_response['blockNumber'], 0)

    @staticmethod
    async def subscribe(webscoket, contract:str, id=1):
        return await subscribe_event(webscoket, contract, SwapData.SIGNATURE, id)

    @staticmethod
    async def wait(ws, chain = Chain.ETH):
        try:
            json_response = json.loads(await ws.recv())

        except asyncio.TimeoutError:
            return None

        return SwapData(json_response['params']['result'], chain)

    @staticmethod
    def _decode_to_in_out_tokens(jrpc_data: str):
        in0_in1_out0_out1 = decode(SwapData.IN0_IN1_OUT0_OUT1, bytearray.fromhex(jrpc_data[2:]))
        if in0_in1_out0_out1[0] == 0:
            return SwapData.Ammounts(0, in0_in1_out0_out1[1], in0_in1_out0_out1[2])

        return SwapData.Ammounts(1, in0_in1_out0_out1[0], in0_in1_out0_out1[3])
