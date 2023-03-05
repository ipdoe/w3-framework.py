import pytest, asyncio, requests

from w3f.lib import crypto_oracle as co
from w3f.lib import stop_watch as sw

def test_Oracle_get():
    oracle = co.EthOracle()
    assert oracle.get() == None
    oracle._fetch()
    assert oracle.get() != 0.0

@pytest.mark.asyncio
async def test_Oracle_my_loop():
    oracle = co.EthOracle()
    task = oracle.create_task(0.25)
    await asyncio.sleep(1)
    task.cancel()
