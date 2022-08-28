import pytest, asyncio, requests

from w3f.lib import crypto_oracle as co
from w3f.lib import stop_watch as sw

def test_EthPrice_get():
    oracle = co.EthPrice()
    assert oracle.get() == 0.0
    oracle._EthPrice__fetch()
    assert oracle.get() != 0.0


@pytest.mark.asyncio
async def test_EthPrice_my_loop():
    oracle = co.EthPrice()
    task = oracle.create_task(0.25)
    await asyncio.sleep(1)
    task.cancel()
    
    
