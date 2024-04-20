import asyncio
import pytest

from w3f.lib.evm_event_monitor import EvmEventMonitor
from w3f.lib.web3 import InfuraEth
from w3f.lib.contracts import eth_usdt
import w3f.hidden_details as hd


@pytest.fixture(scope="module")
def contract():
    yield eth_usdt.Contract(InfuraEth(hd.infura_key))


@pytest.mark.asyncio
async def test___cancel___ok(contract):
    monitor = EvmEventMonitor(contract, "Swap")

    async def cancel(monitor: EvmEventMonitor):
        await monitor.cancel()

    run_task = asyncio.create_task(monitor.run())
    cancel_task = asyncio.create_task(cancel(monitor))
    await asyncio.gather(run_task, cancel_task)
    assert monitor._msg == "Closing gracefully"
