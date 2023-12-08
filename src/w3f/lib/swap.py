
import decimal
from web3 import Web3
from w3f.lib import eth_event_socket

class SwapToken:
    def __init__(self, tracker, unit, decimals) -> None:
        self.tracker = tracker
        self.unit = unit
        self.decimals = decimals
        self.ammount = 0.0

    def set_ammount(self, amount: int):
        self.ammount = float(Web3.from_wei(amount, self.unit))
        return self

    def to_string(self):
        return f'{self.ammount:,.{self.decimals}f} {self.tracker}'


class Swap:
    def __init__(self, abi, name, address, tokens: list[SwapToken],
                 buy_idx, chain = eth_event_socket.Chain.ETH, buy_char='🟢') -> None:
        self.abi = abi
        self.name = name
        self.address = address
        self.chain = chain

        self._buy_idx = buy_idx
        self._buy_token: SwapToken = tokens[self._buy_idx]
        self._sell_token: SwapToken = tokens[1 - self._buy_idx]
        self._buy_char = buy_char
        self._sell_char = '🔴'

    @staticmethod
    def _green_red(char, usd_val, divisor):
        return char * max(1, min(int(usd_val) // divisor, 1000))
        # return char * max(1, len(str(int(usd_val))))

    def is_buy(self, swap_data: eth_event_socket.SwapData):
        return swap_data.ammounts.out_idx == self._buy_idx

    def buy_sell_msg(self, swap_data: eth_event_socket.SwapData, oracle_usd_price, divisor = 100):
        # SELL
        in_token = self._buy_token.set_ammount(swap_data.ammounts.in_a)
        out_token = self._sell_token.set_ammount(swap_data.ammounts.out_a)
        swap_char = self._sell_char

        # buy
        if self.is_buy(swap_data):
            out_token = self._buy_token.set_ammount(swap_data.ammounts.out_a)
            in_token = self._sell_token.set_ammount(swap_data.ammounts.in_a)
            swap_char = self._buy_char

        usd_val = self._sell_token.ammount * oracle_usd_price
        token_price_usd = usd_val / self._buy_token.ammount
        usd_msg = f" (${usd_val:,.2f})" if usd_val > 0.0 else ""
        price_msg = f"Price: ${token_price_usd:f}\n" if token_price_usd > 0.0 else ""

        return f"{Swap._green_red(swap_char, usd_val, divisor)}\n" \
               f"In: {in_token.to_string()}{usd_msg}\n" \
               f"Out: {out_token.to_string()}\n" \
               f"{price_msg}" \
               f"addr: {swap_data.addr_link},  Tx: {swap_data.tx_link}"
