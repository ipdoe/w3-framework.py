import requests, pathlib
from datetime import datetime, timedelta, timezone
from w3f.lib.opensea import OpenseaApi
from w3f.lib.util import to_json_str, dump_json

EVENTS=['item_metadata_updated', 'item_listed', 'item_sold', 'item_transferred',
'item_received_offer', 'item_received_bid', 'item_cancelled']

def short_hex(hex: str, chars=8):
    return hex[0:chars]

class Timestamp(datetime):
    def __new__(cls, year, month=None, day=None, hour=0, minute=0, second=0, microsecond=0, tzinfo=None):
        return super().__new__(cls, year, month, day, hour, minute, second, microsecond, tzinfo)

    def make(date_time):
        dt: datetime
        if isinstance(date_time, str):
            dt = datetime.strptime(date_time, "%Y-%m-%dT%H:%M:%S.%f%z")
        else:
            dt = date_time

        return Timestamp(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, dt.microsecond, dt.tzinfo)

    def older_than(self, time_delta = timedelta(hours=1)):
        return (self + time_delta) < datetime.now(timezone.utc)

class PaymentToken:
    def __init__(self, json_d: dict) -> None:
        self.dict = json_d
        self.address = self.dict['address']
        self.decimals = self.dict['decimals']
        self.eth_price = float(self.dict['eth_price'])
        self.name = self.dict['name']
        self.symbol = self.dict['symbol']
        self.usd_price = self.dict['usd_price']

    def from_wei(self, ammount):
        return ammount / (10 ** self.decimals)

    def to_string(self, ammount):
        return f'{self.from_wei(ammount)} {self.symbol}'

class EventBase:
    def __init__(self, _dict: dict, eth_price_usd: float) -> None:
        self._dict = _dict
        self.eth_price_usd = eth_price_usd
        self.event_type = self._dict['event']
        self.title = self.event_type
        self.payload = self._dict['payload']
        self.timestamp = Timestamp.make(self.payload['payload']['event_timestamp'])
        self.sent_at = Timestamp.make(self.payload['sent_at'])
        self.collection = self.payload['payload']['collection']['slug']

    def announcement(self):
        return f'{self.title}'

    def base_describe(self):
        return f'[{self.collection}] {self.title}: ' \
            f'TS: {self.timestamp}, ' \
            f'sent_at: {self.sent_at}'

    def describe(self, rarity):
        return self.base_describe()

    def __str__(self) -> str:
        return to_json_str(self._dict)

    def dump_json(self, path: pathlib.Path, indent=2):
        dump_json(path, self._dict, indent=indent)

class ItemBase(EventBase):
    def __init__(self, _dict: dict, eth_price_usd: float, os_api_key: str) -> None:
        EventBase.__init__(self, _dict, eth_price_usd)
        self.maker = self.payload['payload']['maker']['address']
        self.os_link = self.payload['payload']['item']['permalink']
        self.nft_id = self.payload['payload']['item']['nft_id'].split('/')[-1]
        self.image_url = self.payload['payload']['item']['metadata']['image_url']
        self.token = PaymentToken(self.payload['payload']['payment_token'])
        self.value = 0
        self.value_type = 'Price'
        self.os_api_key = OpenseaApi(os_api_key)


    def eth_value(self) -> float:
        return float(self.token.from_wei(self.value))

    def usd_value(self) -> float:
        return self.eth_value() * self.eth_price_usd

    def value_str(self):
        ret = f'{self.token.to_string(self.value)}'
        if self.token.symbol == 'ETH' or self.token.symbol == 'WETH':
            return f'{ret} (${self.usd_value():,.2f})'
        return ret

    def os_md_link(self, text: str):
        return f'[{text}]({self.os_link})'

    def maker_taker(self):
        return self.os_md_link(f'From: {self.os_api_key.get_username(self.maker)}')

    def announcement(self):
        return f'{self.title} {self.nft_id}'

    def img_url(self):
        # return f'https://explorer.dogsofelon.io/static/images/nft/{self.nft_id}.png'
        api = "a28d5dc2279a0f535adcae2aad0c3bdb"
        return f"https://api.dogsofelon.io/ipfs/{api}/images/{self.nft_id}.png"

    def describe(self, rarity):
        return f'{self.announcement()}\n' \
            f'Rank: {rarity}\n' \
            f'{self.value_type}: {self.value_str()}\n' \
            f'{self.maker_taker()}'

class ItemListed(ItemBase):
    def __init__(self, _dict: dict, eth_price_usd: float, os_api_key: str) -> None:
        ItemBase.__init__(self, _dict, eth_price_usd, os_api_key)
        self.title = 'Listing'
        self.value = int(self.payload['payload']['base_price'])

    def announcement(self):
        return f'📰📰 {self.title} {self.nft_id} 📰📰'

class ItemReceivedOffer(ItemListed):
    def __init__(self, _dict: dict, eth_price_usd: float, os_api_key: str) -> None:
        ItemListed.__init__(self, _dict, eth_price_usd, os_api_key)
        self.title = 'New Offer'
        self.value_type = 'Offer'

class ItemReceivedBid(ItemListed):
    def __init__(self, _dict: dict, eth_price_usd: float, os_api_key: str) -> None:
        ItemListed.__init__(self, _dict, eth_price_usd, os_api_key)
        self.title = 'New Bid'
        self.value_type = 'Bid'

    def announcement(self):
        return f'🔨🔨 {self.title} {self.nft_id} 🔨🔨'

class ItemSold(ItemBase):
    def __init__(self, _dict: dict, eth_price_usd: float, os_api_key: str) -> None:
        ItemBase.__init__(self, _dict, eth_price_usd, os_api_key)
        self.title = 'Sale'
        self.value = int(self.payload['payload']['sale_price'])
        self.taker = self.payload['payload']['taker']['address']
        self.transaction = self.payload['payload']['transaction']['hash']

    def announcement(self):
        return f'🔥🔥🔥 {self.title} {self.nft_id} 🔥🔥🔥'

    def tx_url(self):
        return f'[{short_hex(self.transaction)}](https://etherscan.io/tx/{self.transaction})'

    def taker_md_link(self):
        return self.os_md_link(f'To: {self.os_api_key.get_username(self.taker)}')

    def maker_taker(self):
        return f'{ItemBase.maker_taker(self)}\n{self.taker_md_link()}'

def create_event(event: dict, eth_price_usd: float, os_api_key: str):
    if event['event'] == 'item_listed':
        return ItemListed(event, eth_price_usd, os_api_key)
    elif event['event'] == 'item_sold':
        return ItemSold(event, eth_price_usd, os_api_key)
    elif event['event'] ==  'item_received_offer':
        return ItemReceivedOffer(event, eth_price_usd, os_api_key)
    elif event['event'] ==  'item_received_bid':
        return ItemReceivedBid(event, eth_price_usd, os_api_key)
    else:
        return EventBase(event, eth_price_usd)
