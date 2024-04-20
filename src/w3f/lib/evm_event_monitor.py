import asyncio
import json
import websockets
from typing import List

import w3f.lib.logger as log
from w3f.lib.web3 import Contract


class EvmEventMonitor:
    def __init__(self, contract: Contract, events: str | List[str] = "_all_") -> None:
        self._contract = contract
        self._events = []
        self._event_names = events
        if isinstance(events, str):
            if events != "_all_":
                self._events = [str(contract.get_event_signature(events))]
                self._event_names = [events]
            else:
                self._event_names = [e["name"] for e in contract.get_events_list()]
        else:
            for e in events:
                self._events.append(str(contract.get_event_signature(e)))
        self._ws = websockets.WebSocketClientProtocol()
        self._close = False
        self._msg = ""
        self._connected = asyncio.Event()
        self.q = asyncio.Queue(10000)

    async def cancel(self):
        self._close = True
        await self._connected.wait()
        await self._ws.close()

    async def _wait_event(self):
        log.log_json("waiting recv")
        log_data = json.loads(await self._ws.recv())['params']['result']
        return self._contract.decode_event(log_data)

    async def _subscribe(self, websocket, id=1):
        await websocket.send(json.dumps({"id": id, "method": "eth_subscribe", "params": ["logs", {
            "address": [str(self._contract.address)],
            "topics": self._events}]}))
        return await websocket.recv()

    def _get_missed_events(self, last_events):
        return
        for k, v in last_events:
            from_block = int(v['blockNumber'], 0)
            all_entries = self._contract.create_filter(v['event'], {"fromBlock": from_block, "toBlock": "latest"}).get_all_entries()

    async def run(self):
        log.log(f"Connected to Web3: {self._contract.w3.w3.is_connected()}")
        log.log(f"Contract: {self._contract.name}, events: {self._event_names}))")
        last_events = {}
        async for self._ws in websockets.connect(self._contract.w3.ws):
            self._connected.set()
            try:
                subscription = await self._subscribe(self._ws)
                msg = f'Socket subscription: {subscription}'
                log.log(msg)
                while True:
                    try:
                        self._get_missed_events(last_events)
                        decoded_event = await self._wait_event()
                        last_events[decoded_event['event']] = decoded_event
                        await self.q.put(decoded_event)
                    except Exception as e:
                        log.log(f'Exception: {e}')
                        raise

            except websockets.ConnectionClosed as cc:
                if self._close:
                    self._msg = "Closing gracefully"
                    break
                self._msg = f'External ConnectionClosed: {cc}'
                log.log(self._msg)
            except Exception as e:
                self._msg = f'Exception: {e}'
                log.log(self._msg)

        log.log(self._msg)

