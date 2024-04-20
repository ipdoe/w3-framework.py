
import requests
from pathlib import Path

from w3f.lib import network
from w3f.lib import json

__EP = "?module=contract&action=getabi&address="


def fetch_abi(chain: network.ChainId, contract: str, api_key=""):
    ep = network.EXPLORER[chain].api + __EP + contract
    if api_key:
        ep = ep + "&apikey=" + api_key
    print(ep)
    return json.loads(requests.get(ep).json()['result'])


def dump_abi(chain: network.ChainId, contract: str, out_path: Path):
    json.dump(out_path, fetch_abi(chain, contract), sort_keys=True)
