from dataclasses import dataclass
from enum import Enum

class ChainId(Enum):
    ETH  = 0
    OP   = 10
    BSC  = 56
    POLY = 134
    BASE = 8453
    ARB  = 42161


@dataclass
class Explorer:
    explorer: str
    api: str

    def tx(self, tx: str):
        return self.explorer + "/tx/" + tx

    def address(self, address: str):
        return self.explorer + "/address/" + address


EXPLORER = {
    ChainId.ETH:  Explorer("https://etherscan.io", "https://api.etherscan.io/api"),
    ChainId.OP:   Explorer("https://optimistic.etherscan.io", "https://api-optimistic.etherscan.io/api"),
    ChainId.BSC:  Explorer("https://bscscan.com", "https://api.bscscan.com/api"),
    ChainId.POLY: Explorer("https://polygonscan.com", "https://api.polygonscan.com/api"),
    ChainId.BASE: Explorer("https://basescan.org", "https://api.basescan.org/api"),
    ChainId.ARB:  Explorer("https://arbiscan.io", "https://api.arbiscan.io/api"),
}


class NodeProvider:
    def __init__(self, chainId: ChainId, http: str, ws: str) -> None:
        self._chain = chainId
        self._http_url = "https://" + http
        self._ws_url = "wss://" + ws

    def http(self, key: str):
        return self._http_url.format(key)

    def ws(self, key: str):
        return self._ws_url.format(key)

    def chain(self):
        return self._chain


PROVIDER = {
    "infura-eth": NodeProvider(ChainId.ETH, "mainnet.infura.io/v3/{}", "mainnet.infura.io/ws/v3/{}"),
    "infura-arb": NodeProvider(ChainId.ARB, "arbitrum-mainnet.infura.io/v3/{}", "arbitrum.mainnet.infura.io/ws/v3/{}"),
    "alchemy-eth": NodeProvider(ChainId.ETH, "eth-mainnet.g.alchemy.com/v2/{}", "eth-mainnet.g.alchemy.com/v2/{}"),
    "alchemy-base": NodeProvider(ChainId.BASE, "base-mainnet.g.alchemy.com/v2/{}", "base-mainnet.g.alchemy.com/v2/{}"),
    "getblock-bsc": NodeProvider(ChainId.BSC, "bsc.getblock.io/{}/mainnet", "bsc.getblock.io/{}/mainnet"),
}
