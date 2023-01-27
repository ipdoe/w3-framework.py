import requests

EVENTS=['item_metadata_updated', 'item_listed', 'item_sold', 'item_transferred',
'item_received_offer', 'item_received_bid', 'item_cancelled']

def short_hex(hex: str, chars=8):
    return hex[0:chars]

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
        self.timestamp = self.payload['payload']['event_timestamp']
        self.sent_at = self.payload['sent_at']

    def announcement(self):
        return f'{self.title}'

    def base_describe(self):
        return f'{self.title}: ' \
            f'TS: {self.timestamp}, ' \
            f'sent_at: {self.sent_at}'

    def describe(self, rarity):
        return self.base_describe()

class ItemBase(EventBase):
    def __init__(self, _dict: dict, eth_price_usd: float) -> None:
        EventBase.__init__(self, _dict, eth_price_usd)
        self.maker = self.payload['payload']['maker']['address']
        self.os_link = self.payload['payload']['item']['permalink']
        self.nft_id = self.payload['payload']['item']['nft_id'].split('/')[-1]
        self.token = PaymentToken(self.payload['payload']['payment_token'])
        self.value = 0
        self.value_type = 'Price'


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
        return self.os_md_link(f'From: {get_os_username(self.maker)}')

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
    def __init__(self, _dict: dict, eth_price_usd: float) -> None:
        ItemBase.__init__(self, _dict, eth_price_usd)
        self.title = 'Listing'
        self.value = int(self.payload['payload']['base_price'])

    def announcement(self):
        return f'📰📰 {self.title} {self.nft_id} 📰📰'

class ItemReceivedOffer(ItemListed):
    def __init__(self, _dict: dict, eth_price_usd: float) -> None:
        ItemListed.__init__(self, _dict, eth_price_usd)
        self.title = 'New Offer'
        self.value_type = 'Offer'

class ItemReceivedBid(ItemListed):
    def __init__(self, _dict: dict, eth_price_usd: float) -> None:
        ItemListed.__init__(self, _dict, eth_price_usd)
        self.title = 'New Bid'
        self.value_type = 'Bid'

    def announcement(self):
        return f'🔨🔨 {self.title} {self.nft_id} 🔨🔨'

class ItemSold(ItemBase):
    def __init__(self, _dict: dict, eth_price_usd: float) -> None:
        ItemBase.__init__(self, _dict, eth_price_usd)
        self.title = 'Sale'
        self.value = int(self.payload['payload']['sale_price'])
        self.taker = self.payload['payload']['taker']['address']
        self.transaction = self.payload['payload']['transaction']['hash']

    def announcement(self):
        return f'🔥🔥🔥 {self.title} {self.nft_id} 🔥🔥🔥'

    def tx_url(self):
        return f'[{short_hex(self.transaction)}](https://etherscan.io/tx/{self.transaction})'

    def taker_md_link(self):
        return self.os_md_link(f'To: {get_os_username(self.taker)}')

    def maker_taker(self):
        return f'{ItemBase.maker_taker(self)}\n{self.taker_md_link()}'

def create_event(event: dict, eth_price_usd: float):
    if event['event'] == 'item_listed':
        return ItemListed(event, eth_price_usd)
    elif event['event'] == 'item_sold':
        return ItemSold(event, eth_price_usd)
    elif event['event'] ==  'item_received_offer':
        return ItemReceivedOffer(event, eth_price_usd)
    elif event['event'] ==  'item_received_bid':
        return ItemReceivedBid(event, eth_price_usd)
    else:
        return EventBase(event, eth_price_usd)

def get_os_username(addr: str):
    try:
        user_agent = {'User-agent': 'Mozilla/5.0'}
        account = requests.get(f'https://api.opensea.io/api/v1/user/{addr}',
            headers=user_agent).json()
        if account['username'] is None:
            return short_hex(account['account']['address'])
        return account['username']
    except:
        return short_hex(addr)
