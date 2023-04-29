import pytest, asyncio, requests

from w3f.lib import crypto_oracle as co
from w3f.lib import stop_watch as sw

def test_EthOracle_get():
    oracle = co.EthOracle()
    assert oracle.get() == None
    oracle._fetch()
    assert oracle.get() != 0.0

def test_BnbOracle_get():
    oracle = co.BnbOracle()
    assert oracle.get() == None
    oracle._fetch()
    assert oracle.get() != 0.0

@pytest.mark.asyncio
async def test_EthOracle_my_loop():
    oracle = co.EthOracle()
    task = oracle.create_task(0.25)
    await asyncio.sleep(1)
    task.cancel()

@pytest.mark.asyncio
async def test_BnbOracle_my_loop():
    oracle = co.BnbOracle()
    task = oracle.create_task(0.25)
    await asyncio.sleep(1)
    task.cancel()
