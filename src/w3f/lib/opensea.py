import requests
from w3f.lib.util import short_hex

class OpenseaApi:
    def __init__(self, key: str) -> None:
        self.v2 = "https://api.opensea.io/api/v2"
        self.__key = key
        self.__header = {'User-agent': 'Mozilla/5.0', "X-API-KEY": self.__key}

    def account(self, addr: str):
        return requests.get(f'{self.v2}/accounts/{addr}', headers=self.__header).json()

    def get_username(self, addr):
        try:
            account = self.account(addr)
            if account['username'] is None:
                return short_hex(account['account']['address'])
            return account['username']
        except Exception as e:
            print(e)
            return short_hex(addr)
