import requests, asyncio
from w3f.lib import logger as log
from w3f.lib import doe_nft_data

class OracaleBase:
    def __init__(self) -> None:
        self.latest: float = None

    def get(self) -> float:
        return self.latest

    def _fetch(self):
        raise NotImplementedError("Must override")

    async def _loop(self, interval_in_s):
        while True:
            try:
                self._fetch()
            except Exception as e:
                log.log(e)
            await asyncio.sleep(interval_in_s)

    def create_task(self, interval_in_s):
        return asyncio.create_task(self._loop(interval_in_s))

class EthOracle(OracaleBase):
    def __init__(self) -> None:
        super().__init__()
        self.latest: float
        self.nft_stats = None
        self.ll_bin = log.LogLatch(2)
        self.ll_cba = log.LogLatch(2)

    def _fetch(self):
        # Fetch price from 2 sources
        binance = 'https://api.binance.com/api/v3/ticker/price?symbol=ETHUSDT'
        # messari = 'https://data.messari.io/api/v1/assets/eth/metrics/market-data'
        # coingecko = 'https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd'
        coinbase = 'https://api.coinbase.com/v2/prices/ETH-USD/spot' # 10k req/h

        binance_price = 0.0
        # messari_price = 0.0
        coinbase_price = 0.0

        try:
            raw = requests.get(binance).json()
            binance_price = float(raw['price'])
            self.ll_bin.reset()
        except Exception as e:
            self.ll_bin.log(f'Binance API failed: {e}: {raw}')
        try:
            raw = requests.get(coinbase).json()
            coinbase_price = float(raw['data']['amount'])
            self.ll_cba.reset()
        except Exception as e:
            self.ll_cba.log(f'Coinbase API failed: {e}: {raw}')
        # try:
        #     messari_price = float(requests.get(messari).json()['data']['market_data']['price_usd'])
        # except:
        #     pass

        # First pass, just check they do not differ too much
        if self.latest is None:
            if abs(binance_price - coinbase_price) / binance_price  < 0.02:
                self.latest = (binance_price + coinbase_price) / 2
                log.log(f'{type(self).__name__} OK: {self.latest:,.2f} usd')

        # Check they are not impossible changes in value
        else:
            price_list = []
            if abs(binance_price - self.latest) / self.latest  < 0.2:
                price_list.append(binance_price)
            if abs(coinbase_price - self.latest) / self.latest  < 0.2:
                price_list.append(coinbase_price)
            self.latest = sum(price_list) / len(price_list)

    def create_task(self, interval_in_s = 30):
        return super().create_task(interval_in_s)

class BnbOracle(OracaleBase):
    def __init__(self) -> None:
        super().__init__()
        self.latest: float
        self.nft_stats = None
        self.ll_bin = log.LogLatch(2)
        self.ll_cba = log.LogLatch(2)

    def _fetch(self):
        # Fetch price from 2 sources
        binance = 'https://api.binance.com/api/v3/ticker/price?symbol=BNBUSDT'
        # messari = 'https://data.messari.io/api/v1/assets/eth/metrics/market-data'
        coingecko = 'https://api.coingecko.com/api/v3/simple/price?ids=binancecoin&vs_currencies=usd'
        # coinbase = 'https://api.coinbase.com/v2/prices/ETH-USD/spot' # 10k req/h

        binance_price = 0.0
        # messari_price = 0.0
        coingecko_price = 0.0

        try:
            raw = requests.get(binance).json()
            binance_price = float(raw['price'])
            self.ll_bin.reset()
        except Exception as e:
            self.ll_bin.log(f'Binance API failed: {e}: {raw}')
        try:
            # {"binancecoin":{"usd":340.9}}
            raw = requests.get(coingecko).json()
            coingecko_price = float(raw['binancecoin']['usd'])
            self.ll_cba.reset()
        except Exception as e:
            self.ll_cba.log(f'Coinbase API failed: {e}: {raw}')
        # try:
        #     messari_price = float(requests.get(messari).json()['data']['market_data']['price_usd'])
        # except:
        #     pass

        # First pass, just check they do not differ too much
        if self.latest is None:
            if abs(binance_price - coingecko_price) / binance_price  < 0.02:
                self.latest = (binance_price + coingecko_price) / 2
                type(self).__name__
                log.log(f'{type(self).__name__} OK: {self.latest:,.2f} usd')

        # Check they are not impossible changes in value
        else:
            price_list = []
            if abs(binance_price - self.latest) / self.latest  < 0.2:
                price_list.append(binance_price)
            if abs(coingecko_price - self.latest) / self.latest  < 0.2:
                price_list.append(coingecko_price)
            self.latest = sum(price_list) / len(price_list)

    def create_task(self, interval_in_s = 30):
        return super().create_task(interval_in_s)

class DoeNftOracle(OracaleBase):
    def __init__(self) -> None:
        super().__init__()
        self.latest: doe_nft_data.CollectionStats
        self.ll = log.LogLatch(2)

    def _fetch(self):
        try:
            nft_stats = doe_nft_data.get_collection_stats()
            if self.latest is None:
                log.log(nft_stats)
            self.latest = nft_stats
            self.ll.reset()
        except Exception as e:
            self.ll.log(f"NFT stats failed: {e}")

    def create_task(self, interval_in_s = 60):
        return super().create_task(interval_in_s)