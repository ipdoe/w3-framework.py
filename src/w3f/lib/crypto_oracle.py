import requests, asyncio, json
from w3f.lib import logger as log

class EthPrice:
    def __init__(self) -> None:
        self.latest = 0.0

    def __fetch(self):
        # Fetch price from 2 sources
        binance = 'https://api.binance.com/api/v3/ticker/price?symbol=ETHUSDC'
        # messari = 'https://data.messari.io/api/v1/assets/eth/metrics/market-data'
        # coingecko = 'https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd'
        coinbase = 'https://api.coinbase.com/v2/prices/ETH-USD/spot' # 10k req/h

        binance_price = 0.0
        # messari_price = 0.0
        coinbase_price = 0.0
        ll_bin = log.LogLatch(2)
        ll_cba = log.LogLatch(2)

        try:
            raw = requests.get(binance).json()
            binance_price = float(raw['price'])
            ll_bin.reset()
        except Exception as e:
            ll_bin.log(f'Binance API failed: {e}: {raw}')
        try:
            raw = requests.get(coinbase).json()
            coinbase_price = float(raw['data']['amount'])
            ll_cba.reset()
        except Exception as e:
            ll_cba.log(f'Coinbase API failed: {e}: {raw}')
        # try:
        #     messari_price = float(requests.get(messari).json()['data']['market_data']['price_usd'])
        # except:
        #     pass

        # First pass, just check they do not differ too much
        if self.latest == 0.0:
            if abs(binance_price - coinbase_price) / binance_price  < 0.02:
                self.latest = (binance_price + coinbase_price) / 2
                log.log(f'EthPrice OK: {self.latest:,.2f} usd')
        
        # Check they are not impossible changes in value
        else:
            price_list = []
            if abs(binance_price - self.latest) / self.latest  < 0.2:
                price_list.append(binance_price)
            if abs(coinbase_price - self.latest) / self.latest  < 0.2:
                price_list.append(coinbase_price)
            self.latest = sum(price_list) / len(price_list)

    def get(self):
        return self.latest

    async def my_loop(self, interval_in_s):
        while True:
            try:
                self.__fetch()
            except Exception as e:
                log.log(e)
            await asyncio.sleep(interval_in_s)
            
    def create_task(self, interval_in_s = 30):
        return asyncio.create_task(self.my_loop(interval_in_s))
